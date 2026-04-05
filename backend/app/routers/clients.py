"""Client CRM management routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Activity, Client, DocumentChecklist, PipelineStage
from app.schemas import ClientCreate, ClientOut, ClientUpdate

router = APIRouter(prefix="/api/clients", tags=["clients"])

# Default document checklist items for new clients
DEFAULT_CHECKLIST = [
    "W-2 Forms",
    "1099 Forms (Freelance/Investments)",
    "Prior Year Tax Return",
    "Property Tax Statements",
    "Mortgage Interest (Form 1098)",
    "Charitable Donation Receipts",
    "Business Expense Receipts",
    "Health Insurance (Form 1095)",
]


@router.get("", response_model=list[ClientOut])
async def list_clients(
    stage: PipelineStage | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Client).order_by(Client.updated_at.desc())
    if stage:
        query = query.where(Client.stage == stage)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("", response_model=ClientOut, status_code=201)
async def create_client(data: ClientCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Client).where(Client.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Client with this email already exists")

    client = Client(**data.model_dump())
    db.add(client)
    await db.flush()

    # Create default document checklist
    for doc_name in DEFAULT_CHECKLIST:
        item = DocumentChecklist(client_id=client.id, doc_name=doc_name)
        db.add(item)

    activity = Activity(
        client_id=client.id,
        action="Client added to CRM",
        details=f"Stage: {client.stage.value}",
    )
    db.add(activity)
    await db.commit()
    await db.refresh(client)
    return client


@router.patch("/{client_id}", response_model=ClientOut)
async def update_client(
    client_id: int, data: ClientUpdate, db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = data.model_dump(exclude_unset=True)
    old_stage = client.stage

    for field_name, value in update_data.items():
        setattr(client, field_name, value)

    if "stage" in update_data and update_data["stage"] != old_stage:
        activity = Activity(
            client_id=client.id,
            action="Pipeline stage updated",
            details=f"{old_stage.value} → {update_data['stage'].value}",
        )
        db.add(activity)

    await db.commit()
    await db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await db.delete(client)
    await db.commit()
