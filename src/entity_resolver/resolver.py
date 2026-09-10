"""Deterministic Entity Resolution Engine for Startups and Products."""

import re
import unicodedata
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from src.models.schemas import EntityMappingLog
from src.entity_resolver.seed_data import KNOWN_AI_STARTUPS


class EntityResolver:
    """Canonicalizes startup and product names deterministically."""

    LEGAL_SUFFIXES = [
        r"\binc\.?\b",
        r"\bllc\.?\b",
        r"\bl\.l\.c\.?\b",
        r"\bcorp\.?\b",
        r"\bcorporation\b",
        r"\bpbc\b",
        r"\bp\.b\.c\.?\b",
        r"\bsas\b",
        r"\bgmbh\b",
        r"\bltd\.?\b",
        r"\blimited\b",
        r"\bb\.v\.?\b",
        r"\bse\b",
        r"\bco\.?\b",
        r"\btechnologies\b",
        r"\btechnology\b",
        r"\blabs\b",
        r"\blaboratory\b",
        r"\blaboratories\b",
        r"\bsystems\b",
        r"\bplatform\b",
        r"\bcompany\b"
    ]

    def __init__(self, seed_data: Optional[Dict] = None):
        self.seed_data = seed_data or KNOWN_AI_STARTUPS
        self._build_alias_index()
        self.mapping_logs: List[EntityMappingLog] = []

    def _build_alias_index(self):
        """Construct fast normalized lookup tables for exact and alias matches."""
        self.normalized_lookup: Dict[str, str] = {}
        for canonical, info in self.seed_data.items():
            norm_canonical = self.normalize_text(canonical)
            self.normalized_lookup[norm_canonical] = canonical
            for alias in info.get("aliases", []):
                norm_alias = self.normalize_text(alias)
                self.normalized_lookup[norm_alias] = canonical

    @classmethod
    def normalize_text(cls, text: str) -> str:
        """Strip accents, lowercase, clean punctuation, and collapse whitespace."""
        if not text:
            return ""
        # Unicode NFKD decomposition to strip diacritics
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
        text = text.lower()
        # Remove punctuation except alphanumeric and space
        text = re.sub(r"[^\w\s]", " ", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def strip_legal_suffixes(cls, text: str) -> str:
        """Remove corporate suffixes like Inc, LLC, Corp, Technologies, Labs."""
        cleaned = text
        for suffix_pattern in cls.LEGAL_SUFFIXES:
            cleaned = re.sub(suffix_pattern, "", cleaned, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", cleaned).strip()

    def resolve(self, raw_name: str, source: str = "general") -> Tuple[str, float, str]:
        """
        Resolve a raw entity name into its canonical form.
        Returns: (canonical_name, confidence_score, method)
        """
        if not raw_name or not raw_name.strip():
            return "Unknown", 0.0, "EmptyInput"

        trimmed = raw_name.strip()
        norm_raw = self.normalize_text(trimmed)

        # 1. Direct match in normalized alias index
        if norm_raw in self.normalized_lookup:
            canonical = self.normalized_lookup[norm_raw]
            score = 1.0
            method = "ExactSeedMatch"
            self._log(trimmed, canonical, source, score, method)
            return canonical, score, method

        # 2. Match after stripping legal suffixes
        stripped = self.strip_legal_suffixes(norm_raw)
        if stripped in self.normalized_lookup:
            canonical = self.normalized_lookup[stripped]
            score = 0.98
            method = "SuffixStrippedSeedMatch"
            self._log(trimmed, canonical, source, score, method)
            return canonical, score, method

        # Also check if stripping suffixes matches canonical name directly
        for canonical, info in self.seed_data.items():
            norm_can_stripped = self.strip_legal_suffixes(self.normalize_text(canonical))
            if stripped == norm_can_stripped and len(stripped) > 2:
                score = 0.95
                method = "CanonicalStrippedMatch"
                self._log(trimmed, canonical, source, score, method)
                return canonical, score, method

        # 3. Fuzzy Levenshtein/Jaro-Winkler via SequenceMatcher against all known aliases
        best_match = None
        best_score = 0.0
        best_canonical = None

        for alias_norm, canonical in self.normalized_lookup.items():
            ratio = SequenceMatcher(None, norm_raw, alias_norm).ratio()
            # If length is significantly different, penalize
            len_ratio = min(len(norm_raw), len(alias_norm)) / max(len(norm_raw), len(alias_norm))
            adjusted_score = ratio * (0.8 + 0.2 * len_ratio)

            if adjusted_score > best_score:
                best_score = adjusted_score
                best_match = alias_norm
                best_canonical = canonical

        # Strict fuzzy acceptance threshold >= 0.86
        if best_canonical and best_score >= 0.86:
            method = "FuzzyRatioMatch"
            self._log(trimmed, best_canonical, source, best_score, method)
            return best_canonical, best_score, method

        # 4. Deterministic Rule-based Cleanup (Title casing, suffix removal)
        # If not in seed, create clean canonical version
        cleaned = self.strip_legal_suffixes(trimmed)
        cleaned = re.sub(r"[,;:\-–—\._]+$", "", cleaned).strip()
        # Preserve CamelCase or convert to Title Case
        if not any(c.isupper() for c in cleaned[1:]):
            cleaned = cleaned.title()

        score = 0.80
        method = "DeterministicRuleCleaned"
        self._log(trimmed, cleaned, source, score, method)
        return cleaned, score, method

    def _log(self, raw: str, canonical: str, source: str, score: float, method: str):
        """Append to audit log."""
        self.mapping_logs.append(
            EntityMappingLog(
                rawName=raw,
                canonicalName=canonical,
                source=source,
                confidenceScore=score,
                method=method
            )
        )

    def get_audit_logs(self) -> List[EntityMappingLog]:
        """Return the collected resolution logs."""
        return self.mapping_logs
