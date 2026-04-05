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


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
