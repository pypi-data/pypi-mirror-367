"""DMARC resolver

Typical Usage:

    >>> from dmarc.resolver import resolve
    >>> record = resolve('example.com') 
"""

from dns.resolver import get_default_resolver, NXDOMAIN, NoAnswer, Answer
from dns.exception import DNSException
from . import Error

resolver = get_default_resolver()

class RecordResolverError(Error):
    pass

class RecordNotFoundError(RecordResolverError):
    pass

class RecordMultiFoundError(RecordResolverError):
    pass

class RecordNoDataError(RecordNotFoundError):
    pass

def resolve(domain: str) -> str:
    try:
        answers = resolver.resolve('_dmarc.{0}'.format(domain), 'TXT')
        return response(answers)
    except NXDOMAIN as err:
        raise RecordNotFoundError(err)
    except NoAnswer as err:
        raise RecordNoDataError(err)
    except DNSException as err:
        raise RecordResolverError(err)

def response(answers: Answer) -> str:
    if len(answers) > 1:
        raise RecordMultiFoundError('A domain can only have one DMARC record.')
    return b''.join(answers[0].strings).decode()
        