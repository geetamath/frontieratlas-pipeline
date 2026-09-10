"""Anti-Bot & Stealth Crawler Engine for Cloudflare / Datadome Protected Endpoints."""

import asyncio
import random
from typing import Dict, List, Optional
import aiohttp


class AntiBotHeaders:
    """Rotates realistic browser fingerprints and HTTP headers."""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15"
    ]

    ACCEPT_LANGUAGES = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9,en-US;q=0.8",
        "en-US,en;q=0.9,fr;q=0.8"
    ]

    @classmethod
    def get_stealth_headers(cls, referer: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "User-Agent": random.choice(cls.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(cls.ACCEPT_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"'
        }
        if referer:
            headers["Referer"] = referer
        return headers


class StealthAsyncSession:
    """
    High-concurrency resilient async crawler session with anti-bot measures:
    - Semaphore-governed concurrency limiting
    - Randomized request delays (politeness policy)
    - Browser header cycling
    - TLS & TCP connection reuse
    """

    def __init__(self, max_concurrent: int = 15, timeout_seconds: int = 20):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=50,
            ttl_dns_cache=300,
            enable_cleanup_closed=True,
            ssl=False  # Allows flexible scraping across older legacy or CDN servers
        )
        self._session = aiohttp.ClientSession(connector=connector, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session and not self._session.closed:
            await self._session.close()

    async def fetch(self, url: str, headers: Optional[Dict[str, str]] = None, delay_range: tuple = (0.1, 0.4)) -> Optional[str]:
        """Fetch URL asynchronously with concurrency control and jittered delay."""
        async with self.semaphore:
            # Politeness delay
            await asyncio.sleep(random.uniform(*delay_range))
            req_headers = headers or AntiBotHeaders.get_stealth_headers()

            try:
                async with self._session.get(url, headers=req_headers) as response:
                    if response.status == 200:
                        return await response.text()
                    elif response.status == 429:
                        # Backoff and retry once
                        await asyncio.sleep(2.0 + random.random())
                        async with self._session.get(url, headers=req_headers) as retry_resp:
                            if retry_resp.status == 200:
                                return await retry_resp.text()
            except Exception:
                return None
        return None
