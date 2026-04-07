# Green Grove Tax Services — Engagement Management System

An automated client engagement management system for tax services, powered by the [Devin API](https://docs.devin.ai/api-reference/overview). Manages the full client lifecycle from Calendly booking through tax filing with real integrations for email, document generation, CRM tracking, and AI-driven task execution.

## Architecture

```
Frontend (React + Tailwind)          Backend (FastAPI + SQLite)
┌──────────────────────┐            ┌──────────────────────────┐
│  Pipeline Dashboard  │───────────▶│  Webhook Handlers        │
│  Webhook Simulator   │  REST API  │  ├─ Calendly booking     │
│  Client Detail Modal │◀───────────│  ├─ Meeting notes        │
│  Activity Feed       │            │  ├─ Engagement letter    │
│  Communications Log  │            │  ├─ Document check       │
└──────────────────────┘            │  └─ Return analysis      │
                                    │                          │
                                    │  Services                │
                                    │  ├─ Gmail API (OAuth2)   │
                                    │  ├─ Google Docs (OAuth2) │
                                    │  ├─ Google Drive (SA)    │
                                    │  ├─ Google Sheets (SA)   │
                                    │  ├─ Calendly API         │
                                    │  ├─ Fireflies API        │
                                    │  └─ Devin API            │
                                    └──────────────────────────┘
```

**SA** = Service Account, **OAuth2** = User OAuth2 credentials

## Prerequisites

- **Python 3.12+**
- **Node.js 18+** and npm
- **Poetry** — Python dependency manager ([install](https://python-poetry.org/docs/#installation))

## Quick Start (Mock Mode)

All integrations fall back to mock/stub mode when credentials are not configured. This lets you run the full app without any API keys.

```bash
# 1. Clone the repo
git clone https://github.com/greengro/tax-assist.git
cd tax-assist

# 2. Backend setup
cd backend
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Frontend setup (in a new terminal)
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env
npm install
npm run dev
```

Open **http://localhost:5173** in your browser. You'll see the pipeline dashboard. Click **"Simulate"** to test the workflow with mock integrations.

## Setting Up Real Integrations

All integrations are optional — enable them one at a time by setting environment variables before starting the backend. Create a `.env` file in `backend/` or export them in your shell.

### 1. Google Cloud Project (required for Drive, Sheets, Gmail, Docs)

All Google integrations share one GCP project.

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → Create a new project (or use an existing one)
2. Enable these APIs:
   - [Google Drive API](https://console.cloud.google.com/apis/api/drive.googleapis.com)
   - [Google Sheets API](https://console.cloud.google.com/apis/api/sheets.googleapis.com)
   - [Gmail API](https://console.cloud.google.com/apis/api/gmail.googleapis.com)
   - [Google Docs API](https://console.cloud.google.com/apis/api/docs.googleapis.com)

### 2. Google Drive + Google Sheets (Service Account)

These use a **service account** for server-to-server auth.

1. Go to [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts) → Create service account → name it `tax-automation`
2. Click into the service account → **Keys** → Add Key → **JSON** → Download
3. Create a **"Clients" folder** in your Google Drive
   - Share it with the service account email (e.g., `tax-automation@your-project.iam.gserviceaccount.com`) as **Editor**
   - Copy the folder ID from the URL: `drive.google.com/drive/folders/{FOLDER_ID}`
4. Create a Google Sheets spreadsheet for the CRM
   - Share it with the same service account email as **Editor**
   - Copy the spreadsheet ID from the URL: `docs.google.com/spreadsheets/d/{SHEET_ID}/edit`

```bash
# Set these env vars (paste the full JSON key content, not the file path)
export GOOGLE_SERVICE_ACCOUNT_KEY='{"type":"service_account","project_id":"...","private_key":"...",...}'
export GOOGLE_DRIVE_FOLDER_ID="your-folder-id"
export GOOGLE_SHEET_ID="your-spreadsheet-id"
```

The app will auto-populate the CRM spreadsheet headers on first startup.

### 3. Gmail + Google Docs (OAuth2 User Credentials)

Gmail and Google Docs use **OAuth2 user credentials** (not the service account) because:
- Gmail API requires user authorization to send emails as your account
- Service accounts have a 0-byte Drive storage quota, so they can't create Google Docs

**Create OAuth2 credentials:**

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials) → Create Credentials → **OAuth client ID**
2. Application type: **Desktop app** → Create
3. Copy the **Client ID** and **Client Secret**

**Set up the OAuth consent screen:**

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Add your email as a test user (if project is in "Testing" status)
3. **Important**: If in "Testing" mode, refresh tokens expire after 7 days. Click **"Publish App"** to make tokens permanent.

**Get a refresh token:**

```bash
export GMAIL_CLIENT_ID="your-client-id"
export GMAIL_CLIENT_SECRET="your-client-secret"

cd backend
poetry run python scripts/gmail_auth.py
```

The script will:
1. Print a URL — open it in your browser
2. Approve access for Gmail, Google Docs, and Google Drive scopes
3. Your browser redirects to `http://localhost:8085` (the page won't load — that's expected)
4. Copy the `code=` value from the URL bar and paste it into the terminal
5. The script prints your **refresh token**

```bash
export GMAIL_ADDRESS="your-email@gmail.com"
export GMAIL_CLIENT_ID="your-client-id"
export GMAIL_CLIENT_SECRET="your-client-secret"
export GMAIL_REFRESH_TOKEN="the-refresh-token-from-above"
```

### 4. Calendly

1. Go to [Calendly → Integrations → API](https://calendly.com/integrations/api_webhooks)
2. Generate a **Personal Access Token**

```bash
export CALENDLY_API_KEY="your-calendly-pat"
```

### 5. Fireflies.ai (Meeting Notes)

1. Sign up at [Fireflies.ai](https://fireflies.ai)
2. Go to [Settings → Developer API](https://app.fireflies.ai/integrations) → Get your API key

```bash
export FIREFLIES_API_KEY="your-fireflies-api-key"
```

### 6. Devin API

1. Go to [Devin Settings → Service Users](https://app.devin.ai/settings)
2. Create a service user → Generate an API key
3. Copy your Org ID from the same page

```bash
export DEVIN_API_KEY="your-devin-api-key"
export DEVIN_ORG_ID="your-org-id"
```

## Full `.env` Template

Create `backend/.env` with all variables:

```bash
# Google Service Account (Drive + Sheets)
GOOGLE_SERVICE_ACCOUNT_KEY='{"type":"service_account",...}'
GOOGLE_DRIVE_FOLDER_ID=your-folder-id
GOOGLE_SHEET_ID=your-spreadsheet-id

# Gmail + Google Docs (OAuth2)
GMAIL_ADDRESS=your-email@gmail.com
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REFRESH_TOKEN=your-refresh-token

# Calendly
CALENDLY_API_KEY=your-calendly-pat

# Fireflies
FIREFLIES_API_KEY=your-fireflies-api-key

# Devin API
DEVIN_API_KEY=your-devin-api-key
DEVIN_ORG_ID=your-org-id
```

> **Note**: The backend reads env vars directly via `os.getenv()`. If using a `.env` file, source it before starting: `source .env && poetry run uvicorn ...`

## Running the App

```bash
# Terminal 1 — Backend
cd backend
source .env  # if using a .env file
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Open **http://localhost:5173**

## Verifying Integrations

Once running, check which integrations are connected:

```bash
curl -s http://localhost:8000/api/integrations/status | python3 -m json.tool
```

Returns:
```json
{
    "calendly": true,
    "google_drive": true,
    "google_sheets": true,
    "google_docs": true,
    "gmail": true,
    "fireflies": true,
    "devin": true
}
```

Any service showing `false` will fall back to mock mode automatically.

## Testing the Workflow

1. **Simulate Calendly Booking**: Click "Simulate" → enter a name and email → submit
   - Creates a Google Drive folder for the client
   - Sends a welcome email via Gmail API
   - Triggers a Devin onboarding session
   - Adds client to Google Sheets CRM
   - Client appears in "INTRO BOOKED" column

2. **Process Meeting Notes**: Click "Process Meeting" on the client card
   - Enter meeting transcript, scope of services, and fee estimate
   - Sends a follow-up email via Gmail API
   - Triggers a Devin post-meeting session

3. **Send Engagement Letter**: Click client card → "Send Engagement Letter"
   - Creates a real Google Doc (Engagement Letter + Statement of Work)
   - Sends email with document links
   - Updates Google Sheets CRM

4. **Check Documents**: Click "Check Documents" to review missing items
   - Sends reminder emails for missing documents

5. **Run Analysis**: Click "Run Analysis" to trigger return analysis
   - Creates a Devin session for AI-powered tax analysis

## Project Structure

```
tax-assist/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, startup, integration status
│   │   ├── database.py          # SQLAlchemy async engine (SQLite)
│   │   ├── models.py            # Client, Activity, ChecklistItem models
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── routers/
│   │   │   ├── clients.py       # CRUD endpoints for clients
│   │   │   ├── webhooks.py      # Webhook handlers (Calendly, meeting, letter, etc.)
│   │   │   ├── pipeline.py      # Dashboard data (summary, stats, activity feed)
│   │   │   └── documents.py     # Document upload/checklist management
│   │   └── services/
│   │       ├── calendly.py      # Calendly API integration
│   │       ├── devin_api.py     # Devin API integration + prompt templates
│   │       ├── gmail.py         # Gmail API (OAuth2 + HTTPS)
│   │       ├── google_docs.py   # Google Docs API (OAuth2)
│   │       ├── google_drive.py  # Google Drive API (Service Account)
│   │       ├── google_sheets.py # Google Sheets CRM (Service Account)
│   │       ├── fireflies.py     # Fireflies.ai API
│   │       └── mock_services.py # Mock fallbacks for all services
│   ├── scripts/
│   │   └── gmail_auth.py        # One-time OAuth2 token helper
│   └── pyproject.toml           # Python dependencies (Poetry)
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main app with auto-refresh polling
│   │   ├── components/
│   │   │   ├── Header.tsx       # Header with stats (Clients, Emails, Signed)
│   │   │   ├── PipelineBoard.tsx # Kanban board with 13 pipeline stages
│   │   │   ├── ActivityFeed.tsx # Real-time activity log
│   │   │   ├── EmailLog.tsx     # Communications panel (Emails + Signatures)
│   │   │   ├── ClientDetailModal.tsx  # Client detail with actions
│   │   │   ├── WebhookSimulatorModal.tsx # Simulate webhooks for testing
│   │   │   └── AddClientModal.tsx # Manual client creation
│   │   ├── lib/
│   │   │   ├── api.ts           # API client functions
│   │   │   └── types.ts         # TypeScript type definitions
│   │   └── index.css            # Tailwind + custom styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Pipeline Stages

The system tracks clients through 13 stages:

| Stage | Description |
|---|---|
| Lead | New prospect, not yet booked |
| Intro Booked | Calendly meeting scheduled |
| Intro Completed | Discovery call done, notes processed |
| Docs Requested | Document checklist sent to client |
| Docs Received | All required documents uploaded |
| Letter Sent | Engagement letter + SOW created and emailed |
| Signed | Client accepted engagement terms |
| In Progress | Tax preparation underway |
| Review | Return ready for internal review |
| Return Completed | Return finalized, ready for client |
| Return Signed | Client signed the return |
| Filed | Return e-filed with IRS |
| Completed | Engagement complete |

## Lint & Build

```bash
# Backend lint
cd backend && poetry run ruff check app/

# Frontend lint + build
cd frontend && npm run lint && npm run build
```

## Troubleshooting

**Gmail API "port blocked" error**: The app uses the Gmail API over HTTPS (not SMTP), so no special ports are needed. If you see SMTP-related errors, make sure you're using the latest code.

**Google Docs "permission denied"**: This usually means the OAuth2 refresh token doesn't include the `documents` or `drive.file` scopes. Re-run `scripts/gmail_auth.py` to get a new token with all scopes.

**OAuth refresh token expired**: If your GCP project is in "Testing" publishing status, tokens expire after 7 days. Either publish the app or re-run the auth script.

**Google Sheets headers not created**: The app auto-creates headers on startup. If it fails (e.g., network issue), restart the backend.
