"""DMARC asyncresolver

Typical Usage:

    >>> from dmarc.asyncresolver import resolve
    >>> record = await resolve('example.com')
"""

from dns.asyncresolver import get_default_resolver
from .resolver import (
    response,
    DNSException,
    NXDOMAIN,
    NoAnswer,
    RecordResolverError,
    RecordNotFoundError,
    RecordNoDataError,
    RecordMultiFoundError,
)

resolver = get_default_resolver()

async def resolve(domain: str) -> str:
    try:
        answers = await resolver.resolve('_dmarc.{0}'.format(domain), 'TXT')
        return response(answers)
    except NXDOMAIN as err:
        raise RecordNotFoundError(err)
    except NoAnswer as err:
        raise RecordNoDataError(err)
    except DNSException as err:
        raise RecordResolverError(err)
