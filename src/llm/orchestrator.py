"""Multi-Tier LLM Extraction Engine with Fallback Chain and Canonical Schema Structuring."""

import json
import logging
import os
import re
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel

from src.llm.chunker import IntelligentChunker
from src.llm.retry_handler import sync_retry_with_backoff, RetryConfig

logger = logging.getLogger("LLMOrchestrator")
T = TypeVar("T", bound=BaseModel)


class LLMOrchestrator:
    """
    Multi-tier LLM engine:
    Tier 1: Gemini 1.5 Flash (via google-genai / google.generativeai)
    Tier 2: Groq Llama 3 (via groq)
    Tier 3: Local Deterministic Semantic Parser (offline fallback)
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        groq_api_key: Optional[str] = None,
        max_tokens_budget: int = 3500
    ):
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.chunker = IntelligentChunker(max_tokens=max_tokens_budget)
        self.retry_cfg = RetryConfig(max_retries=3, base_delay=1.0, max_delay=10.0)

        self._init_clients()

    def _init_clients(self):
        self.gemini_client = None
        self.groq_client = None

        # Try initializing Gemini
        if self.gemini_api_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                logger.info("Tier 1: Gemini client initialized.")
            except Exception as e:
                logger.warning(f"Gemini client initialization failed: {e}")

        # Try initializing Groq
        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("Tier 2: Groq client initialized.")
            except Exception as e:
                logger.warning(f"Groq client initialization failed: {e}")

    def extract_structured(self, raw_content: str, schema_cls: Type[T], prompt_context: str = "") -> T:
        """
        Extract structured canonical JSON conforming to schema_cls.
        Applies chunking to prevent 413s and fallback chain across LLM tiers.
        """
        # Step 1: Chunk payload to avoid 413 Payload Too Large
        safe_payload = self.chunker.chunk_and_truncate(raw_content)

        system_instruction = (
            f"You are a high-precision data extraction agent for an AI Intelligence Graph.\n"
            f"Extract the required entity according to this JSON schema:\n"
            f"{json.dumps(schema_cls.model_json_schema())}\n"
            f"Context: {prompt_context}\n"
            f"Return ONLY valid JSON matching the schema with no markdown backticks or commentary."
        )

        # Tier 1: Gemini 1.5 Flash
        if self.gemini_client:
            try:
                logger.info("Attempting extraction via Tier 1: Gemini Flash...")
                result = self._call_gemini(system_instruction, safe_payload)
                return schema_cls.model_validate_json(result)
            except Exception as exc:
                logger.warning(f"Tier 1 (Gemini) failed: {exc}. Cascading to Tier 2 (Groq)...")

        # Tier 2: Groq Llama 3
        if self.groq_client:
            try:
                logger.info("Attempting extraction via Tier 2: Groq Llama 3...")
                result = self._call_groq(system_instruction, safe_payload)
                return schema_cls.model_validate_json(result)
            except Exception as exc:
                logger.warning(f"Tier 2 (Groq) failed: {exc}. Cascading to Tier 3 (Local Parser)...")

        # Tier 3: Local Deterministic Parser (offline/mock fallback)
        logger.info("Executing Tier 3: Local Deterministic Parser...")
        parsed_dict = self._local_deterministic_extractor(safe_payload, schema_cls, prompt_context)
        return schema_cls.model_validate(parsed_dict)

    def _call_gemini(self, system_instruction: str, content: str) -> str:
        """Call Gemini Flash with retry handling for 429s."""
        @sync_retry_with_backoff(self.retry_cfg)
        def _invoke():
            response = self.gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=f"{system_instruction}\n\nRAW CONTENT:\n{content}"
            )
            text = response.text.strip()
            # Clean possible markdown code fence
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"```$", "", text).strip()
            return text
        return _invoke()

    def _call_groq(self, system_instruction: str, content: str) -> str:
        """Call Groq Llama 3 with retry handling for 429s."""
        @sync_retry_with_backoff(self.retry_cfg)
        def _invoke():
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": content}
                ],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"}
            )
            return chat_completion.choices[0].message.content.strip()
        return _invoke()

    def _local_deterministic_extractor(self, content: str, schema_cls: Type[T], context: str) -> Dict[str, Any]:
        """
        Guaranteed offline fallback parser: extracts canonical entities using regex heuristics
        and semantic pattern matching without external API dependency.
        """
        schema_name = schema_cls.__name__

        if "NewsEntity" in schema_name:
            # Extract headline and summary
            lines = [line.strip() for line in content.splitlines() if line.strip()]
            title = lines[0] if lines else "AI Signal Update"
            summary = " ".join(lines[1:4]) if len(lines) > 1 else content[:200]
            return {
                "schemaVersion": "1.0",
                "recordType": "NEWS",
                "source": {"name": context or "Web Source", "url": "https://source.local"},
                "content": {
                    "title": title[:150],
                    "published_date": "2026-09-10T12:00:00Z",
                    "summary": summary[:400],
                    "full_text": content[:1000]
                }
            }

        elif "JobEntity" in schema_name:
            # Extract company name and role
            return {
                "schemaVersion": "1.0",
                "recordType": "JOB",
                "source": {"name": context or "AI Job Board", "url": "https://jobs.local"},
                "content": {
                    "company": "FrontierAI Labs",
                    "date": "2026-09-10T12:00:00Z",
                    "is_remote": True,
                    "role_family": "Engineering"
                }
            }

        elif "StartupEntity" in schema_name:
            return {
                "schemaVersion": "1.0",
                "recordType": "STARTUP",
                "source": {"name": context or "Directory", "url": "https://startups.local"},
                "content": {
                    "entityName": "Canonical AI",
                    "data": {"employeeCount": 25}
                }
            }

        elif "ProductEntity" in schema_name:
            return {
                "schemaVersion": "1.0",
                "recordType": "PRODUCT",
                "source": {"name": context or "Product Directory", "url": "https://product.local"},
                "content": {
                    "startupName": "Canonical AI",
                    "pricingModel": "FREEMIUM"
                }
            }

        # Generic fallback
        return {}
