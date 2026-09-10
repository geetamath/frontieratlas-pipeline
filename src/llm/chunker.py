"""Intelligent HTML / Text Chunker and Boilerplate Remover to prevent 413 Payload Too Large."""

import re
from typing import List, Optional
from bs4 import BeautifulSoup, Comment


class IntelligentChunker:
    """Cleans raw web payloads and chunks dense semantic content to avoid 413 errors."""

    def __init__(self, max_tokens: int = 3500, chars_per_token: float = 4.0):
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        self.max_chars = int(max_tokens * chars_per_token)

    def clean_html(self, raw_html: str) -> str:
        """Strip boilerplate HTML elements, inline styles, scripts, and non-content tags."""
        if not raw_html:
            return ""

        soup = BeautifulSoup(raw_html, "html.parser")

        # 1. Remove non-content tags
        boilerplate_tags = [
            "script", "style", "svg", "noscript", "header", "footer", "nav",
            "aside", "iframe", "button", "input", "form", "select", "canvas"
        ]
        for tag in soup.find_all(boilerplate_tags):
            tag.decompose()

        # 2. Remove comments
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 3. Remove common boilerplate containers (ad banners, cookie notices, share widgets)
        boilerplate_classes = re.compile(
            r"cookie|banner|advertisement|promo|newsletter|social-share|sidebar|modal|popup",
            re.IGNORECASE
        )
        for bad_div in soup.find_all(attrs={"class": boilerplate_classes}):
            bad_div.decompose()
        for bad_id in soup.find_all(attrs={"id": boilerplate_classes}):
            bad_id.decompose()

        # 4. Extract meaningful text structured with line breaks
        text = soup.get_text(separator="\n")

        # 5. Clean whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines)
        return cleaned_text

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count based on average character-to-token ratio."""
        if not text:
            return 0
        return int(len(text) / self.chars_per_token)

    def chunk_and_truncate(self, content: str, max_tokens: Optional[int] = None) -> str:
        """
        Truncate content to never exceed max_tokens while preserving semantic density.
        Prioritizes headlines, lead paragraphs, and key metadata.
        """
        limit_tokens = max_tokens or self.max_tokens
        limit_chars = int(limit_tokens * self.chars_per_token)

        # If it's HTML, clean it first
        if "<html" in content.lower() or "<body" in content.lower() or "<div" in content.lower():
            text = self.clean_html(content)
        else:
            text = content.strip()

        if len(text) <= limit_chars:
            return text

        # Dense Truncation Strategy:
        # Keep the beginning 70% of allowed budget (lead info/titles)
        # and the ending 30% (conclusions/specs/dates) with a clear truncation marker
        head_chars = int(limit_chars * 0.7)
        tail_chars = limit_chars - head_chars - 100

        head = text[:head_chars].rsplit("\n", 1)[0]
        tail = text[-tail_chars:].split("\n", 1)[-1] if tail_chars > 0 else ""

        truncated = f"{head}\n\n[... content truncated to prevent 413 context window overflow ...]\n\n{tail}"
        return truncated

    def split_into_windows(self, content: str, window_tokens: int = 2048, overlap_tokens: int = 200) -> List[str]:
        """Split very large articles/documents into overlapping semantic windows for Map-Reduce processing."""
        clean_text = self.clean_html(content) if "<" in content else content
        paragraphs = clean_text.split("\n\n")

        windows = []
        current_window = []
        current_len = 0
        window_chars = int(window_tokens * self.chars_per_token)
        overlap_chars = int(overlap_tokens * self.chars_per_token)

        for para in paragraphs:
            para_len = len(para)
            if current_len + para_len > window_chars and current_window:
                windows.append("\n\n".join(current_window))
                # Retain overlap from end of current window
                overlap_accum = []
                overlap_size = 0
                for p in reversed(current_window):
                    if overlap_size + len(p) <= overlap_chars:
                        overlap_accum.insert(0, p)
                        overlap_size += len(p)
                    else:
                        break
                current_window = overlap_accum
                current_len = overlap_size

            current_window.append(para)
            current_len += para_len

        if current_window:
            windows.append("\n\n".join(current_window))

        return windows
