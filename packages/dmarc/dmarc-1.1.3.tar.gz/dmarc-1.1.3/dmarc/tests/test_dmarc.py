import unittest

from dmarc import (
    reverse_domain,
    DMARC,
    SPF,
    DKIM,
    Result,
    Policy,
    DMARCPolicy,
    RecordSyntaxError,
    RecordValueError,
    PolicyNoneError,
    PolicyRejectError,
    PolicyQuarantineError,
    RECORD_P_UNSPECIFIED,
    RECORD_P_NONE,
    RECORD_P_REJECT,
    RECORD_P_QUARANTINE,
    RECORD_A_RELAXED,
    RECORD_A_STRICT,
    RECORD_RF_AFRF,
    RECORD_RF_IODEF,
    RECORD_FO_0,
    RECORD_FO_1,
    RECORD_FO_D,
    RECORD_FO_S,
    SPF_PASS,
    SPF_FAIL,
    SPF_SCOPE_MFROM,
    DKIM_PASS,
    DKIM_FAIL,
    POLICY_PASS,
    POLICY_FAIL,
    POLICY_DIS_NONE,
    POLICY_DIS_REJECT,
    POLICY_DIS_QUARANTINE,
    POLICY_SPF_ALIGNMENT_PASS,
    POLICY_SPF_ALIGNMENT_FAIL,
    POLICY_DKIM_ALIGNMENT_PASS,
    POLICY_DKIM_ALIGNMENT_FAIL,
    SPFAuthResult,
    DKIMAuthResult,
    Report,
    PolicyPublished,
    Record,
)

class TestFunctions(unittest.TestCase):
    
    def test_reverse_domain(self):
        self.assertEqual(reverse_domain('example.com'), 'com.example')

class TestPolicy(unittest.TestCase):
    
    def test_parse_record(self):
        policy = Policy('DMARC1', 'example.com')
        policy.parse_record(
            'v=DMARC1; p=reject; sp=quarantine; adkim=s; pct=50; ri=3600; RF = AFRF,IODEF; RUA = MAILTO:Dmarc@example.com ; ruf=mailto:forensic@example.com; fo=0:1:d:s; unknown=test'
        )
        self.assertEqual(policy.p, RECORD_P_REJECT)
        self.assertEqual(policy.sp, RECORD_P_QUARANTINE)
        self.assertEqual(policy.adkim, RECORD_A_STRICT)
        self.assertEqual(policy.aspf, RECORD_A_RELAXED)
        self.assertEqual(policy.pct, 50)
        self.assertEqual(policy.ri, 3600)
        self.assertEqual(policy.rf, RECORD_RF_AFRF | RECORD_RF_IODEF)
        self.assertEqual(policy.rua, ['mailto:dmarc@example.com'])
        self.assertEqual(policy.ruf, ['mailto:forensic@example.com'])
        self.assertEqual(policy.fo, RECORD_FO_0 | RECORD_FO_1 | RECORD_FO_D | RECORD_FO_S)
    
    def test_parse_record_syntax_invalid(self):
        records = [
            ('', "'' is not a valid record"),
            ('v=DMARC1 p=none', "'v=DMARC1 p=none' is not a valid record"),
            ('p=none', "'p=none' is not a valid record"),
            ('v=DMARC1; p:none', "' p:none' is not a valid record tag"),
            ('v=DAMRC1; p=none', "Record must start with v=DMARC1 tag"),
            ('v=dmarc1; p=none;', "Record must start with v=DMARC1 tag"),
            ('p=none; v=DMARC1', "Record must start with v=DMARC1 tag"),
            ('v=DMARC1; sp=none', "Record required tag p unspecified"),
        ]
        policy = Policy('DMARC1', 'example.com')
        for record, err in records:
            with self.assertRaises(RecordSyntaxError) as cm:
                policy.parse_record(record)
            self.assertEqual(err, str(cm.exception))
    
    def test_parse_record_value_invalid(self):
        records = [
            ('v=DMARC1; p=reject; sp=pass', "'pass' is not a valid DMARCDisposition"),
            ('v=DMARC1; p=pass', "'pass' is not a valid DMARCDisposition"),
            ('v=DMARC1; p=none; adkim=none', "'none' is not a valid DMARCAlignment"),
            ('v=DMARC1; p=none; aspf=none', "'none' is not a valid DMARCAlignment"),
        ]
        policy = Policy('DMARC1', 'example.com')
        for record, err in records:
            with self.assertRaises(RecordValueError) as cm:
                policy.parse_record(record)
            self.assertEqual(err, str(cm.exception))
    
    def test_parse_record_not_strict(self):
        policy = Policy('DMARC1', 'example.com')
        policy.parse_record('v=DMARC1; p=none; sp=test; adkim=test; aspf=test; pct=test', strict=False)
        self.assertEqual(policy.p, RECORD_P_NONE)
        self.assertEqual(policy.sp, RECORD_P_UNSPECIFIED)
        self.assertEqual(policy.adkim, RECORD_A_RELAXED)
        self.assertEqual(policy.aspf, RECORD_A_RELAXED)
        self.assertEqual(policy.pct, 100)
        self.assertEqual(policy.ri, 86400)
        self.assertEqual(policy.rf, RECORD_RF_AFRF)
        self.assertEqual(policy.rua, [])
        self.assertEqual(policy.ruf, [])
        self.assertEqual(policy.fo, RECORD_FO_0)

class TestDMARC(unittest.TestCase):
    
    def setUp(self):
        self.dmarc = DMARC()
    
    def test_parse_record(self):
        policy = self.dmarc.parse_record('v=DMARC1; p=none', 'news.example.com', 'example.com')
        self.assertIsInstance(policy, Policy)
        self.assertEqual(policy.v, 'DMARC1')
        self.assertEqual(policy.p, RECORD_P_NONE)
        self.assertEqual(policy.domain, 'news.example.com')
        self.assertEqual(policy.org_domain, 'example.com')
    
    def test_alignment(self):
        self.assertTrue(self.dmarc.check_alignment('example.com', 'news.example.com', RECORD_A_RELAXED))
        self.assertTrue(self.dmarc.check_alignment('news.example.com', 'example.com', RECORD_A_RELAXED))
        self.assertFalse(self.dmarc.check_alignment('example.com', 'news.example.com', RECORD_A_STRICT))
        self.assertFalse(self.dmarc.check_alignment('news.example.com', 'example.com', RECORD_A_STRICT))
    
    def test_alignment_mixed_case(self):
        self.assertTrue(self.dmarc.check_alignment('EXAMPLE.COM', 'news.example.com', RECORD_A_RELAXED))
        self.assertTrue(self.dmarc.check_alignment('NEWS.EXAMPLE.COM', 'example.com', RECORD_A_RELAXED))
        self.assertFalse(self.dmarc.check_alignment('EXAMPLE.COM', 'news.example.com', RECORD_A_STRICT))
        self.assertFalse(self.dmarc.check_alignment('NEWS.EXAMPLE.COM', 'example.com', RECORD_A_STRICT))
    
    def test_alignment_value_invalid(self):
        self.assertRaises(ValueError, self.dmarc.check_alignment, fd=None, ad=None, mode=None)
        self.assertRaises(ValueError, self.dmarc.check_alignment, fd=None, ad='news.example.com', mode=RECORD_A_RELAXED)
        self.assertRaises(ValueError, self.dmarc.check_alignment, fd='example.com', ad=None, mode=RECORD_A_RELAXED)
        self.assertRaises(ValueError, self.dmarc.check_alignment, fd='example.com', ad='news.example.com', mode=None)
    
    def test_result_spf_alignment(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = None
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_PASS)
        self.assertEqual(result.disposition, POLICY_DIS_NONE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_PASS)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
    
    def test_result_dkim_alignment(self):
        aspf = None
        adkim = DKIM(domain='news.example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_PASS)
        self.assertEqual(result.disposition, POLICY_DIS_NONE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_PASS)
    
    def test_result_spf_dkim_alignment(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='news.example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_PASS)
        self.assertEqual(result.disposition, POLICY_DIS_NONE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_PASS)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_PASS)
    
    def test_result_no_alignment(self):
        aspf = None
        adkim = None
        policy = self.dmarc.parse_record(record='v=DMARC1; p=none', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_FAIL)
        self.assertEqual(result.disposition, POLICY_DIS_NONE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
    
    def test_result_reject(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='example.com', result=DKIM_FAIL)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject; aspf=s; adkim=s;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_FAIL)
        self.assertEqual(result.disposition, POLICY_DIS_REJECT)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
        self.assertRaises(PolicyRejectError, result.verify)
    
    def test_result_quarantine(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=quarantine; adkim=s;', domain='mail.example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_FAIL)
        self.assertEqual(result.disposition, POLICY_DIS_QUARANTINE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
        self.assertRaises(PolicyQuarantineError, result.verify)
    
    def test_result_quarantine_subdomain(self):
        aspf = SPF(domain='news.example.com', result=SPF_PASS)
        adkim = DKIM(domain='example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=none; sp=quarantine; adkim=s;', domain='mail.example.com', org_domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(result.result, POLICY_FAIL)
        self.assertEqual(result.disposition, POLICY_DIS_QUARANTINE)
        self.assertEqual(result.spf, POLICY_SPF_ALIGNMENT_FAIL)
        self.assertEqual(result.dkim, POLICY_DKIM_ALIGNMENT_FAIL)
        self.assertRaises(PolicyQuarantineError, result.verify)
    
    def test_result_as_dict(self):
        expected = {
            'policy_published': {'domain': 'example.com', 'adkim': 'r', 'aspf': 'r', 'p': 'reject', 'pct': 100},
            'record': {
                'row': {
                    'count': 1,
                    'policy_evaluated': {'disposition': 'none', 'dkim': 'pass', 'spf': 'pass'}
                },
                'identifiers': {'header_from': 'example.com'},
                'auth_results': {
                    'dkim': {'domain': 'example.com', 'result': 'pass'},
                    'spf': {'domain': 'news.example.com', 'scope': 'mfrom', 'result': 'pass'}
                }
            }
        }
        aspf = SPF(domain='news.example.com', result=SPF_PASS, scope=SPF_SCOPE_MFROM)
        adkim = DKIM(domain='example.com', result=DKIM_PASS)
        policy = self.dmarc.parse_record(record='v=DMARC1; p=reject;', domain='example.com')
        result = self.dmarc.get_result(policy, aspf, adkim)
        self.assertEqual(expected, result.as_dict())

class TestDMARCPolicy(unittest.TestCase):
    
    def test_policy(self):
        policy = DMARCPolicy(record='v=DMARC1; p=none;', domain='example.com')
        self.assertIsInstance(policy.dmarc, DMARC)
        self.assertIsInstance(policy.policy, Policy)
        self.assertIsNone(policy.result)
    
    def test_verify_pass(self):
        policy = DMARCPolicy(record='v=DMARC1; p=none;', domain='example.com')
        policy.verify(spf=SPF(domain='news.example.com', result=SPF_PASS))
        policy.verify(dkim=DKIM(domain='example.com', result=DKIM_PASS))
        policy.verify(auth_results=[SPF('news.example.com', SPF_FAIL), DKIM('example.com', DKIM_PASS)])
        self.assertIsInstance(policy.result, Result)
    
    def test_verify_none(self):
        policy = DMARCPolicy(record='v=DMARC1; p=none;', domain='example.com')
        with self.assertRaises(PolicyNoneError) as cm:
            policy.verify()
        self.assertEqual("Policy verification failed. Disposition type 'none'.", str(cm.exception))
        self.assertIsInstance(policy.result, Result)
    
    def test_verify_reject(self):
        policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
        with self.assertRaises(PolicyRejectError) as cm:
            policy.verify()
        self.assertEqual("Policy verification failed. Disposition type 'reject'.", str(cm.exception))
        self.assertIsInstance(policy.result, Result)
    
    def test_verify_quarantine(self):
        policy = DMARCPolicy(record='v=DMARC1; p=quarantine;', domain='example.com')
        with self.assertRaises(PolicyQuarantineError) as cm:
            policy.verify()
        self.assertEqual("Policy verification failed. Disposition type 'quarantine'.", str(cm.exception))
        self.assertIsInstance(policy.result, Result)
    
    def test_isaligned_spf(self):
        policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
        self.assertTrue(policy.isaligned(SPF('news.example.com', SPF_PASS)))
        self.assertFalse(policy.isaligned(SPF('news.example.com', SPF_FAIL)))
    
    def test_isaligned_dkim(self):
        policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
        self.assertTrue(policy.isaligned(DKIM('news.example.com', DKIM_PASS)))
        self.assertFalse(policy.isaligned(DKIM('news.example.com', DKIM_FAIL)))
    
    def test_isaligned_value_invalid(self):
        policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
        with self.assertRaises(ValueError) as cm:
            policy.isaligned(None)
        self.assertEqual("invalid authentication result 'None'", str(cm.exception))
    
    def test_report(self):
        policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
        policy.verify(auth_results=[SPFAuthResult('news.example.com', SPF_FAIL), DKIMAuthResult('example.com', DKIM_PASS)])
        report = policy.get_report()
        self.assertIsInstance(report, Report)
        self.assertIsNone(report.version)
        self.assertIsNone(report.report_metadata)
        self.assertIsInstance(report.policy_published, PolicyPublished)
        self.assertTrue(all(isinstance(record, Record) for record in report.record))
    
    def test_report_as_dict(self):
        expected = {
            'policy_published': {'domain': 'example.com', 'p': 'reject', 'adkim': 'r', 'aspf': 'r', 'pct': 100},
            'record': [
                {
                    'row': {
                        'count': 1,
                        'policy_evaluated': {'disposition': 'none', 'dkim': 'pass', 'spf': 'fail'}
                    },
                    'identifiers': {'header_from': 'example.com'},
                    'auth_results': {
                        'dkim': [{'domain': 'example.com', 'result': 'pass'}],
                        'spf': [{'domain': 'news.example.com', 'result': 'fail'}]
                    }
                }
            ]
        }
        policy = DMARCPolicy(record='v=DMARC1; p=reject;', domain='example.com')
        policy.verify(auth_results=[SPFAuthResult('news.example.com', SPF_FAIL), DKIMAuthResult('example.com', DKIM_PASS)])
        self.assertEqual(expected, policy.get_report().as_dict())
