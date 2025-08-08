from __future__ import annotations

import pkgutil
from xmlschema import (
    XMLSchema,
    etree_tostring,
)
from dmarc import (
    Report,
    ReportMetadata,
    DateRange,
    PolicyPublished,
    Record,
    SPFAuthResult,
    DKIMAuthResult,
    AuthResults,
    Identifiers,
    Row,
    PolicyOverrideReason,
    PolicyEvaluated,
)

DMARCSchema = XMLSchema(pkgutil.get_data(__name__, "schemas/dmarc.xsd"))
DMARCRelaxedSchema = XMLSchema(pkgutil.get_data(__name__, "schemas/dmarc-relaxed.xsd"))
