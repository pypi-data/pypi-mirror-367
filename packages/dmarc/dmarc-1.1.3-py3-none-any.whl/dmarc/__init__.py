from __future__ import annotations

"""DMARC (Domain-based Message Authentication, Reporting & Conformance)

Typical Usage:

    >>> from dmarc import SPFAuthResult, DKIMAuthResult, SPFResult, DKIMResult, DMARCPolicy
    >>> # Represent verified SPF and DKIM identifiers
    >>> spf = SPFAuthResult('news.example.com', SPFResult('pass'))
    >>> dkim = DKIMAuthResult('example.com', DKIMResult('pass'))
    >>> policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
    >>> policy.verify(auth_results=[spf, dkim])
"""

import re
import importlib.metadata
import warnings
from enum import auto, Enum, IntFlag

__author__ = 'Dusan Obradovic <dusan@euracks.net>'
__version__ = importlib.metadata.version("dmarc")

def reverse_domain(domain: str) -> str:
    return '.'.join(reversed(domain.split('.')))

class Error(Exception):
    pass

class RecordSyntaxError(Error):
    pass

class RecordValueError(RecordSyntaxError):
    pass

class PolicyError(Error):
    pass

class PolicyNoneError(PolicyError):
    pass

class PolicyRejectError(PolicyError):
    pass

class PolicyQuarantineError(PolicyError):
    pass

class SPFResult(Enum):
    """SPF verification result.
    """
    NONE = 'none'
    PASS = 'pass'
    NEUTRAL = 'neutral'
    FAIL = 'fail'
    TEMPFAIL = 'temperror'
    PERMFAIL = 'permerror'
    SOFTFAIL = 'softfail'

class SPFDomainScope(Enum):
    """SPF domain scope.
    """
    HELO = 'helo'
    MFROM = 'mfrom'

class DKIMResult(Enum):
    """DKIM verification result.
    """
    NONE = 'none'
    PASS = 'pass'
    FAIL = 'fail'
    TEMPFAIL = 'temperror'
    PERMFAIL = 'permerror'
    NEUTRAL = 'neutral'
    POLICY = 'policy'

class DMARCResult(Enum):
    """The DMARC-aligned authentication result.
    """
    PASS = 'pass'
    FAIL = 'fail'

class DMARCDisposition(Enum):
    """The policy actions specified by p and sp in the
    DMARC record.
    """
    UNSPECIFIED = None
    NONE = 'none'
    REJECT = 'reject'
    QUARANTINE = 'quarantine'

class DMARCAlignment(Enum):
    """Alignment mode (relaxed or strict) for DKIM and SPF.
    """
    UNSPECIFIED = None
    RELAXED = 'r'
    STRICT = 's'

class DMARCReportFormat(IntFlag):
    UNSPECIFIED = 0x0
    AFRF = auto()
    IODEF = auto()
    
class DMARCFailureReportOptions(IntFlag):
    UNSPECIFIED = 0x0
    ALL = auto()
    ANY = auto()
    SPF = auto()
    DKIM = auto()

class DMARCPolicyOverride(Enum):
    """Reasons that may affect DMARC disposition or execution
    thereof.
    """
    FORWARDED = 'forwarded'
    SAMPLED_OUT = 'sampled_out'
    TRUSTED_FORWARDER = 'trusted_forwarder'
    MAILING_LIST = 'mailing_list'
    LOCAL_POLICY = 'local_policy'
    OTHER = 'other'

class AuthResult:
    pass

class SPF(AuthResult):
    
    def __init__(self, domain: str, result: SPFResult, scope: SPFDomainScope|None = None):
        """Represent a single domain SPF verification status
        
        Args:
            domain: Domain part of RFC5321.MailFrom
            result: SPFResult
            scope: SPFDomainScope
        """
        self.domain = domain
        self.result = result
        self.scope = scope
    
    @classmethod
    def from_authres(cls, ar):
        """
        Args:
            ar: SPFAuthenticationResult object
        
        Returns:
            An instance
        """
        
        if ar.smtp_mailfrom:
            domain = ar.smtp_mailfrom.split('@')[-1]
            scope = SPFDomainScope.MFROM
        else:
            domain = ar.smtp_helo
            scope = SPFDomainScope.HELO
        
        return cls(domain, SPFResult(ar.result), scope)

class DKIM(AuthResult):
    
    def __init__(self, domain: str, result: DKIMResult, selector: str|None = None, human_result: str|None = None):
        """Represent a single domain DKIM verification status
        
        Args:
            domain: Domain value of the signature header d= tag
            result: DKIMResult
            selector: Selector value of the signature header s= tag
            human_result: Any extra information
        """
        self.domain = domain
        self.result = result
        self.selector = selector
        self.human_result = human_result
    
    @classmethod
    def from_authres(cls, ar):
        """
        Args:
            ar: DKIMAuthenticationResult object
        
        Returns:
            An instance
        """
        
        return cls(ar.header_d, DKIMResult(ar.result), ar.header_s, ar.reason or ar.result_comment)

class Policy(object):
    """Policy object:
    
    v: Protocol version
    p: Policy for organizational domain
    sp: Policy for subdomains of the OD
    adkim: Alignment mode for DKIM
    aspf: Alignment mode for SPF
    pct: Percentage of messages subjected to filtering
    ri: Reporting interval
    rf: Reporting format
    rua: Reporting URI of aggregate reports
    ruf: Reporting URI for forensic reports
    fo: Error reporting policy
    domain: Domain part of RFC5322.From header
    org_domain: Organizational Domain of the sender domain
    ip_addr: Source IP address
    """
    def __init__(self, version: str, domain: str, org_domain: str|None = None, ip_addr: str|None = None):
        self.v: str = version
        self.p: DMARCDisposition = DMARCDisposition.UNSPECIFIED
        self.sp: DMARCDisposition = DMARCDisposition.UNSPECIFIED
        self.adkim: DMARCAlignment = DMARCAlignment.UNSPECIFIED
        self.aspf: DMARCAlignment = DMARCAlignment.UNSPECIFIED
        self.pct: int = -1
        self.ri: int = -1
        self.rf: DMARCReportFormat = DMARCReportFormat.UNSPECIFIED
        self.rua = []
        self.ruf = []
        self.fo: DMARCFailureReportOptions = DMARCFailureReportOptions.UNSPECIFIED
        self.domain = domain
        self.org_domain = org_domain
        self.ip_addr = ip_addr
    
    def parse_record(self, record: str, strict: bool = True) -> None:
        """Parse DMARC DNS record
        
        Args:
            record: TXT RR value
            strict: If strict is true, use strict parser which rejects invalid tag values
        
        Returns:
            None
        
        Raises:
            RecordValueError:  If the strict is true and the tag value is not valid
            
            RecordSyntaxError: If the record does not comply with the formal specification
                               in that the "v" and "p" tags must be present and appear in that order
        """
        
        # The record must start with "v=DMARC1"
        # and the string "DMARC" is the only portion that is case-sensitive...
        # 
        # Unknown tags are ignored.
        # 
        # If strict is not true, discard invalid tag values in the remainder of the record
        # in favor of default values (if any) or ignored outright.
        parts = record.rstrip(' ;').split(';')
        if len(parts) < 2:
            raise RecordSyntaxError(f"{record!r} is not a valid record")
        
        for i, part in enumerate(parts):
            res = re.match(r'^\s*([^=\s]+)\s*=(.*)$', part)
            try:
                tag = res.group(1).strip().lower()
                value = res.group(2).strip()
            except AttributeError:
                raise RecordSyntaxError(f"{part!r} is not a valid record tag")
            
            if i == 0:
                if tag != 'v' or value != self.v:
                    raise RecordSyntaxError(f"Record must start with v={self.v} tag")
                continue
            
            value = value.lower()
            try:
                if tag == 'p':
                    self.p = DMARCDisposition(value)
                elif tag == 'sp':
                    self.sp = DMARCDisposition(value)
                elif tag == 'adkim':
                    self.adkim = DMARCAlignment(value)
                elif tag == 'aspf':
                    self.aspf = DMARCAlignment(value)
                elif tag == 'pct':
                    self.pct = int(value)
                elif tag == 'ri':
                    self.ri = int(value)
                elif tag == 'rf':
                    for x in value.split(','):
                        if x == 'afrf':
                            self.rf |= DMARCReportFormat.AFRF
                        elif x == 'iodef':
                            self.rf |= DMARCReportFormat.IODEF
                elif tag == 'rua':
                    self.rua = value.split(',')
                elif tag == 'ruf':
                    self.ruf = value.split(',')
                elif tag == 'fo':
                    for x in value.split(':'):
                        if x == '0':
                            self.fo |= DMARCFailureReportOptions.ALL
                        elif x == '1':
                            self.fo |= DMARCFailureReportOptions.ANY
                        elif x == 'd':
                            self.fo |= DMARCFailureReportOptions.DKIM
                        elif x == 's':
                            self.fo |= DMARCFailureReportOptions.SPF
                    
            except ValueError as err:
                if strict:
                    raise RecordValueError(err)
        
        if self.p is DMARCDisposition.UNSPECIFIED:
            raise RecordSyntaxError('Record required tag p unspecified')
        
        if self.adkim is DMARCAlignment.UNSPECIFIED:
            self.adkim = DMARCAlignment.RELAXED
        
        if self.aspf is DMARCAlignment.UNSPECIFIED:
            self.aspf = DMARCAlignment.RELAXED
        
        if self.pct < 0:
            self.pct = 100
        
        if self.rf is DMARCReportFormat.UNSPECIFIED:
            self.rf = DMARCReportFormat.AFRF
        
        if self.ri < 0:
            self.ri = 86400
        
        if self.fo is DMARCFailureReportOptions.UNSPECIFIED:
            self.fo = DMARCFailureReportOptions.ALL

class Result(object):
    """Result object keeps policy evaluated 
    results:
    
    dkim:         DKIM identifier alignment result,
                  DMARCResult
    
    spf:          SPF identifier alignment result,
                  DMARCResult
                  
    result:       Policy evaluated result,
                  DMARCResult
                  
    disposition:  Policy to enforce,
                  DMARCDisposition
    
    reason:       Policy override reason,
                  DMARCPolicyOverride
    
    policy:       Policy object
    
    aspf:         SPF object
    
    adkim:        DKIM object
    """
    def __init__(self, policy: Policy, aspf: SPF|None, adkim: DKIM|None):
        self.dkim: DMARCResult = DMARCResult.FAIL
        self.spf: DMARCResult = DMARCResult.FAIL
        self.result: DMARCResult = DMARCResult.FAIL
        self.disposition: DMARCDisposition = DMARCDisposition.UNSPECIFIED
        self.reason: DMARCPolicyOverride | None = None
        self.policy = policy
        self.aspf = aspf
        self.adkim = adkim
    
    def verify(self) -> None:
        """Policy disposition verification
        
        Returns:
            None
        
        Raises:
            PolicyNoneError: if DMARCResult.FAIL and DMARCDisposition.NONE
            PolicyQuarantineError: if DMARCResult.FAIL and DMARCDisposition.QUARANTINE
            PolicyRejectError: if DMARCResult.FAIL and DMARCDisposition.REJECT
            PolicyError: if DMARCResult.FAIL and unknown disposition error
        """
        warnings.warn("Use DMARCPolicy.verify() instead", DeprecationWarning, stacklevel=2)
        if self.result is DMARCResult.FAIL:
            if self.disposition is DMARCDisposition.NONE:
                raise PolicyNoneError
            
            elif self.disposition is DMARCDisposition.QUARANTINE:
                raise PolicyQuarantineError
            
            elif self.disposition is DMARCDisposition.REJECT:
                raise PolicyRejectError
            
            else:
                raise PolicyError
    
    def as_dict(self):
        warnings.warn("Use DMARCPolicy.get_report().as_dict() instead", DeprecationWarning, stacklevel=2)
        policy_published = {}
        policy_evaluated = {}
        row = {}
        identifiers = {}
        auth_results = {}
        dkim = {}
        spf = {}
        
        policy_published['domain'] = self.policy.org_domain or self.policy.domain
        policy_published['adkim'] = self.policy.adkim.value
        policy_published['aspf'] = self.policy.aspf.value
        policy_published['p'] = self.policy.p.value
        if self.policy.sp is not DMARCDisposition.UNSPECIFIED:
            policy_published['sp'] = self.policy.sp.value
        
        policy_published['pct'] = self.policy.pct
        
        policy_evaluated['disposition'] = self.disposition.value
        policy_evaluated['dkim'] = self.dkim.value
        policy_evaluated['spf'] = self.spf.value
        
        if self.policy.ip_addr:
            row['source_ip'] = self.policy.ip_addr
        
        row['count'] = 1
        row['policy_evaluated'] = policy_evaluated
        
        identifiers['header_from'] = self.policy.domain
        
        if self.adkim:
            dkim['domain'] = self.adkim.domain
            if self.adkim.result:
                dkim['result'] = self.adkim.result.value
            if self.adkim.selector:
                dkim['selector'] = self.adkim.selector
            if self.adkim.human_result:
                dkim['human_result'] = self.adkim.human_result
            
            auth_results['dkim'] = dkim
        
        if self.aspf:
            spf['domain'] = self.aspf.domain
            if self.aspf.scope:
                spf['scope'] = self.aspf.scope.value
            if self.aspf.result:
                spf['result'] = self.aspf.result.value
            
            auth_results['spf'] = spf
        
        return {
            'policy_published':policy_published,
            'record':{
                'row':row,
                'identifiers':identifiers,
                'auth_results':auth_results
            }
        }        

class DMARC(object):
    def __init__(self, publicsuffix=None):
        """The DMARC constructor accepts PublicSuffixList object,
        and (if given) will be used for determining Organizational Domain
        """
        self.publicsuffix = publicsuffix
    
    def get_result(self, policy: Policy, spf: SPF|None = None, dkim: DKIM|None = None) -> Result:
        """Policy evaluation
        
        Args:
            policy: Policy object
            spf: SPF object
            dkim: DKIM object
        
        Returns:
            Result object
        """
        res = Result(policy, aspf=spf, adkim=dkim)
        
        if dkim and dkim.result is DKIMResult.PASS and self.check_alignment(
            policy.domain, dkim.domain, policy.adkim, self.publicsuffix):
            res.dkim = DMARCResult.PASS
        
        if spf and spf.result is SPFResult.PASS and self.check_alignment(
            policy.domain, spf.domain, policy.aspf, self.publicsuffix):
            res.spf = DMARCResult.PASS
        
        if DMARCResult.PASS in (res.spf, res.dkim):
            res.result = DMARCResult.PASS
            res.disposition = DMARCDisposition.NONE
        elif policy.org_domain and policy.sp is not DMARCDisposition.UNSPECIFIED:
            res.disposition = policy.sp
        else:
            res.disposition = policy.p
        
        return res
    
    def check_alignment(self, fd: str, ad: str, mode: DMARCAlignment, psl=None) -> bool:
        if not all((fd, ad, mode)):
            raise ValueError
        
        rev_fd = reverse_domain(fd.lower()) + '.'
        rev_ad = reverse_domain(ad.lower()) + '.'
        
        if rev_ad == rev_fd:
            return True
        
        if rev_fd[:len(rev_ad)] == rev_ad and mode is DMARCAlignment.RELAXED:
            return True
        
        if rev_ad[:len(rev_fd)] == rev_fd and mode is DMARCAlignment.RELAXED:
            return True
        
        if psl and mode is DMARCAlignment.RELAXED:
            return self.check_alignment(fd, psl.get_public_suffix(ad), mode)
        
        return False
    
    def parse_record(self, record: str, domain: str, org_domain: str|None = None, ip_addr: str|None = None, strict: bool = True) -> Policy:
        """Parse DMARC DNS record
        
        Args:
            record: TXT RR value
            domain: Domain part of RFC5322.From header
            org_domain: Organizational Domain of the sender domain
            ip_addr: Source IP address
            strict: If strict is true, use strict parser which rejects invalid tag values
        
        Returns:
            Policy object
        
        Raises:
            RecordValueError:  If the strict is true and the tag value is not valid
            
            RecordSyntaxError: If the record does not comply with the formal specification
                               in that the "v" and "p" tags must be present and appear in that order
        """
        policy = Policy('DMARC1', domain, org_domain, ip_addr)
        policy.parse_record(record, strict)
        return policy

class BaseResult:
    
    def __iter__(self):
        for key in self.__dict__:
            if self.__dict__[key] is not None:
                yield key
    
    def __getitem__(self, name):
        return self.__dict__[name]
    
    def as_dict(self):
        def convert_value(value):
            if isinstance(value, Enum):
                return value.value
            elif isinstance(value, BaseResult):
                return value.as_dict()
            elif isinstance(value, list):
                return [convert_value(x) for x in value]
            else:
                return value
        
        return {key: convert_value(self[key]) for key in iter(self)}

class Report(BaseResult):
    
    def __init__(self, report_metadata: ReportMetadata, policy_published: PolicyPublished, record: list[Record], version: float|None = None):
        self.version = version
        self.report_metadata = report_metadata
        self.policy_published = policy_published
        self.record = record

class ReportMetadata(BaseResult):
    """Report generator metadata.
    """
    def __init__(self, org_name: str, email: str, report_id: str, date_range: DateRange, extra_contact_info: str|None = None, error: list[str]|None = None):
        self.org_name = org_name
        self.email = email
        self.extra_contact_info = extra_contact_info
        self.report_id = report_id
        self.date_range = date_range
        self.error = error

class DateRange(BaseResult):
    """The time range in UTC covered by messages in this report,
    specified in seconds since epoch.
    """
    def __init__(self, begin: int, end: int):
        self.begin = begin
        self.end = end

class PolicyPublished(BaseResult):
    """The DMARC policy that applied to the messages in
    this report.
    """
    def __init__(
            self,
            domain: str,
            p: DMARCDisposition,
            pct: int,
            sp: DMARCDisposition|None = None,
            adkim: DMARCAlignment|None = None,
            aspf: DMARCAlignment|None = None,
            fo: str|None = None
    ):
        """
        Args:
            domain:    The domain at which the DMARC record was found
            
            p:         The policy to apply to messages from the domain,
                       DMARCDisposition
            
            sp:        The policy to apply to messages from subdomains,
                       DMARCDisposition
            
            adkim:     The DKIM alignment mode,
                       DMARCAlignment
            
            aspf:      The SPF alignment mode,
                       DMARCAlignment
            
            pct:       The percent of messages to which policy applies
            
            fo:        Failure reporting options in effect
        """
        self.domain = domain
        self.p = p
        self.sp = sp
        self.adkim = adkim
        self.aspf = aspf
        self.pct = pct
        self.fo = fo

class Record(BaseResult):
    """The authentication results that were evaluated by the receiving system
    for the given set of messages.
    """
    def __init__(self, row: Row, identifiers: Identifiers, auth_results: AuthResults):
        self.row = row
        self.identifiers = identifiers
        self.auth_results = auth_results

class SPFAuthResult(SPF, BaseResult):
    pass

class DKIMAuthResult(DKIM, BaseResult):
    pass

class AuthResults(BaseResult):
    """There may be no DKIM signatures, or multiple DKIM
    signatures. There will always be at least one SPF result.
    """
    def __init__(self, spf: list[SPFAuthResult], dkim: list[DKIMAuthResult]|None = None):
        self.dkim = dkim
        self.spf = spf

class Identifiers(BaseResult):
    
    def __init__(self, header_from: str, envelope_from: str|None = None, envelope_to: str|None = None):
        """
        Args:
            header_from:    The RFC5322.From domain
            envelope_from:  The RFC5321.MailFrom domain
            envelope_to:    The envelope recipient domain
        """
        self.header_from = header_from
        self.envelope_from = envelope_from
        self.envelope_to = envelope_to

class Row(BaseResult):
    
    def __init__(self, source_ip: str, count: int, policy_evaluated: PolicyEvaluated):
        """
        Args:
            source_ip:        The connecting IP
            
            count:            The number of matching messages
            
            policy_evaluated: The DMARC disposition applying to matching messages,
                              PolicyEvaluated
            
        """
        self.source_ip = source_ip
        self.count = count
        self.policy_evaluated = policy_evaluated

class PolicyOverrideReason(BaseResult):
    
    def __init__(self, policy_override: DMARCPolicyOverride, comment: str|None = None):
        self.type = policy_override
        self.comment = comment

class PolicyEvaluated(BaseResult):
    """Taking into account everything else in the record,
    the results of applying DMARC.
    """
    def __init__(self, disposition: DMARCDisposition, spf: DMARCResult, dkim: DMARCResult, reason: list[PolicyOverrideReason]|None = None):
        self.disposition = disposition
        self.dkim = dkim
        self.spf = spf
        self.reason = reason

class DMARCPolicy(object):
    """DMARC evaluation
    
    Attributes:
        dmarc:  DMARC object
        policy: Policy object
        result: Result object
    """
    def __init__(self, record: str, domain: str, org_domain: str|None = None, ip_addr: str|None = None, publicsuffix=None, strict: bool = True):
        """
        Args:
            record: TXT RR value
            domain: Domain part of RFC5322.From header
            org_domain: Organizational Domain of the sender domain
            ip_addr: Source IP address
            publicsuffix: PublicSuffixList object
            strict: If strict is true, use strict parser which rejects invalid tag values
        
        Raises:
            RecordValueError:  If the strict is true and the tag value is not valid
            
            RecordSyntaxError: If the record does not comply with the formal specification
                               in that the "v" and "p" tags must be present and appear in that order
        """
        self.dmarc: DMARC = DMARC(publicsuffix)
        self.policy: Policy = self.dmarc.parse_record(record, domain, org_domain, ip_addr, strict)
        self.result: Result|None = None
    
    def verify(self, spf: SPF|None = None, dkim: DKIM|None = None, auth_results: list[AuthResult] = []) -> None:
        """Policy disposition verification
        
        Args:
            spf: SPF object
            dkim: DKIM object
            auth_results: Iterable (of authentication results)
        
        Returns:
            None
        
        Raises:
            PolicyNoneError: if DMARCResult.FAIL and DMARCDisposition.NONE
            PolicyQuarantineError: if DMARCResult.FAIL and DMARCDisposition.QUARANTINE
            PolicyRejectError: if DMARCResult.FAIL and DMARCDisposition.REJECT
            PolicyError: if DMARCResult.FAIL and unknown disposition error
        """
        for ar in auth_results:
            # The aligned authentication result is chosen over any result
            if isinstance(ar, SPF):
                spf = ar if self.isaligned(ar) else spf or ar
            elif isinstance(ar, DKIM):
                dkim = ar if self.isaligned(ar) else dkim or ar
        
        self.result = self.dmarc.get_result(self.policy, spf, dkim)
        if self.result.result is DMARCResult.FAIL:
            if self.result.disposition is DMARCDisposition.NONE:
                raise PolicyNoneError("Policy verification failed. Disposition type 'none'.")
            
            elif self.result.disposition is DMARCDisposition.QUARANTINE:
                raise PolicyQuarantineError("Policy verification failed. Disposition type 'quarantine'.")
            
            elif self.result.disposition is DMARCDisposition.REJECT:
                raise PolicyRejectError("Policy verification failed. Disposition type 'reject'.")
            
            else:
                raise PolicyError("Policy verification failed.")
    
    def isaligned(self, ar: AuthResult) -> bool:
        if isinstance(ar, SPF):
            return (
                ar.result is SPFResult.PASS and 
                self.dmarc.check_alignment(
                    self.policy.domain,
                    ar.domain,
                    self.policy.aspf,
                    self.dmarc.publicsuffix
                )
            )
        elif isinstance(ar, DKIM):
            return (
                ar.result is DKIMResult.PASS and 
                self.dmarc.check_alignment(
                    self.policy.domain,
                    ar.domain,
                    self.policy.adkim,
                    self.dmarc.publicsuffix
                )
            )
        else:
            raise ValueError("invalid authentication result '{0}'".format(ar))
    
    def get_report(self, metadata: ReportMetadata | None = None) -> Report:
        policy_published = PolicyPublished(
            domain = self.policy.org_domain or self.policy.domain,
            adkim = self.policy.adkim,
            aspf = self.policy.aspf,
            p = self.policy.p,
            sp = self.policy.sp if self.policy.sp is not DMARCDisposition.UNSPECIFIED else None,
            pct = self.policy.pct
        )
        policy_evaluated = PolicyEvaluated(
            disposition = self.result.disposition,
            dkim = self.result.dkim,
            spf = self.result.spf,
            reason = [PolicyOverrideReason(self.result.reason)] if self.result.reason else None
        )
        row = Row(source_ip = self.policy.ip_addr, count = 1, policy_evaluated = policy_evaluated)
        identifiers = Identifiers(header_from = self.policy.domain)
        auth_results = AuthResults(
            dkim = [self.result.adkim] if self.result.adkim else None,
            spf = [self.result.aspf] if self.result.aspf else None
        )
        record = Record(row, identifiers, auth_results)
        report = Report(metadata, policy_published, [record])
        return report

SPF_PASS = SPFResult.PASS
SPF_NEUTRAL = SPFResult.NEUTRAL
SPF_FAIL = SPFResult.FAIL
SPF_TEMPFAIL = SPFResult.TEMPFAIL
SPF_PERMFAIL = SPFResult.PERMFAIL
SPF_SOFTFAIL = SPFResult.SOFTFAIL
SPF_SCOPE_MFROM = SPFDomainScope.MFROM
SPF_SCOPE_HELO = SPFDomainScope.HELO

DKIM_PASS = DKIMResult.PASS
DKIM_FAIL = DKIMResult.FAIL
DKIM_TEMPFAIL = DKIMResult.TEMPFAIL
DKIM_PERMFAIL = DKIMResult.PERMFAIL
DKIM_NEUTRAL = DKIMResult.NEUTRAL

POLICY_PASS = DMARCResult.PASS
POLICY_FAIL = DMARCResult.FAIL
POLICY_DIS_NONE = DMARCDisposition.NONE
POLICY_DIS_REJECT = DMARCDisposition.REJECT
POLICY_DIS_QUARANTINE = DMARCDisposition.QUARANTINE
POLICY_SPF_ALIGNMENT_PASS = DMARCResult.PASS
POLICY_SPF_ALIGNMENT_FAIL = DMARCResult.FAIL
POLICY_DKIM_ALIGNMENT_PASS = DMARCResult.PASS
POLICY_DKIM_ALIGNMENT_FAIL = DMARCResult.FAIL

RECORD_P_UNSPECIFIED = DMARCDisposition.UNSPECIFIED
RECORD_P_NONE = DMARCDisposition.NONE
RECORD_P_REJECT = DMARCDisposition.REJECT
RECORD_P_QUARANTINE = DMARCDisposition.QUARANTINE
RECORD_A_UNSPECIFIED = DMARCAlignment.UNSPECIFIED
RECORD_A_RELAXED = DMARCAlignment.RELAXED
RECORD_A_STRICT = DMARCAlignment.STRICT
RECORD_RF_UNSPECIFIED = DMARCReportFormat.UNSPECIFIED
RECORD_RF_AFRF = DMARCReportFormat.AFRF
RECORD_RF_IODEF = DMARCReportFormat.IODEF
RECORD_FO_UNSPECIFIED = DMARCFailureReportOptions.UNSPECIFIED
RECORD_FO_0 = DMARCFailureReportOptions.ALL
RECORD_FO_1 = DMARCFailureReportOptions.ANY
RECORD_FO_D = DMARCFailureReportOptions.DKIM
RECORD_FO_S = DMARCFailureReportOptions.SPF
