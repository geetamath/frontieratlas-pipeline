"""Tests for Intelligent Chunker and Retry Backoff."""

import unittest
from src.llm.chunker import IntelligentChunker
from src.llm.retry_handler import RetryConfig


class TestChunkerAndLLM(unittest.TestCase):
    def test_clean_html_strips_scripts_and_styles(self):
        chunker = IntelligentChunker()
        html = """
        <html>
            <head><style>.ad { color: red; }</style></head>
            <body>
                <script>alert("bad");</script>
                <h1>Important Title</h1>
                <p>This is primary content.</p>
                <div class="cookie-banner">Accept all cookies</div>
            </body>
        </html>
        """
        cleaned = chunker.clean_html(html)
        self.assertIn("Important Title", cleaned)
        self.assertIn("This is primary content", cleaned)
        self.assertNotIn("alert", cleaned)
        self.assertNotIn(".ad {", cleaned)
        self.assertNotIn("Accept all cookies", cleaned)

    def test_chunking_prevents_overflow(self):
        chunker = IntelligentChunker(max_tokens=50, chars_per_token=4.0)
        huge_text = "Headline: AI Revolution.\n\n" + ("Lorem ipsum dolor sit amet. " * 50) + "\n\nConclusion: The future is bright."
        truncated = chunker.chunk_and_truncate(huge_text)
        self.assertLessEqual(len(truncated), 300)
        self.assertIn("Headline: AI Revolution", truncated)
        self.assertIn("truncated", truncated)

    def test_retry_config_backoff(self):
        cfg = RetryConfig(base_delay=1.0, max_delay=16.0, exponential_factor=2.0, jitter=False)
        self.assertEqual(cfg.compute_delay(0), 1.0)
        self.assertEqual(cfg.compute_delay(1), 2.0)
        self.assertEqual(cfg.compute_delay(2), 4.0)
        self.assertEqual(cfg.compute_delay(5), 16.0)  # Capped at max_delay


if __name__ == "__main__":
    unittest.main()
