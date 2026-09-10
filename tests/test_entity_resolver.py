"""Tests for Deterministic Entity Resolver."""

import unittest
from src.entity_resolver.resolver import EntityResolver


class TestEntityResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = EntityResolver()

    def test_exact_resolution(self):
        canonical, score, method = self.resolver.resolve("OpenAI")
        self.assertEqual(canonical, "OpenAI")
        self.assertEqual(score, 1.0)
        self.assertEqual(method, "ExactSeedMatch")

    def test_suffix_stripping(self):
        canonical, score, method = self.resolver.resolve("OpenAI, Inc.")
        self.assertEqual(canonical, "OpenAI")

        canonical, score, method = self.resolver.resolve("Open AI")
        self.assertEqual(canonical, "OpenAI")

        canonical, score, method = self.resolver.resolve("Anthropic PBC")
        self.assertEqual(canonical, "Anthropic")

    def test_alias_resolution(self):
        canonical, score, method = self.resolver.resolve("Anysphere Inc.")
        self.assertEqual(canonical, "Cursor")

        canonical, score, method = self.resolver.resolve("Cursor AI")
        self.assertEqual(canonical, "Cursor")

    def test_unknown_entity_rule_cleaned(self):
        canonical, score, method = self.resolver.resolve("Acme Autonomous Systems LLC")
        self.assertEqual(canonical, "Acme Autonomous")
        self.assertEqual(method, "DeterministicRuleCleaned")

    def test_audit_logging(self):
        self.resolver.resolve("OpenAI, Inc.", source="YC")
        logs = self.resolver.get_audit_logs()
        self.assertTrue(len(logs) > 0)
        last_log = logs[-1]
        self.assertEqual(last_log.rawName, "OpenAI, Inc.")
        self.assertEqual(last_log.canonicalName, "OpenAI")
        self.assertEqual(last_log.source, "YC")


if __name__ == "__main__":
    unittest.main()
