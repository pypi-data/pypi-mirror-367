from __future__ import annotations
import logging
import tomllib
import click
import dmarc.psl as psl

from contextvars import ContextVar
from socket import gethostname
from email.utils import getaddresses
from logging.handlers import SysLogHandler
from typing import BinaryIO
from purepythonmilter import (
    Accept,
    Continue,
    TempFailWithCode,
    RejectWithCode,
    CauseConnectionFail,
    InsertHeader,
    ChangeHeader,
    Quarantine,
    AddRecipient,
    VerdictOrContinue,
    Connect,
    Helo,
    MailFrom,
    Header,
    EndOfMessage,
    PurePythonMilter,
    DEFAULT_LISTENING_TCP_IP,
    DEFAULT_LISTENING_TCP_PORT,
)
from purepythonmilter.api.models import (
    ConnectionInfoArgs,
    ConnectionInfoArgsUnixSocket,
    ConnectionInfoArgsIPv4,
    ConnectionInfoArgsIPv6,
    ConnectionInfoUnknown,
)
from string import Template
from dmarc import __version__
from authres import (
    AuthenticationResultsHeader,
    AuthResError,
)
from dmarc.asyncresolver import resolver
from .networkparser import NetworkParser
from .utils import (
    unfold,
    split_address,
    check_spf,
    get_record,
    check_dmarc,
)

logger: logging.LoggerAdapter[logging.Logger]
ctx_client: ContextVar[ConnectionInfoArgs] = ContextVar('client')
ctx_helo: ContextVar[str] = ContextVar('helo')
ctx_mail_from: ContextVar[str] = ContextVar('mail_from')
ctx_headers: ContextVar[dict] = ContextVar('headers')
ctx_queue_id: ContextVar[str] = ContextVar('queue_id')
ctx_domain: ContextVar[str] = ContextVar('domain')
consume_headers = ('from', 'authentication-results')
mynet = NetworkParser('127.0.0.0/8 ::1/128')
myhostname = gethostname()
config = {
    'myauthserv_id': myhostname,
    'trusted_authserv_ids': [myhostname],
    'ignore_domains': [],
    'ignore_sasl_authenticated': False,
    'bind_host': DEFAULT_LISTENING_TCP_IP,
    'bind_port': DEFAULT_LISTENING_TCP_PORT,
    'log_level': 'INFO',
    'log_ar_header': True,
    'keep_ar_header': True,
    'add_ar_header': True,
    'spf_enabled': True,
    'policy': {
        'none': {'action': 'Accept'},
        'reject': {'action': 'Accept'},
        'quarantine': {'action': 'Accept'},
        'domainerror': {'action': 'Accept'},
        'dnserror': {'action': 'Accept'}
    }
}

def get_policy_response(action: str, text: str = 'DMARC error', manipulations: list = []) -> VerdictOrContinue:
    queue_id = ctx_queue_id.get()
    domain = ctx_domain.get()
    text = Template(text).safe_substitute(queue_id=queue_id, domain=domain)
    if action == 'Accept':
        response = Accept()
    elif action == 'TempFail':
        response = TempFailWithCode(
            primary_code=(4,5,0), enhanced_code=(4,7,1), text=text)
    elif action == 'Reject':
        response = RejectWithCode(
            primary_code=(5,5,0), enhanced_code=(5,7,1), text=text)
    else:
        logger.error(f"{queue_id}: unrecognized policy action: {action}")
        response = CauseConnectionFail()
        
    for manipulation in manipulations:
        logger.debug(f"{queue_id}: manipulation: {manipulation}")
        action = manipulation.get('action')
        if action == 'InsertHeader':
            field = manipulation.get('headername')
            text = manipulation.get('headertext') 
            logger.info(f"{queue_id}: insert header: {field}: {text}")
            response.manipulations.append(
                InsertHeader(index=1, headername=field, headertext=text)
            )
        elif action == 'Quarantine':
            reason = manipulation.get('reason')
            logger.info(f"{queue_id}: quarantine: {reason}")
            response.manipulations.append(
                Quarantine(reason=reason)
            )
        elif action == 'AddRecipient':
            recipient = manipulation.get('recipient')
            logger.info(f"{queue_id}: add recipient: {recipient}")
            response.manipulations.append(
                AddRecipient(recipient=recipient)
            )
        else:
            logger.error(f"{queue_id}: unrecognized manipulation action: {action}")
            response = CauseConnectionFail()
    
    return response

async def on_connect(cmd: Connect) -> VerdictOrContinue:
    logger.debug(f"connect: args={cmd.connection_info_args}, macros={cmd.macros}")
    client = cmd.connection_info_args
    ctx_client.set(client)
    if isinstance(client, ConnectionInfoArgsUnixSocket):
        logger.info(f"client accept: {client.path}")
        response = Accept()
    elif isinstance(client, (ConnectionInfoArgsIPv4, ConnectionInfoArgsIPv6)):
        if client.addr in mynet:
            logger.info(f"client accept: {client.addr}")
            response = Accept()
        else:
            response = Continue()
    elif isinstance(client, ConnectionInfoUnknown):
        logger.error(f"unknown client error: {client.description}")
        response = CauseConnectionFail()
    else:
        logger.error(f"undefined client error: {client!r}")
        response = CauseConnectionFail()
    return response

async def on_helo(cmd: Helo) -> None:
    logger.debug(f"helo: hostname={cmd.hostname}, macros={cmd.macros}")
    ctx_helo.set(cmd.hostname)

async def on_mail_from(cmd: MailFrom) -> VerdictOrContinue:
    logger.debug(
        f"mail from: address={cmd.address}, esmtp_args={cmd.esmtp_args}, "
        f"macros={cmd.macros}"
    )
    ctx_mail_from.set(cmd.address)
    ctx_headers.set({header: [] for header in consume_headers})
    sasl_login = cmd.macros.get('{auth_authen}')
    if sasl_login and config.get('ignore_sasl_authenticated'):
        logger.info(f"ignoring SASL authenticated: {sasl_login}")
        response = Accept()
    else:
        response = Continue()
    return response

async def on_header(cmd: Header) -> None:
    logger.debug(f"header: name={cmd.name} text={cmd.text!r}, macros={cmd.macros}")
    name = cmd.name.lower()
    text = cmd.text
    if name in consume_headers:
        logger.debug(f"accept header: name={name} text={text!r}")
        ctx_headers.get()[name].append(unfold(text))

async def on_end_of_message(cmd: EndOfMessage) -> VerdictOrContinue:
    logger.debug(f"end of message: macros={cmd.macros}")
    queue_id = cmd.macros.get('i')
    ctx_queue_id.set(queue_id)
    domain = None
    addresses = getaddresses(ctx_headers.get()['from'])
    if len(addresses) > 1:
        logger.error(f"{queue_id}: multiple author addresses found: {addresses}")
    else:
        for address in addresses:
            _, domain = split_address(address[1])
            domain = domain.strip()
    ctx_domain.set(domain)
    if not domain:
        logger.error(f"{queue_id}: no author domain found")
    elif domain in config.get('ignore_domains'):
        logger.info(f"{queue_id}: ignoring domain: {domain}")
        return Continue()
    else:
        logger.info(f"{queue_id}: author domain: {domain}")
    
    auth_results = []
    manipulations = []
    ar_headers = ctx_headers.get()['authentication-results']
    for idx in reversed(range(len(ar_headers))):
        value = ar_headers.pop(idx)
        try:
            header = AuthenticationResultsHeader.parse_value(value)
        except AuthResError as err:
            logger.error(f"{queue_id}: authres error: error={err!r}, text={value!r}")
        else:
            if header.authserv_id in config.get('trusted_authserv_ids'):
                logger.debug(f"{queue_id}: trusted authres: value={header.header_value()!r}")
                auth_results.extend(header.results)
                if not config.get('keep_ar_header'):
                    # Empty header text removes header instance
                    # Nth occurrence 1 means the first instance
                    manipulations.append(
                        ChangeHeader(headername=header.HEADER_FIELD_NAME, headertext='', nth_occurrence=idx + 1)
                    )
            else:
                logger.debug(f"{queue_id}: ignoring authres: value={header.header_value()!r}")
    
    ip_addr = ctx_client.get().addr
    helo = ctx_helo.get('')
    mail_from = ctx_mail_from.get()
    if config.get('spf_enabled'):
        logger.debug(f"{queue_id}: check spf: ip_addr={ip_addr!r}, helo={helo!r}, mail_from={mail_from!r}")
        ares = await check_spf(ip_addr, helo, mail_from)
        auth_results.append(ares)
    for ares in auth_results:
        if ares.result == 'pass' and ares.method == 'dkim':
            logger.info(f"{queue_id}: DKIM-Authenticated identifier: {ares.header_d}")
        elif ares.result == 'pass' and ares.method == 'spf':
            logger.info(f"{queue_id}: SPF-Authenticated identifier: {ares.smtp_mailfrom or ares.smtp_helo}")
    logger.debug(
        f"{queue_id}: check dmarc: domain={domain!r}, auth_results={auth_results!r}, ip_addr={ip_addr!r}, psl={psl!r}"
    )
    ares = await check_dmarc(domain, auth_results, ip_addr, psl)
    auth_results.append(ares)
    if ares.result == 'none':
        logger.info(f"{queue_id}: no policy published for {domain}")
        response = Accept()
    elif ares.result == 'pass':
        logger.info(f"{queue_id}: DMARC verification successful")
        response = Accept()
    else:
        logger.info(f"{queue_id}: DMARC verification failed")
        policy = config.get('policy')
        if ares.policy in policy:
            response = get_policy_response(**policy[ares.policy])
        else:
            logger.error(f"{queue_id}: unknown local policy: {ares.policy}")
            response = CauseConnectionFail()
    header = AuthenticationResultsHeader(authserv_id=config.get('myauthserv_id'), results=auth_results)
    if config.get('log_ar_header'):
        logger.info(f"{queue_id}: {header.header_value()}")
    if config.get('add_ar_header'):
        manipulations.append(
            InsertHeader(index=1, headername=header.HEADER_FIELD_NAME, headertext=header.header_value())
        )
    response.manipulations.extend(manipulations)
    return response

milter = PurePythonMilter(
    name="dmarcmilter",
    hook_on_connect=on_connect,
    hook_on_helo=on_helo,
    hook_on_mail_from=on_mail_from,
    hook_on_header=on_header,
    hook_on_end_of_message=on_end_of_message,
    can_add_headers=True,
    can_change_headers=True,
    can_quarantine=True,
    restrict_symbols=None,
)
logger = milter.logger

@click.command(
    context_settings={
        "auto_envvar_prefix": milter.name,
    }
)
@click.option("--bind-host")
@click.option("--bind-port", type=int)
@click.option(
    "-l", "--log-level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
@click.option("-c", "--config-file", type=click.File('rb'))
@click.version_option(prog_name=milter.name)
def main(*, bind_host: str, bind_port: int, log_level: str, config_file: BinaryIO) -> None:
    logger = logging.getLogger(__name__)
    if config_file:
        config.update(tomllib.load(config_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level or config.get('log_level'))
    )
    syslog = config.get('syslog')
    if syslog:
        logger.debug(f"use syslog: {syslog!r}")
        log_handler = SysLogHandler(syslog, SysLogHandler.LOG_MAIL)
        log_handler.setFormatter(logging.Formatter('[%(process)d]: %(message)s'))
        log_handler.ident = milter.name
        logging.getLogger().handlers.clear()
        logging.getLogger().addHandler(log_handler)
    
    publicsuffixlist = config.get('publicsuffixlist')
    if publicsuffixlist:
        logger.debug(f"load publicsuffixlist: {publicsuffixlist!r}")
        psl.load(publicsuffixlist)
    
    mynetworks = config.get('mynetworks')
    if mynetworks:
        logger.debug(f"mynetworks: {mynetworks!r}")
        mynet.readfp(mynetworks.split() if isinstance(mynetworks, str) else mynetworks)
    
    resolv_conf = config.get('resolver')
    if resolv_conf:
        nameservers = resolv_conf.get('nameservers')
        lifetime = resolv_conf.get('lifetime')
        if nameservers:
            logger.debug(f"resolver nameservers: {nameservers!r}")
            resolver.nameservers = nameservers
        if lifetime:
            logger.debug(f"resolver lifetime: {lifetime}")
            resolver.lifetime = lifetime
    
    logger.info(f"version {__version__}, configuration {getattr(config_file, 'name', config_file)}")
    milter.run_server(
        host=bind_host or config.get('bind_host'),
        port=bind_port or config.get('bind_port')
    )

if __name__ == "__main__":
    main()
