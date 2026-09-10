"""High-Fidelity Signal Crawler for 5 AI News Sources and 5 AI Job Boards (24-Hour Freshness)."""

import json
import logging
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

from src.models.schemas import NewsEntity, NewsContent, JobEntity, JobContent, SourceInfo
from src.entity_resolver.resolver import EntityResolver
from src.llm.chunker import IntelligentChunker

logger = logging.getLogger("SignalCrawler")


class DateNormalizer:
    """Parses and normalizes arbitrary date representations into UTC ISO-8601 timestamps."""

    RELATIVE_PATTERNS = [
        (r"(\d+)\s*(?:sec|second)s?\s*ago", lambda m: timedelta(seconds=int(m.group(1)))),
        (r"(\d+)\s*(?:min|minute)s?\s*ago", lambda m: timedelta(minutes=int(m.group(1)))),
        (r"(\d+)\s*(?:hour|hr)s?\s*ago", lambda m: timedelta(hours=int(m.group(1)))),
        (r"(\d+)\s*day?s?\s*ago", lambda m: timedelta(days=int(m.group(1)))),
        (r"yesterday", lambda m: timedelta(days=1)),
        (r"just now", lambda m: timedelta(seconds=10)),
    ]

    @classmethod
    def parse_to_iso(cls, raw_date: Optional[str], reference_time: Optional[datetime] = None) -> Tuple[Optional[str], Optional[datetime]]:
        """
        Normalize date string into (iso_str, datetime_obj).
        Handles relative dates, RFC2822, ISO strings, and unix timestamps.
        """
        now = reference_time or datetime.now(timezone.utc)
        if not raw_date:
            return None, None

        cleaned = raw_date.strip().lower()

        # 1. Unix timestamp
        if cleaned.isdigit() and len(cleaned) in (10, 13):
            ts = int(cleaned) if len(cleaned) == 10 else int(cleaned) / 1000.0
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return dt.isoformat(), dt

        # 2. Relative dates ("2 hours ago", "yesterday", etc.)
        for pattern, delta_fn in cls.RELATIVE_PATTERNS:
            match = re.search(pattern, cleaned)
            if match:
                dt = now - delta_fn(match)
                return dt.isoformat(), dt

        # 3. Standard dateutil parsing
        try:
            from dateutil import parser
            dt = parser.parse(raw_date)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.isoformat(), dt
        except Exception:
            return None, None

    @classmethod
    def is_within_24_hours(cls, dt: Optional[datetime], reference_time: Optional[datetime] = None) -> bool:
        """Verify strict 24-hour freshness."""
        if not dt:
            return False
        now = reference_time or datetime.now(timezone.utc)
        age = now - dt
        return timedelta(seconds=0) <= age <= timedelta(hours=24, minutes=5)


class SignalCrawler:
    """Monitors 5 AI news sources and 5 AI job boards with strict 24-hour freshness enforcement."""

    def __init__(self, resolver: Optional[EntityResolver] = None):
        self.resolver = resolver or EntityResolver()
        self.chunker = IntelligentChunker()

    def scrape_all_signals(self) -> Tuple[List[NewsEntity], List[JobEntity]]:
        """Ingest fresh news and fresh jobs from all 10 sources."""
        logger.info("Ingesting 24-hour fresh signals...")
        news = self.scrape_news_sources()
        jobs = self.scrape_job_boards()
        return news, jobs

    # =========================================================================
    # Phase II.A: 5 Distinct AI News Sources
    # =========================================================================
    def scrape_news_sources(self) -> List[NewsEntity]:
        news_items: List[NewsEntity] = []
        now = datetime.now(timezone.utc)

        # 1. TechCrunch AI
        news_items.extend(self._scrape_rss_feed(
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "TechCrunch AI",
            now
        ))

        # 2. Ars Technica
        news_items.extend(self._scrape_rss_feed(
            "https://feeds.arstechnica.com/arstechnica/index",
            "Ars Technica AI",
            now
        ))

        # 3. Hacker News AI Stories (Algolia API)
        news_items.extend(self._scrape_hn_ai(now))

        # 4. Hugging Face Daily Papers News
        news_items.extend(self._scrape_hf_daily(now))

        # 5. MIT Technology Review / Techmeme AI Feed
        news_items.extend(self._scrape_rss_feed(
            "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
            "The Verge AI",
            now
        ))

        logger.info(f"Total 24-hour fresh news items collected: {len(news_items)}")
        return news_items

    def _scrape_rss_feed(self, feed_url: str, source_name: str, now: datetime) -> List[NewsEntity]:
        items = []
        try:
            req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                xml_data = resp.read()
                root = ET.fromstring(xml_data)

                # Support standard RSS <item> and Atom <entry>
                entries = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")

                for e in entries:
                    title_el = e.find("title") or e.find("{http://www.w3.org/2005/Atom}title")
                    title = title_el.text.strip() if title_el is not None and title_el.text else ""

                    link_el = e.find("link") or e.find("{http://www.w3.org/2005/Atom}link")
                    url = link_el.text.strip() if link_el is not None and link_el.text else ""
                    if not url and link_el is not None:
                        url = link_el.attrib.get("href", "")

                    pub_el = e.find("pubDate") or e.find("{http://www.w3.org/2005/Atom}published") or e.find("{http://www.w3.org/2005/Atom}updated")
                    raw_pub = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

                    iso_str, dt = DateNormalizer.parse_to_iso(raw_pub, reference_time=now)

                    # Freshness check: published within 24 hours
                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        desc_el = e.find("description") or e.find("{http://www.w3.org/2005/Atom}summary")
                        desc = self.chunker.clean_html(desc_el.text) if desc_el is not None and desc_el.text else title

                        entity = NewsEntity(
                            schemaVersion="1.0",
                            recordType="NEWS",
                            source=SourceInfo(name=source_name, url=url or feed_url),
                            content=NewsContent(
                                title=title,
                                published_date=iso_str,
                                summary=desc[:300],
                                full_text=desc
                            ),
                            collectedAt=now.isoformat()
                        )
                        items.append(entity)
        except Exception as exc:
            logger.warning(f"Error scraping news feed {source_name}: {exc}")

        return items

    def _scrape_hn_ai(self, now: datetime) -> List[NewsEntity]:
        items = []
        one_day_ago = int((now - timedelta(hours=24)).timestamp())
        url = f"https://hn.algolia.com/api/v1/search_by_date?tags=story&query=AI&numericFilters=created_at_i>{one_day_ago}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for h in data.get("hits", []):
                    title = h.get("title")
                    story_url = h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}"
                    created_at = h.get("created_at")

                    iso_str, dt = DateNormalizer.parse_to_iso(created_at, reference_time=now)
                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        items.append(
                            NewsEntity(
                                schemaVersion="1.0",
                                recordType="NEWS",
                                source=SourceInfo(name="Hacker News AI", url=story_url),
                                content=NewsContent(
                                    title=title,
                                    published_date=iso_str,
                                    summary=f"Hacker News AI signal with {h.get('points', 0)} points and {h.get('num_comments', 0)} comments.",
                                    full_text=title
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping Hacker News AI: {exc}")

        return items

    def _scrape_hf_daily(self, now: datetime) -> List[NewsEntity]:
        items = []
        url = "https://huggingface.co/api/daily_papers"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for paper in data[:15]:
                    title = paper.get("title") or (paper.get("paper", {}).get("title"))
                    pub_str = paper.get("publishedAt") or (paper.get("paper", {}).get("publishedAt"))
                    pid = paper.get("paper", {}).get("id") or ""
                    url = f"https://huggingface.co/papers/{pid}" if pid else "https://huggingface.co/papers"
                    summary = paper.get("summary") or paper.get("paper", {}).get("summary") or title

                    iso_str, dt = DateNormalizer.parse_to_iso(pub_str, reference_time=now)
                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        items.append(
                            NewsEntity(
                                schemaVersion="1.0",
                                recordType="NEWS",
                                source=SourceInfo(name="Hugging Face Daily Papers", url=url),
                                content=NewsContent(
                                    title=title,
                                    published_date=iso_str,
                                    summary=summary[:350],
                                    full_text=summary
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping HF Daily Papers: {exc}")

        return items

    # =========================================================================
    # Phase II.B: 5 Distinct AI Job Boards
    # =========================================================================
    def scrape_job_boards(self) -> List[JobEntity]:
        jobs: List[JobEntity] = []
        now = datetime.now(timezone.utc)

        # 1. RemoteOK API
        jobs.extend(self._scrape_remoteok(now))

        # 2. Remotive API
        jobs.extend(self._scrape_remotive(now))

        # 3. WeWorkRemotely RSS
        jobs.extend(self._scrape_wwr(now))

        # 4. Jobspresso RSS
        jobs.extend(self._scrape_jobspresso(now))

        # 5. Hacker News Who's Hiring (Algolia)
        jobs.extend(self._scrape_hn_hiring(now))

        logger.info(f"Total 24-hour fresh jobs collected: {len(jobs)}")
        return jobs

    def _scrape_remoteok(self, now: datetime) -> List[JobEntity]:
        jobs = []
        url = "https://remoteok.com/api?tag=ai"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for item in data:
                    if not isinstance(item, dict) or not item.get("company"):
                        continue

                    raw_company = item.get("company")
                    canonical_company, _, _ = self.resolver.resolve(raw_company, source="RemoteOK")

                    date_str = item.get("date")
                    iso_str, dt = DateNormalizer.parse_to_iso(date_str, reference_time=now)

                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        job_url = item.get("url") or f"https://remoteok.com/remote-jobs/{item.get('id')}"
                        position = item.get("position", "AI Engineer")

                        # Categorize role family
                        pos_lower = position.lower()
                        if "data" in pos_lower or "analytics" in pos_lower:
                            family = "Data Science"
                        elif "product" in pos_lower:
                            family = "Product"
                        elif "research" in pos_lower:
                            family = "Research"
                        else:
                            family = "Engineering"

                        jobs.append(
                            JobEntity(
                                schemaVersion="1.0",
                                recordType="JOB",
                                source=SourceInfo(name="RemoteOK", url=job_url),
                                content=JobContent(
                                    company=canonical_company,
                                    date=iso_str,
                                    is_remote=True,
                                    role_family=family
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping RemoteOK: {exc}")

        return jobs

    def _scrape_remotive(self, now: datetime) -> List[JobEntity]:
        jobs = []
        url = "https://remotive.com/api/remote-jobs?category=software-dev&limit=40"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for j in data.get("jobs", []):
                    raw_company = j.get("company_name", "Tech Startup")
                    canonical_company, _, _ = self.resolver.resolve(raw_company, source="Remotive")

                    pub_str = j.get("publication_date")
                    iso_str, dt = DateNormalizer.parse_to_iso(pub_str, reference_time=now)

                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        jobs.append(
                            JobEntity(
                                schemaVersion="1.0",
                                recordType="JOB",
                                source=SourceInfo(name="Remotive", url=j.get("url", "https://remotive.com")),
                                content=JobContent(
                                    company=canonical_company,
                                    date=iso_str,
                                    is_remote=True,
                                    role_family="Engineering"
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping Remotive: {exc}")

        return jobs

    def _scrape_wwr(self, now: datetime) -> List[JobEntity]:
        jobs = []
        url = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall(".//item"):
                    title = item.find("title").text if item.find("title") is not None else ""
                    # Title format is often: "Company: Job Title"
                    company = title.split(":")[0].strip() if ":" in title else "Remote Tech"
                    canonical_company, _, _ = self.resolver.resolve(company, source="WeWorkRemotely")

                    link = item.find("link").text if item.find("link") is not None else "https://weworkremotely.com"
                    pub = item.find("pubDate").text if item.find("pubDate") is not None else ""

                    iso_str, dt = DateNormalizer.parse_to_iso(pub, reference_time=now)
                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        jobs.append(
                            JobEntity(
                                schemaVersion="1.0",
                                recordType="JOB",
                                source=SourceInfo(name="WeWorkRemotely", url=link),
                                content=JobContent(
                                    company=canonical_company,
                                    date=iso_str,
                                    is_remote=True,
                                    role_family="Engineering"
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping WeWorkRemotely: {exc}")

        return jobs

    def _scrape_jobspresso(self, now: datetime) -> List[JobEntity]:
        jobs = []
        url = "https://jobspresso.co/feed/"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall(".//item"):
                    title = item.find("title").text if item.find("title") is not None else ""
                    company = title.split(" at ")[-1].strip() if " at " in title else "AI Labs"
                    canonical_company, _, _ = self.resolver.resolve(company, source="Jobspresso")

                    link = item.find("link").text if item.find("link") is not None else "https://jobspresso.co"
                    pub = item.find("pubDate").text if item.find("pubDate") is not None else ""

                    iso_str, dt = DateNormalizer.parse_to_iso(pub, reference_time=now)
                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        jobs.append(
                            JobEntity(
                                schemaVersion="1.0",
                                recordType="JOB",
                                source=SourceInfo(name="Jobspresso", url=link),
                                content=JobContent(
                                    company=canonical_company,
                                    date=iso_str,
                                    is_remote=True,
                                    role_family="Engineering"
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping Jobspresso: {exc}")

        return jobs

    def _scrape_hn_hiring(self, now: datetime) -> List[JobEntity]:
        jobs = []
        one_day_ago = int((now - timedelta(hours=24)).timestamp())
        url = f"https://hn.algolia.com/api/v1/search_by_date?tags=comment&query=hiring+AI&numericFilters=created_at_i>{one_day_ago}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for c in data.get("hits", []):
                    comment_text = c.get("comment_text", "")
                    clean_text = self.chunker.clean_html(comment_text)

                    # Extract company from first line (e.g., "Company Name | Senior AI Engineer | REMOTE")
                    first_line = clean_text.splitlines()[0] if clean_text.splitlines() else ""
                    raw_company = first_line.split("|")[0].strip() if "|" in first_line else "AI Venture"
                    canonical_company, _, _ = self.resolver.resolve(raw_company, source="HN Who is Hiring")

                    created_at = c.get("created_at")
                    iso_str, dt = DateNormalizer.parse_to_iso(created_at, reference_time=now)

                    if dt and DateNormalizer.is_within_24_hours(dt, now):
                        jobs.append(
                            JobEntity(
                                schemaVersion="1.0",
                                recordType="JOB",
                                source=SourceInfo(
                                    name="Hacker News Hiring",
                                    url=f"https://news.ycombinator.com/item?id={c.get('objectID')}"
                                ),
                                content=JobContent(
                                    company=canonical_company,
                                    date=iso_str,
                                    is_remote=True,
                                    role_family="Engineering"
                                ),
                                collectedAt=now.isoformat()
                            )
                        )
        except Exception as exc:
            logger.warning(f"Error scraping HN Hiring: {exc}")

        return jobs
