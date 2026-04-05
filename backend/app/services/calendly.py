"""Calendly API integration — fetch events and manage webhook subscriptions."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://api.calendly.com"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.getenv('CALENDLY_API_KEY', '')}",
        "Content-Type": "application/json",
    }


async def get_current_user() -> dict | None:
    """Get the authenticated Calendly user info."""
    if not os.getenv("CALENDLY_API_KEY", ""):
        logger.warning("[CALENDLY] API key not set — skipping")
        return None

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/users/me", headers=_headers())
        resp.raise_for_status()
        return resp.json().get("resource", {})


async def list_scheduled_events(count: int = 10) -> list[dict]:
    """List recent scheduled events."""
    if not os.getenv("CALENDLY_API_KEY", ""):
        return []

    user = await get_current_user()
    if not user:
        return []

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/scheduled_events",
            headers=_headers(),
            params={
                "user": user["uri"],
                "count": count,
                "sort": "start_time:desc",
                "status": "active",
            },
        )
        resp.raise_for_status()
        return resp.json().get("collection", [])


async def get_event_invitees(event_uri: str) -> list[dict]:
    """Get invitees for a specific event."""
    if not os.getenv("CALENDLY_API_KEY", ""):
        return []

    event_uuid = event_uri.split("/")[-1]
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/scheduled_events/{event_uuid}/invitees",
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json().get("collection", [])


async def create_webhook_subscription(
    callback_url: str, events: list[str] | None = None,
) -> dict | None:
    """Create a webhook subscription for Calendly events.

    Args:
        callback_url: The URL to receive webhook events.
        events: List of event types. Defaults to invitee.created.
    """
    if not os.getenv("CALENDLY_API_KEY", ""):
        logger.warning("[CALENDLY] API key not set — cannot create webhook")
        return None

    if events is None:
        events = ["invitee.created"]

    user = await get_current_user()
    if not user:
        return None

    org_uri = user.get("current_organization", "")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/webhook_subscriptions",
            headers=_headers(),
            json={
                "url": callback_url,
                "events": events,
                "organization": org_uri,
                "scope": "organization",
            },
        )
        resp.raise_for_status()
        return resp.json().get("resource", {})


async def list_webhook_subscriptions() -> list[dict]:
    """List existing webhook subscriptions."""
    if not os.getenv("CALENDLY_API_KEY", ""):
        return []

    user = await get_current_user()
    if not user:
        return []

    org_uri = user.get("current_organization", "")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/webhook_subscriptions",
            headers=_headers(),
            params={"organization": org_uri, "scope": "organization"},
        )
        resp.raise_for_status()
        return resp.json().get("collection", [])
