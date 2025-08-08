import unittest, pkgutil

from dmarc.report import (
    DMARCRelaxedSchema,
    etree_tostring,
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
from dmarc import (
    DMARCResult,
    DMARCAlignment,
    DMARCDisposition,
    DMARCPolicyOverride,
    SPFResult,
    SPFDomainScope,
    DKIMResult,
)

class TestDMARCRelaxedSchema(unittest.TestCase):
    
    def setUp(self):
        self.schema = DMARCRelaxedSchema
    
    def test_xml_document_to_dict(self):
        self.assertEqual(TEST_DICT, self.schema.to_dict(TEST_XML_DOCUMENT))
    
    def test_dict_to_xml_document(self):
        etree = self.schema.to_etree(TEST_DICT)
        self.assertEqual(TEST_XML_DOCUMENT, etree_tostring(etree, encoding='UTF-8', xml_declaration=True))
    
    def test_report(self):
        metadata = ReportMetadata(
            org_name = 'acme.com',
            email = 'noreply-dmarc-support@acme.com',
            extra_contact_info = 'http://acme.com/dmarc/support',
            report_id = '9391651994964116463',
            date_range = DateRange(begin=1335571200, end=1335657599),
            error = ['There was a sample error.']
        )
        policy_published = PolicyPublished(
            domain = 'example.com',
            adkim = DMARCAlignment.RELAXED,
            aspf = DMARCAlignment.RELAXED,
            p = DMARCDisposition.NONE,
            sp = DMARCDisposition.NONE,
            pct = 100,
            fo = '1',
        )
        policy_evaluated = PolicyEvaluated(
            disposition = DMARCDisposition.NONE,
            dkim = DMARCResult.FAIL,
            spf = DMARCResult.PASS,
            reason = [PolicyOverrideReason(DMARCPolicyOverride.OTHER, 'DMARC Policy overridden for incoherent example.')]
        )
        row = Row(source_ip = '72.150.241.94', count = 2, policy_evaluated = policy_evaluated)
        identifiers = Identifiers(header_from='example.com', envelope_from='example.com', envelope_to='acme.com')
        auth_results = AuthResults(
            dkim = [
                DKIMAuthResult(domain='example.com', selector='ExamplesSelector', result=DKIMResult.FAIL, human_result='Incoherent example')
            ],
            spf = [
                SPFAuthResult(domain='example.com', scope=SPFDomainScope.HELO, result=SPFResult.PASS)
            ]
        )
        record = Record(row, identifiers, auth_results)
        report = Report(metadata, policy_published, [record])
        self.assertEqual(TEST_DICT, report.as_dict())

TEST_XML_DOCUMENT = pkgutil.get_data(__name__, "data/samplereport.xml")
TEST_DICT = {'report_metadata': {'org_name': 'acme.com',
                     'email': 'noreply-dmarc-support@acme.com',
                     'extra_contact_info': 'http://acme.com/dmarc/support',
                     'report_id': '9391651994964116463',
                     'date_range': {'begin': 1335571200, 'end': 1335657599},
                     'error': ['There was a sample error.']},
 'policy_published': {'domain': 'example.com',
                      'adkim': 'r',
                      'aspf': 'r',
                      'p': 'none',
                      'sp': 'none',
                      'pct': 100,
                      'fo': '1'},
 'record': [{'row': {'source_ip': '72.150.241.94',
                     'count': 2,
                     'policy_evaluated': {'disposition': 'none',
                                          'dkim': 'fail',
                                          'spf': 'pass',
                                          'reason': [{'type': 'other',
                                                      'comment': 'DMARC Policy '
                                                                 'overridden '
                                                                 'for '
                                                                 'incoherent '
                                                                 'example.'}]}},
             'identifiers': {'header_from': 'example.com',
                             'envelope_from': 'example.com',
                             'envelope_to': 'acme.com'},
             'auth_results': {'dkim': [{'domain': 'example.com',
                                        'selector': 'ExamplesSelector',
                                        'result': 'fail',
                                        'human_result': 'Incoherent example'}],
                              'spf': [{'domain': 'example.com',
                                       'scope': 'helo',
                                       'result': 'pass'}]}}]}
