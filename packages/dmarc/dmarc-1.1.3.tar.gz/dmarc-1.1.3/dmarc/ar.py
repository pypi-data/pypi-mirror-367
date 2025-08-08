import warnings
warnings.warn("Use authres module instead", DeprecationWarning, stacklevel=2)

from authres import (
    AuthenticationResult,
    AuthenticationResultProperty,
    SPFAuthenticationResult,
    DKIMAuthenticationResult,
    AuthenticationResultsHeader,
    AuthResError,
)
from authres.dmarc import DMARCAuthenticationResult
def authres(result=None, **kwargs) -> DMARCAuthenticationResult:
    """This is a convenience factory function that uses the dmarc.Result object
    to make the DMARCAuthenticationResult object.
    
    Args:
        result: dmarc.Result object
    
    Returns:
        DMARCAuthenticationResult object
    """
    warnings.warn("This function is deprecated", DeprecationWarning, stacklevel=2)
    kwargs['result'] = 'none'
    if result:
        kwargs['result'] = result.result.value
        adict = result.as_dict()
        policy_published = adict['policy_published']
        policy_evaluated = adict['record']['row']['policy_evaluated']
        kwargs['result_comment'] = ' '.join('{0}=%({1})s'.format(key,key) for key in policy_published) % policy_published
        kwargs['header_from'] = result.policy.domain
        kwargs['policy'] = policy_evaluated['disposition']
        kwargs['policy_comment'] = ' '.join('{0}=%({1})s'.format(key,key) for key in policy_evaluated) % policy_evaluated
    
    return DMARCAuthenticationResult(**kwargs)
