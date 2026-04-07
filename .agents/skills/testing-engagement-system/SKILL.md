# Testing: Tax Engagement Management System

## Local Setup

### Backend
```bash
cd backend
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```
Frontend runs on `http://localhost:5173`, backend on `http://localhost:8000`.

Frontend requires `.env` with `VITE_API_URL=http://localhost:8000`.

## Known Issues

### Vite Cache Stale CSS
Tailwind CSS utility classes may not compile after large CSS changes (e.g., adding `@layer` blocks to `index.css`). Symptoms: `display: block` instead of `flex`, missing `position: absolute`, etc.

**Fix:** Clear the Vite cache and restart:
```bash
rm -rf node_modules/.vite .vite
npm run dev -- --host 0.0.0.0
```
No code changes needed — production `npm run build` is unaffected.

## UI Testing Workflow

### Key UI Entry Points
- **Header**: "New Client" button opens AddClientModal, "Simulate" button opens WebhookSimulatorModal
- **Pipeline cards**: Click any client card to open ClientDetailModal
- **Activity Feed**: Bottom-left panel, auto-refreshes every 5 seconds
- **Communications**: Bottom-right panel with Emails/Signatures tabs

### End-to-End Test Flow
1. Click "Simulate" → fill Calendly Booking form (Name, Email) → submit
2. Verify success message shows client ID and Devin session ID
3. Close modal → verify new client card appears in pipeline
4. Click client card → verify ClientDetailModal opens with proper styling
5. Click "Send Engagement Letter" → verify stage advances and activity log updates
6. Check Activity Feed for gold-colored Devin session IDs

### Debugging CSS with Playwright
Use Playwright CDP to inspect computed styles when visual inspection is ambiguous:
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:29229")
    page = browser.contexts[0].pages[0]
    page.goto("http://localhost:5173", wait_until="networkidle")
    # Check computed styles
    result = page.evaluate("getComputedStyle(document.querySelector('.flex')).display")
```
**Note:** The app auto-refreshes every 5 seconds, which can cause Playwright `Execution context was destroyed` errors. Use `page.wait_for_timeout()` sparingly and handle navigation errors gracefully.

## Devin Secrets Needed
- No secrets required for local testing (all integrations use mock services)
- For production: `DEVIN_API_KEY`, `DEVIN_ORG_ID` (optional, falls back to mock)
