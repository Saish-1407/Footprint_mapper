"""
Company Footprint Mapper — FastAPI backend.

Run:
    uvicorn main:app --reload

Environment variables (optional):
    SHODAN_API_KEY   — your free Shodan API key
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from recon.crtsh import enumerate_subdomains
from recon.shodan import lookup_exposed_services
from recon.jobposts import fetch_job_posts


app = FastAPI(title="Footprint Mapper", version="1.0.0")

# Allow the single-file frontend to call us from file:// or any dev port
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SHODAN_API_KEY = os.getenv("SHODAN_API_KEY", "")


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "service": "Footprint Mapper"}


# ── Subdomains (crt.sh) ───────────────────────────────────────────────────────

@app.get("/api/subdomains")
async def get_subdomains(domain: str = Query(..., description="Target domain e.g. example.com")):
    try:
        results = await enumerate_subdomains(domain)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"domain": domain, "count": len(results), "results": results}


# ── Exposed services (Shodan) ─────────────────────────────────────────────────

@app.get("/api/services")
async def get_services(
    domain: str = Query(..., description="Target domain"),
    api_key: Optional[str] = Query(None, description="Override SHODAN_API_KEY env var"),
):
    key = api_key or SHODAN_API_KEY
    try:
        results = await lookup_exposed_services(domain, key)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"domain": domain, "count": len(results), "results": results}


# ── Job posts ─────────────────────────────────────────────────────────────────

@app.get("/api/jobs")
async def get_jobs(
    company: str = Query(..., description="Company name e.g. Stripe"),
    domain: str = Query(..., description="Domain e.g. stripe.com"),
):
    try:
        result = await fetch_job_posts(company, domain)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return result


# ── Full scan (all three in parallel) ────────────────────────────────────────

import asyncio

@app.get("/api/scan")
async def full_scan(
    company: str = Query(..., description="Company name"),
    domain: str = Query(..., description="Target domain"),
    shodan_key: Optional[str] = Query(None),
):
    key = shodan_key or SHODAN_API_KEY
    try:
        subdomains, services, jobs = await asyncio.gather(
            enumerate_subdomains(domain),
            lookup_exposed_services(domain, key),
            fetch_job_posts(company, domain),
            return_exceptions=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    def _safe(val):
        return {"error": str(val)} if isinstance(val, Exception) else val

    return {
        "company": company,
        "domain": domain,
        "subdomains": {"count": len(subdomains) if isinstance(subdomains, list) else 0, "results": _safe(subdomains)},
        "services":   {"count": len(services)   if isinstance(services,   list) else 0, "results": _safe(services)},
        "jobs":        _safe(jobs),
    }
