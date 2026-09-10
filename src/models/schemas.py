"""Canonical Pydantic Schemas for FrontierAtlas / GraphOne Ingestion Pipeline."""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class PricingModel(str, Enum):
    FREE = "FREE"
    FREEMIUM = "FREEMIUM"
    PAID = "PAID"
    ENTERPRISE = "ENTERPRISE"


class SourceInfo(BaseModel):
    name: str = Field(..., description="Name of the source site")
    url: str = Field(..., description="Original source URL")


# ==========================================
# 1. Startup Entity
# ==========================================
class StartupData(BaseModel):
    employeeCount: Optional[int] = Field(None, description="Number of employees (if available)")


class StartupContent(BaseModel):
    entityName: str = Field(..., description="Canonical startup name")
    data: StartupData = Field(default_factory=StartupData)


class StartupEntity(BaseModel):
    schemaVersion: str = Field("1.0", description="Versioning for the schema")
    recordType: str = Field("STARTUP", description="Fixed to 'STARTUP'")
    source: SourceInfo
    content: StartupContent
    collectedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 collection timestamp"
    )

    def to_flat_dict(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType,
            "source.name": self.source.name,
            "source.url": self.source.url,
            "content.entityName": self.content.entityName,
            "content.data.employeeCount": self.content.data.employeeCount if self.content.data.employeeCount is not None else "",
            "collectedAt": self.collectedAt
        }


# ==========================================
# 2. Product Entity
# ==========================================
class ProductContent(BaseModel):
    startupName: str = Field(..., description="Canonical startup name")
    pricingModel: PricingModel = Field(..., description="FREE, FREEMIUM, PAID, ENTERPRISE")


class ProductEntity(BaseModel):
    schemaVersion: str = Field("1.0", description="Versioning for the schema")
    recordType: str = Field("PRODUCT", description="Fixed to 'PRODUCT'")
    source: SourceInfo
    content: ProductContent
    collectedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 collection timestamp"
    )

    def to_flat_dict(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType,
            "source.name": self.source.name,
            "source.url": self.source.url,
            "content.startupName": self.content.startupName,
            "content.pricingModel": self.content.pricingModel.value if hasattr(self.content.pricingModel, "value") else str(self.content.pricingModel),
            "collectedAt": self.collectedAt
        }


# ==========================================
# 3. Research Paper Entity
# ==========================================
class ResearchPaperContent(BaseModel):
    title: str = Field(..., description="Title of the research paper")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    paper_url: str = Field(..., description="Link to the Arxiv/PDF page")
    github_url: Optional[str] = Field(None, description="Link to the associated code repository (if any)")
    github_stars: Optional[int] = Field(0, description="Current number of stars on the GitHub repository")
    published_date: str = Field(..., description="ISO-8601 publication date")


class ResearchPaperEntity(BaseModel):
    schemaVersion: str = Field("1.0", description="Versioning for the schema")
    recordType: str = Field("RESEARCH_PAPER", description="Fixed to 'RESEARCH_PAPER'")
    content: ResearchPaperContent
    collectedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 collection timestamp"
    )

    def to_flat_dict(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType,
            "content.title": self.content.title,
            "content.authors": ", ".join(self.content.authors),
            "content.paper_url": self.content.paper_url,
            "content.github_url": self.content.github_url or "",
            "content.github_stars": self.content.github_stars if self.content.github_stars is not None else 0,
            "content.published_date": self.content.published_date,
            "collectedAt": self.collectedAt
        }


# ==========================================
# 4. Job Entity
# ==========================================
class JobContent(BaseModel):
    company: str = Field(..., description="Canonical company name")
    date: str = Field(..., description="ISO-8601 publication date")
    is_remote: bool = Field(True, description="Remote eligibility")
    role_family: str = Field(..., description="Functional category (e.g., 'Engineering', 'AI/ML')")


class JobEntity(BaseModel):
    schemaVersion: str = Field("1.0", description="Versioning for the schema")
    recordType: str = Field("JOB", description="Fixed to 'JOB'")
    source: SourceInfo
    content: JobContent
    collectedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 collection timestamp"
    )

    def to_flat_dict(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType,
            "source.name": self.source.name,
            "source.url": self.source.url,
            "content.company": self.content.company,
            "content.date": self.content.date,
            "content.is_remote": self.content.is_remote,
            "content.role_family": self.content.role_family,
            "collectedAt": self.collectedAt
        }


# ==========================================
# 5. News Entity
# ==========================================
class NewsContent(BaseModel):
    title: str = Field(..., description="Article headline")
    published_date: str = Field(..., description="ISO-8601 publication date")
    summary: str = Field(..., description="Extracted summary or key signal")
    full_text: Optional[str] = Field(None, description="Full extracted text content")


class NewsEntity(BaseModel):
    schemaVersion: str = Field("1.0", description="Versioning for the schema")
    recordType: str = Field("NEWS", description="Fixed to 'NEWS'")
    source: SourceInfo
    content: NewsContent
    collectedAt: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 collection timestamp"
    )

    def to_flat_dict(self) -> dict:
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType,
            "source.name": self.source.name,
            "source.url": self.source.url,
            "content.title": self.content.title,
            "content.published_date": self.content.published_date,
            "content.summary": self.content.summary,
            "content.full_text": self.content.full_text or "",
            "collectedAt": self.collectedAt
        }


# ==========================================
# 6. Entity Mapping Log
# ==========================================
class EntityMappingLog(BaseModel):
    rawName: str = Field(..., description="Raw string encountered in source")
    canonicalName: str = Field(..., description="Canonical resolved entity name")
    source: str = Field(..., description="Source origin or domain")
    confidenceScore: float = Field(..., ge=0.0, le=1.0, description="Match confidence")
    method: str = Field(..., description="Exact, SeedSynonym, FuzzyLevenshtein, RuleCleaned")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Resolution timestamp"
    )

    def to_flat_dict(self) -> dict:
        return {
            "rawName": self.rawName,
            "canonicalName": self.canonicalName,
            "source": self.source,
            "confidenceScore": round(self.confidenceScore, 4),
            "method": self.method,
            "timestamp": self.timestamp
        }
