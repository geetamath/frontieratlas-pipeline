"""Tests for Pydantic Canonical Schemas."""

import unittest
from src.models.schemas import (
    StartupEntity,
    StartupContent,
    StartupData,
    ProductEntity,
    ProductContent,
    PricingModel,
    ResearchPaperEntity,
    ResearchPaperContent,
    JobEntity,
    JobContent,
    NewsEntity,
    NewsContent,
    SourceInfo
)


class TestSchemas(unittest.TestCase):
    def test_startup_schema(self):
        entity = StartupEntity(
            source=SourceInfo(name="Y Combinator", url="https://ycombinator.com/companies/test"),
            content=StartupContent(entityName="Test AI", data=StartupData(employeeCount=50))
        )
        flat = entity.to_flat_dict()
        self.assertEqual(flat["schemaVersion"], "1.0")
        self.assertEqual(flat["recordType"], "STARTUP")
        self.assertEqual(flat["content.entityName"], "Test AI")
        self.assertEqual(flat["content.data.employeeCount"], 50)

    def test_product_schema(self):
        entity = ProductEntity(
            source=SourceInfo(name="FutureTools", url="https://futuretools.io/tools/test"),
            content=ProductContent(startupName="OpenAI", pricingModel=PricingModel.FREEMIUM)
        )
        flat = entity.to_flat_dict()
        self.assertEqual(flat["recordType"], "PRODUCT")
        self.assertEqual(flat["content.pricingModel"], "FREEMIUM")

    def test_research_paper_schema(self):
        entity = ResearchPaperEntity(
            content=ResearchPaperContent(
                title="Attention Is All You Need",
                authors=["Ashish Vaswani", "Noam Shazeer"],
                paper_url="https://arxiv.org/abs/1706.03762",
                github_url="https://github.com/tensorflow/tensor2tensor",
                github_stars=12000,
                published_date="2017-06-12T00:00:00Z"
            )
        )
        flat = entity.to_flat_dict()
        self.assertEqual(flat["recordType"], "RESEARCH_PAPER")
        self.assertEqual(flat["content.github_stars"], 12000)
        self.assertIn("Ashish Vaswani", flat["content.authors"])

    def test_job_schema(self):
        entity = JobEntity(
            source=SourceInfo(name="RemoteOK", url="https://remoteok.com/job/1"),
            content=JobContent(
                company="Anthropic",
                date="2026-09-10T00:00:00Z",
                is_remote=True,
                role_family="Engineering"
            )
        )
        flat = entity.to_flat_dict()
        self.assertEqual(flat["recordType"], "JOB")
        self.assertTrue(flat["content.is_remote"])


if __name__ == "__main__":
    unittest.main()
