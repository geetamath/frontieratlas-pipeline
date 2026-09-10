"""FastAPI Web Dashboard & REST API for FrontierAtlas Intelligence Graph."""

import os
import csv
from datetime import datetime, timezone
from typing import Dict, List, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.entity_resolver.resolver import EntityResolver

app = FastAPI(
    title="FrontierAtlas Intelligence Graph API",
    description="Production Data Ingestion, Signal Monitoring & Entity Resolution Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

resolver = EntityResolver()
OUTPUT_DIR = "output"


def load_csv_data(filename: str) -> List[Dict]:
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        return list(reader)


class ResolveRequest(BaseModel):
    raw_name: str
    source: Optional[str] = "api"


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "FrontierAtlas Ingestion Engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/stats")
def get_stats():
    return {
        "startups_count": len(load_csv_data("startups.csv")),
        "products_count": len(load_csv_data("products.csv")),
        "research_papers_count": len(load_csv_data("research_papers.csv")),
        "fresh_jobs_count": len(load_csv_data("jobs.csv")),
        "fresh_news_count": len(load_csv_data("news.csv")),
        "entity_mapping_logs_count": len(load_csv_data("entity_mapping_log.csv"))
    }


@app.post("/api/resolve")
def resolve_entity(req: ResolveRequest):
    canonical, score, method = resolver.resolve(req.raw_name, source=req.source)
    return {
        "raw_name": req.raw_name,
        "canonical_name": canonical,
        "confidence_score": score,
        "method": method,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/startups")
def get_startups(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    data = load_csv_data("startups.csv")
    return {"total": len(data), "limit": limit, "offset": offset, "records": data[offset:offset + limit]}


@app.get("/api/products")
def get_products(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    data = load_csv_data("products.csv")
    return {"total": len(data), "limit": limit, "offset": offset, "records": data[offset:offset + limit]}


@app.get("/api/papers")
def get_papers(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0)):
    data = load_csv_data("research_papers.csv")
    return {"total": len(data), "limit": limit, "offset": offset, "records": data[offset:offset + limit]}


@app.get("/api/jobs")
def get_jobs():
    data = load_csv_data("jobs.csv")
    return {"total": len(data), "records": data}


@app.get("/api/news")
def get_news():
    data = load_csv_data("news.csv")
    return {"total": len(data), "records": data}


@app.get("/download/excel")
def download_excel():
    excel_path = os.path.join(OUTPUT_DIR, "pipeline_output.xlsx")
    if not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="Excel file not found. Run pipeline first.")
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="frontieratlas_pipeline_output.xlsx"
    )


@app.get("/download/architecture-pdf")
def download_pdf():
    pdf_path = "architecture.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Architecture PDF not found.")
    return FileResponse(pdf_path, media_type="application/pdf", filename="architecture.pdf")


@app.get("/", response_class=HTMLResponse)
def index_dashboard():
    stats = get_stats()
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>FrontierAtlas — Live Intelligence Graph</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Inter', sans-serif; background-color: #0B0F17; color: #E2E8F0; }}
        </style>
    </head>
    <body class="min-h-screen p-6 md:p-10">
        <div class="max-w-7xl mx-auto space-y-8">
            <!-- Header -->
            <div class="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-6 gap-4">
                <div>
                    <div class="flex items-center gap-3">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            ● Live Production Node
                        </span>
                        <span class="text-xs text-slate-500">v1.0.0</span>
                    </div>
                    <h1 class="text-3xl font-bold tracking-tight text-white mt-1">FrontierAtlas Intelligence Graph</h1>
                    <p class="text-sm text-slate-400 mt-0.5">High-Scale Autonomous Data Ingestion, Signal Monitoring & Entity Resolution Mesh</p>
                </div>
                <div class="flex items-center gap-3">
                    <a href="/download/excel" class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition shadow-sm">
                        📥 Download Excel (6 Tabs)
                    </a>
                    <a href="/download/architecture-pdf" class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
                        📄 Architecture PDF (3 Pgs)
                    </a>
                    <a href="/docs" target="_blank" class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition">
                        ⚡ Swagger API
                    </a>
                </div>
            </div>

            <!-- Stats Overview Cards -->
            <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
                    <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Startups</div>
                    <div class="text-2xl font-bold text-white mt-1">{stats['startups_count']:,}</div>
                    <div class="text-xs text-emerald-400 mt-1">✓ YC Algolia Index</div>
                </div>
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
                    <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">AI Products</div>
                    <div class="text-2xl font-bold text-white mt-1">{stats['products_count']:,}</div>
                    <div class="text-xs text-emerald-400 mt-1">✓ 4 Pricing Tiers</div>
                </div>
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
                    <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Research Papers</div>
                    <div class="text-2xl font-bold text-white mt-1">{stats['research_papers_count']:,}</div>
                    <div class="text-xs text-emerald-400 mt-1">✓ ArXiv + GitHub Stars</div>
                </div>
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
                    <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">24h AI Jobs</div>
                    <div class="text-2xl font-bold text-white mt-1">{stats['fresh_jobs_count']:,}</div>
                    <div class="text-xs text-blue-400 mt-1">✓ 5 Job Boards</div>
                </div>
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
                    <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">24h AI News</div>
                    <div class="text-2xl font-bold text-white mt-1">{stats['fresh_news_count']:,}</div>
                    <div class="text-xs text-blue-400 mt-1">✓ 5 News Outlets</div>
                </div>
                <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4">
                    <div class="text-xs font-medium text-slate-400 uppercase tracking-wider">Entity Mappings</div>
                    <div class="text-2xl font-bold text-white mt-1">{stats['entity_mapping_logs_count']:,}</div>
                    <div class="text-xs text-purple-400 mt-1">✓ Full Audit Log</div>
                </div>
            </div>

            <!-- Interactive Entity Resolution Sandbox -->
            <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h2 class="text-lg font-semibold text-white">Interactive Deterministic Entity Resolver</h2>
                        <p class="text-sm text-slate-400">Test canonicalization with corporate legal suffix stripping, Unicode normalization, and seed alias mapping.</p>
                    </div>
                </div>
                <div class="flex flex-col sm:flex-row gap-3">
                    <input id="rawInput" type="text" placeholder="Try: 'OpenAI, Inc.', 'Anthropic PBC', 'Mistral AI SAS', 'Anysphere Inc.'" class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500">
                    <button onclick="testResolution()" class="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition shadow-sm">Resolve Entity</button>
                </div>
                <div id="resolveResult" class="mt-4 hidden p-4 rounded-lg bg-slate-950 border border-slate-800 font-mono text-xs">
                    <!-- Dynamic Result -->
                </div>
            </div>

            <!-- API Endpoints Quick Reference -->
            <div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6">
                <h2 class="text-lg font-semibold text-white mb-4">REST API Endpoints</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div class="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">GET</span>
                            <code class="text-slate-300">/api/startups?limit=50&offset=0</code>
                        </div>
                        <span class="text-xs text-slate-500">Startups Directory</span>
                    </div>
                    <div class="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">GET</span>
                            <code class="text-slate-300">/api/products?limit=50&offset=0</code>
                        </div>
                        <span class="text-xs text-slate-500">AI Products</span>
                    </div>
                    <div class="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">GET</span>
                            <code class="text-slate-300">/api/papers?limit=50&offset=0</code>
                        </div>
                        <span class="text-xs text-slate-500">Research Papers with Stars</span>
                    </div>
                    <div class="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-blue-500/20 text-blue-400">POST</span>
                            <code class="text-slate-300">/api/resolve</code>
                        </div>
                        <span class="text-xs text-slate-500">Live Entity Canonicalizer</span>
                    </div>
                    <div class="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">GET</span>
                            <code class="text-slate-300">/api/jobs</code>
                        </div>
                        <span class="text-xs text-slate-500">24-Hour Fresh Jobs</span>
                    </div>
                    <div class="p-3 bg-slate-950 rounded-lg border border-slate-800/80 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/20 text-emerald-400">GET</span>
                            <code class="text-slate-300">/api/news</code>
                        </div>
                        <span class="text-xs text-slate-500">24-Hour Fresh News</span>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function testResolution() {{
                const input = document.getElementById('rawInput').value.trim();
                if (!input) return;
                const resEl = document.getElementById('resolveResult');
                resEl.classList.remove('hidden');
                resEl.innerHTML = '<span class="text-slate-500">Resolving...</span>';

                try {{
                    const resp = await fetch('/api/resolve', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ raw_name: input }})
                    }});
                    const data = await resp.json();
                    resEl.innerHTML = `
                        <div class="space-y-1">
                            <div><span class="text-slate-500">Input String:</span> <span class="text-amber-300 font-semibold">"${{data.raw_name}}"</span></div>
                            <div><span class="text-slate-500">Canonical Name:</span> <span class="text-emerald-400 font-bold text-sm">"${{data.canonical_name}}"</span></div>
                            <div><span class="text-slate-500">Confidence Score:</span> <span class="text-blue-400">${{data.confidence_score}}</span></div>
                            <div><span class="text-slate-500">Resolution Method:</span> <span class="text-purple-400">${{data.method}}</span></div>
                        </div>
                    `;
                }} catch (e) {{
                    resEl.innerHTML = `<span class="text-red-400">Error: ${{e.message}}</span>`;
                }}
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
