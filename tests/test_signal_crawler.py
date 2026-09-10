"""Tests for SignalCrawler and DateNormalizer."""

import unittest
from datetime import datetime, timezone, timedelta
from src.crawler.signal_crawler import DateNormalizer


class TestSignalCrawler(unittest.TestCase):
    def test_relative_date_normalization(self):
        ref_time = datetime(2026, 9, 10, 18, 0, 0, tzinfo=timezone.utc)

        iso_str, dt = DateNormalizer.parse_to_iso("2 hours ago", reference_time=ref_time)
        self.assertEqual(dt, datetime(2026, 9, 10, 16, 0, 0, tzinfo=timezone.utc))
        self.assertTrue(DateNormalizer.is_within_24_hours(dt, ref_time))

        iso_str, dt = DateNormalizer.parse_to_iso("45 minutes ago", reference_time=ref_time)
        self.assertEqual(dt, datetime(2026, 9, 10, 17, 15, 0, tzinfo=timezone.utc))
        self.assertTrue(DateNormalizer.is_within_24_hours(dt, ref_time))

    def test_rfc2822_date_normalization(self):
        ref_time = datetime(2026, 9, 10, 18, 0, 0, tzinfo=timezone.utc)
        raw = "Thu, 10 Sep 2026 12:00:00 +0000"
        iso_str, dt = DateNormalizer.parse_to_iso(raw, reference_time=ref_time)
        self.assertTrue(DateNormalizer.is_within_24_hours(dt, ref_time))

    def test_expired_date_rejected(self):
        ref_time = datetime(2026, 9, 10, 18, 0, 0, tzinfo=timezone.utc)
        old_time = ref_time - timedelta(days=2)
        self.assertFalse(DateNormalizer.is_within_24_hours(old_time, ref_time))


if __name__ == "__main__":
    unittest.main()
