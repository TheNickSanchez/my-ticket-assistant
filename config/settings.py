from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"), override=False)

def env_bool(name: str, default: bool=False) -> bool:
    v = os.getenv(name, "").strip().lower()
    if v in ("1","true","yes","y","on"): return True
    if v in ("0","false","no","n","off"): return False
    return default

@dataclass
class Settings:
    demo_mode: bool = env_bool("DEMO_MODE", True)
    dry_run: bool = env_bool("DRY_RUN", True)

    # Jira
    jira_base_url: str = os.getenv("JIRA_BASE_URL", "").rstrip("/")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")
    jira_jql_assignee: str = os.getenv("JIRA_JQL_ASSIGNEE", 'assignee = currentUser()')
    jira_jql_status: str = os.getenv("JIRA_JQL_STATUS", 'status in ("To Do","In Progress","Selected for Development")')

    # LLM
    llm_provider: str = os.getenv("LLM_PROVIDER", "stub")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.1")

SETTINGS = Settings()
