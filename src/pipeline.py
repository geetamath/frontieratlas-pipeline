"""Main End-to-End Pipeline Orchestrator for GraphOne / FrontierAtlas Ingestion."""

import argparse
import logging
import sys
import time
from typing import Optional

from src.entity_resolver.resolver import EntityResolver
from src.crawler.startup_scraper import StartupScraper
from src.crawler.product_scraper import ProductScraper
from src.crawler.paper_scraper import PaperScraper
from src.crawler.signal_crawler import SignalCrawler
from src.llm.orchestrator import LLMOrchestrator
from src.exporter import DatasetExporter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Pipeline")


class PipelineRunner:
    """Orchestrates all extraction, normalization, resolution, and export steps."""

    def __init__(
        self,
        target_startups: int = 1000,
        target_products: int = 1000,
        target_papers: int = 1000,
        output_dir: str = "output"
    ):
        self.target_startups = target_startups
        self.target_products = target_products
        self.target_papers = target_papers
        self.output_dir = output_dir

        self.resolver = EntityResolver()
        self.startup_scraper = StartupScraper(resolver=self.resolver)
        self.product_scraper = ProductScraper(resolver=self.resolver)
        self.paper_scraper = PaperScraper()
        self.signal_crawler = SignalCrawler(resolver=self.resolver)
        self.llm_orchestrator = LLMOrchestrator()
        self.exporter = DatasetExporter(output_dir=output_dir)

    def run(self):
        start_time = time.time()
        logger.info("=================================================================")
        logger.info("Starting GraphOne / FrontierAtlas Data Ingestion Pipeline")
        logger.info("=================================================================")

        # 1. Startups (Target: 1,000+)
        logger.info("\n--- Phase I.A: Scraping Startups ---")
        startups = self.startup_scraper.scrape_startups(min_records=self.target_startups)
        logger.info(f"Startups Extracted: {len(startups)}")

        # 2. Products (Target: 1,000+)
        logger.info("\n--- Phase I.B: Scraping AI Products ---")
        products = self.product_scraper.scrape_products(min_records=self.target_products)
        logger.info(f"Products Extracted: {len(products)}")

        # 3. Research Papers (Target: 1,000+)
        logger.info("\n--- Phase I.C: Scraping Research Papers with GitHub Metrics ---")
        papers = self.paper_scraper.scrape_papers(min_records=self.target_papers)
        logger.info(f"Research Papers Extracted: {len(papers)}")

        # 4. Fresh Signals: News and Jobs (Strict 24h Freshness)
        logger.info("\n--- Phase II: Signal Ingestion (24h Fresh News & Jobs) ---")
        news, jobs = self.signal_crawler.scrape_all_signals()
        logger.info(f"Fresh News Articles Extracted: {len(news)}")
        logger.info(f"Fresh Jobs Extracted: {len(jobs)}")

        # 5. Entity Resolution Logs
        mapping_logs = self.resolver.get_audit_logs()
        logger.info(f"\n--- Phase IV: Entity Resolution Logs ---")
        logger.info(f"Total Entity Mappings Logged: {len(mapping_logs)}")

        # 6. Export to Multi-Tab Excel Workbook & CSVs
        logger.info("\n--- Generating Deliverables: Excel Workbook & CSVs ---")
        excel_file = self.exporter.export_all(
            startups=startups,
            products=products,
            papers=papers,
            jobs=jobs,
            news=news,
            mapping_logs=mapping_logs,
            excel_filename="pipeline_output.xlsx"
        )

        elapsed = time.time() - start_time
        logger.info("=================================================================")
        logger.info("Pipeline Execution Summary:")
        logger.info(f"- Startups:            {len(startups):,}")
        logger.info(f"- Products:            {len(products):,}")
        logger.info(f"- Research Papers:     {len(papers):,}")
        logger.info(f"- 24h Fresh Jobs:      {len(jobs):,}")
        logger.info(f"- 24h Fresh News:      {len(news):,}")
        logger.info(f"- Entity Mapping Logs: {len(mapping_logs):,}")
        logger.info(f"- Deliverable Excel:   {excel_file}")
        logger.info(f"- Total Runtime:       {elapsed:.2f} seconds")
        logger.info("=================================================================")
        return {
            "startups": len(startups),
            "products": len(products),
            "papers": len(papers),
            "jobs": len(jobs),
            "news": len(news),
            "mapping_logs": len(mapping_logs),
            "excel_path": excel_file
        }


def main():
    parser = argparse.ArgumentParser(description="GraphOne Ingestion Pipeline")
    parser.add_argument("--startups", type=int, default=1050, help="Target startup count (min 1000)")
    parser.add_argument("--products", type=int, default=1050, help="Target product count (min 1000)")
    parser.add_argument("--papers", type=int, default=1050, help="Target research papers count (min 1000)")
    parser.add_argument("--output-dir", type=str, default="output", help="Output directory")

    args = parser.parse_args()
    runner = PipelineRunner(
        target_startups=args.startups,
        target_products=args.products,
        target_papers=args.papers,
        output_dir=args.output_dir
    )
    runner.run()


if __name__ == "__main__":
    main()
