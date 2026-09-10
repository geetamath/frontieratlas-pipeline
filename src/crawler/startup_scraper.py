"""Massive Bulk Scraper for Startups (1,000+ records) via Y Combinator Directory."""

import json
import logging
import urllib.request
from typing import List, Optional
from datetime import datetime, timezone

from src.models.schemas import StartupEntity, StartupContent, StartupData, SourceInfo
from src.entity_resolver.resolver import EntityResolver

logger = logging.getLogger("StartupScraper")


class StartupScraper:
    """Scrapes structured startup records from Y Combinator's verified directory index."""

    ALGOLIA_APP_ID = "45BWZJ1SGC"
    ALGOLIA_API_KEY = "NzllNTY5MzJiZGM2OTY2ZTQwMDEzOTNhYWZiZGRjODlhYzVkNjBmOGRjNzJiMWM4ZTU0ZDlhYTZjOTJiMjlhMWFuYWx5dGljc1RhZ3M9eWNkYyZyZXN0cmljdEluZGljZXM9WUNDb21wYW55X3Byb2R1Y3Rpb24lMkNZQ0NvbXBhbnlfQnlfTGF1bmNoX0RhdGVfcHJvZHVjdGlvbiZ0YWdGaWx0ZXJzPSU1QiUyMnljZGNfcHVibGljJTIyJTVE"

    def __init__(self, resolver: Optional[EntityResolver] = None):
        self.resolver = resolver or EntityResolver()

    def scrape_startups(self, min_records: int = 1000) -> List[StartupEntity]:
        """Fetch min_records unique startup entities with employee counts and canonical names."""
        logger.info(f"Starting startup extraction (target: {min_records} records)...")
        results: List[StartupEntity] = []
        seen_names = set()

        hits_per_page = 100
        search_terms = ["", "AI", "Software", "Tech", "Data"]

        url = f"https://{self.ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/YCCompany_production/query"
        headers = {
            "x-algolia-application-id": self.ALGOLIA_APP_ID,
            "x-algolia-api-key": self.ALGOLIA_API_KEY,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        for term in search_terms:
            if len(results) >= min_records:
                break

            for page in range(10):  # Algolia allows pages 0-9 per query
                if len(results) >= min_records:
                    break

                payload = json.dumps({
                    "query": term,
                    "hitsPerPage": hits_per_page,
                    "page": page
                }).encode("utf-8")

                try:
                    req = urllib.request.Request(url, data=payload, headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        hits = data.get("hits", [])
                        if not hits:
                            break

                        for h in hits:
                            raw_name = h.get("name")
                            if not raw_name:
                                continue

                            # Resolve canonical name using EntityResolver
                            canonical_name, _, _ = self.resolver.resolve(raw_name, source="Y Combinator")

                            if canonical_name in seen_names:
                                continue
                            seen_names.add(canonical_name)

                            team_size = h.get("team_size")
                            emp_count = int(team_size) if team_size and str(team_size).isdigit() else None

                            slug = h.get("slug") or raw_name.lower().replace(" ", "-")

                            entity = StartupEntity(
                                schemaVersion="1.0",
                                recordType="STARTUP",
                                source=SourceInfo(
                                    name="Y Combinator",
                                    url=f"https://www.ycombinator.com/companies/{slug}"
                                ),
                                content=StartupContent(
                                    entityName=canonical_name,
                                    data=StartupData(employeeCount=emp_count)
                                ),
                                collectedAt=datetime.now(timezone.utc).isoformat()
                            )
                            results.append(entity)

                            if len(results) >= min_records:
                                break

                        logger.info(f"Startups progress ({term or 'all'}): {len(results)}/{min_records}")

                except Exception as e:
                    logger.error(f"Error fetching YC page {page} for term '{term}': {e}")
                    break

        logger.info(f"Successfully collected {len(results)} unique startup records.")
        return results
