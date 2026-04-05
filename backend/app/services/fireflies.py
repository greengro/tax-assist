"""Fireflies.ai integration — fetch meeting transcripts via GraphQL API."""

import logging
import os

import httpx

logger = logging.getLogger(__name__)

GRAPHQL_URL = "https://api.fireflies.ai/graphql"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.getenv('FIREFLIES_API_KEY', '')}",
        "Content-Type": "application/json",
    }


async def get_recent_transcripts(limit: int = 5) -> list[dict]:
    """Fetch recent meeting transcripts from Fireflies."""
    if not os.getenv("FIREFLIES_API_KEY", ""):
        logger.warning("[FIREFLIES] API key not set — skipping")
        return []

    query = """
    query GetTranscripts($limit: Int!) {
        transcripts(limit: $limit) {
            id
            title
            date
            duration
            organizer_email
            participants
            summary {
                action_items
                keywords
                overview
                shorthand_bullet
            }
            sentences {
                text
                speaker_name
            }
        }
    }
    """

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GRAPHQL_URL,
            headers=_headers(),
            json={"query": query, "variables": {"limit": limit}},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("transcripts", [])


async def get_transcript_by_id(transcript_id: str) -> dict | None:
    """Fetch a specific transcript by ID."""
    if not os.getenv("FIREFLIES_API_KEY", ""):
        return None

    query = """
    query GetTranscript($id: String!) {
        transcript(id: $id) {
            id
            title
            date
            duration
            organizer_email
            participants
            summary {
                action_items
                keywords
                overview
                shorthand_bullet
            }
            sentences {
                text
                speaker_name
            }
        }
    }
    """

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            GRAPHQL_URL,
            headers=_headers(),
            json={"query": query, "variables": {"id": transcript_id}},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}).get("transcript")


async def test_connection() -> bool:
    """Test Fireflies API connectivity by fetching the user profile."""
    if not os.getenv("FIREFLIES_API_KEY", ""):
        return False

    query = """
    query {
        user {
            email
            name
        }
    }
    """

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GRAPHQL_URL,
                headers=_headers(),
                json={"query": query},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            user = data.get("data", {}).get("user", {})
            if user:
                logger.info("[FIREFLIES] Connected as %s (%s)", user.get("name"), user.get("email"))
                return True
            return False
    except Exception as e:
        logger.error("[FIREFLIES] Connection test failed: %s", e)
        return False
