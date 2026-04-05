import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import clients, documents, pipeline, webhooks

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Tax Engagement Automation",
    description="Automated client engagement management for tax services, powered by Devin API",
    version="0.1.0",
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(clients.router)
app.include_router(webhooks.router)
app.include_router(pipeline.router)
app.include_router(documents.router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    os.makedirs("./uploads", exist_ok=True)

    # Ensure Google Sheets CRM headers exist
    from app.services import google_sheets
    try:
        await google_sheets.ensure_headers()
    except Exception:
        logging.getLogger(__name__).warning(
            "Failed to ensure Google Sheets headers — continuing startup",
        )


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/integrations/status")
async def integration_status():
    """Return which integrations are configured (not the actual keys)."""
    return {
        "calendly": bool(os.getenv("CALENDLY_API_KEY", "")),
        "google_drive": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "") and os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")),
        "google_sheets": bool(os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY", "") and os.getenv("GOOGLE_SHEET_ID", "")),
        "google_docs": bool(os.getenv("GMAIL_CLIENT_ID", "") and os.getenv("GMAIL_CLIENT_SECRET", "") and os.getenv("GMAIL_REFRESH_TOKEN", "")),
        "gmail": bool(os.getenv("GMAIL_ADDRESS", "") and os.getenv("GMAIL_CLIENT_ID", "") and os.getenv("GMAIL_CLIENT_SECRET", "") and os.getenv("GMAIL_REFRESH_TOKEN", "")),
        "fireflies": bool(os.getenv("FIREFLIES_API_KEY", "")),
        "devin": bool(os.getenv("DEVIN_API_KEY", "") and os.getenv("DEVIN_ORG_ID", "")),
    }
