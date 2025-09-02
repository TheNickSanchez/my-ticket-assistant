# Personal Ticket Assistant (CLI)

A conversational AI work companion for Jira: pulls your tickets, prioritizes intelligently, collaborates on actions (research CVEs, draft comments, generate scripts), and keeps a lightweight conversational session.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp config/.env.example config/.env
# Edit config/.env with your Jira domain & credentials and LLM settings
# For a no-credential demo run:
# DEMO_MODE=true

python assistant.py           # Morning summary & interactive flow
python assistant.py --ticket ABC-123        # Focus a specific ticket
python assistant.py --continue              # Resume last session
```

## Environment

Create `config/.env` (see `.env.example`).

- `DEMO_MODE=true` will bypass network calls and use sample tickets and stubbed LLM outputs.
- `DRY_RUN=true` will avoid posting comments to Jira (prints what would happen).

## Jira Setup

1. Get your Cloud API token: https://id.atlassian.com/manage-profile/security/api-tokens
2. Set:
   - `JIRA_BASE_URL=https://YOURDOMAIN.atlassian.net`
   - `JIRA_EMAIL=you@company.com`
   - `JIRA_API_TOKEN=...`
3. Optional scoping: set `JIRA_JQL_ASSIGNEE=assignee = currentUser()` or `assignee = "you@company.com"`

## LLM Setup

Choose one provider via `LLM_PROVIDER`:

- `openai` (requires `OPENAI_API_KEY`, model via `OPENAI_MODEL`, default `gpt-4o-mini`)
- `ollama` (requires local Ollama; set `OLLAMA_BASE_URL` and `OLLAMA_MODEL` like `llama3.1`)
- `stub` (deterministic, offline default for DEMO_MODE)

## Features

- **Smart Prioritization**: severity, age, no-progress signals, blockers, CVE boost, custom label boosts.
- **Conversational Flow**: remembers session in `.pta_session.json` and proposes next actions.
- **Actions**: research CVE, draft Jira comments, generate scripts, create files in `artifacts/`.
- **Safety**: dry-run mode for Jira writes; DEMO mode for offline usage.

## File Tree

```
my-ticket-assistant/
├── assistant.py
├── requirements.txt
├── README.md
├── config/
│   ├── .env.example
│   └── settings.py
├── src/
│   ├── models.py
│   ├── llm_client.py
│   ├── ticket_fetcher.py
│   ├── work_assistant.py
│   ├── action_handler.py
│   └── chat_session.py
├── artifacts/           # Generated briefs, scripts, notes
└── tests/
    └── test_scoring.py
```

## Notes

- This is a clean, extensible baseline. Plug in company heuristics, add more actions, or connect to your knowledge base.
- All network calls are contained in `ticket_fetcher.py`, `action_handler.py`, and `llm_client.py` for easy mocking/testing.
