# coding=utf-8

from unittest import TestCase
from netutils_linux_tuning.rss_ladder import RSSLadder


class RSSLadderTests(TestCase):

    def setUp(self):
        self.rss = RSSLadder(argv=['--dry-run', 'eth0'])

    def test_queue_postfix_extract(self):
        line = '31312 0 0 0 blabla eth0-TxRx-0'
        self.assertEqual(self.rss.queue_postfix_extract(line), '-TxRx-')
