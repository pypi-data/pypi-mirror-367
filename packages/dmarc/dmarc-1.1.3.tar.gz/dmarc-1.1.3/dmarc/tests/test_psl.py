import unittest

from dmarc.psl import (
    load,
    get_public_suffix,
    PublicSuffixList,
)
from dmarc import (
    DMARC,
    RECORD_A_RELAXED,
    RECORD_A_STRICT,
)

class TestPublicSuffixList(unittest.TestCase):
    
    def test_get_public_suffix(self):
        self.assertEqual('example.com', get_public_suffix('example.com'))
        self.assertEqual('example.com', get_public_suffix('news.example.com'))
    
    def test_load(self):
        self.assertIsInstance(load(psl_file=None), PublicSuffixList)

class TestDMARC(unittest.TestCase):
    
    def setUp(self):
        self.dmarc = DMARC(PublicSuffixList())
    
    def test_alignment(self):
        self.assertTrue(self.dmarc.check_alignment('news.example.com', 'mailer.example.com', RECORD_A_RELAXED, self.dmarc.publicsuffix))
        self.assertFalse(self.dmarc.check_alignment('example.com', 'mailer.example.com', RECORD_A_STRICT, self.dmarc.publicsuffix))
