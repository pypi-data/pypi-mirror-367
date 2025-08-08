from __future__ import annotations
from publicsuffix2 import PublicSuffixList

PSL = None

def load(psl_file, idna: bool=True) -> PublicSuffixList:
    global PSL
    PSL = PublicSuffixList(psl_file, idna)
    return PSL

def get_public_suffix(domain: str) -> str | None:
    return PSL.get_sld(domain) if PSL else load(psl_file=None).get_sld(domain)
