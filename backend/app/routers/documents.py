"""Document upload and checklist routes."""

import os
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Activity, Client, Document, DocumentChecklist, PipelineStage

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = "./uploads"


@router.post("/upload/{client_id}")
async def upload_document(
    client_id: int,
    doc_type: str = "general",
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    upload_path = os.path.join(UPLOAD_DIR, str(client_id))
    os.makedirs(upload_path, exist_ok=True)

    filename = file.filename or f"doc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    file_path = os.path.join(upload_path, filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        client_id=client.id, filename=filename,
        doc_type=doc_type, file_path=file_path,
    )
    db.add(doc)

    db.add(Activity(
        client_id=client.id,
        action="Document uploaded",
        details=f"File: {filename} (Type: {doc_type})",
    ))

    # Auto-advance stage if waiting for documents
    if client.stage == PipelineStage.DOCUMENTS_REQUESTED:
        client.stage = PipelineStage.DOCUMENTS_RECEIVED
        db.add(Activity(
            client_id=client.id,
            action="Pipeline stage updated",
            details="documents_requested → documents_received",
        ))

    await db.commit()
    return {
        "status": "uploaded",
        "document_id": doc.id,
        "filename": filename,
        "client_stage": client.stage.value,
    }


@router.get("/{client_id}")
async def list_documents(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Document).where(Document.client_id == client_id)
        .order_by(Document.uploaded_at.desc())
    )
    return [
        {"id": d.id, "filename": d.filename, "doc_type": d.doc_type,
         "uploaded_at": d.uploaded_at.isoformat()}
        for d in result.scalars().all()
    ]


@router.get("/checklist/{client_id}")
async def get_checklist(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(DocumentChecklist).where(DocumentChecklist.client_id == client_id)
    )
    return [
        {"id": i.id, "doc_name": i.doc_name, "required": i.required, "received": i.received}
        for i in result.scalars().all()
    ]


@router.patch("/checklist/{item_id}")
async def update_checklist_item(
    item_id: int, received: bool = True, db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(DocumentChecklist).where(DocumentChecklist.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    item.received = received
    await db.commit()
    return {"id": item.id, "doc_name": item.doc_name, "received": item.received}
