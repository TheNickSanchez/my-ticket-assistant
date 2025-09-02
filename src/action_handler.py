from __future__ import annotations
import os, json, pathlib
import requests
from typing import Optional
from .models import CVEDetails, Script, Ticket, Result
from .llm_client import LLMClient
from config.settings import SETTINGS

ART_DIR = os.path.join(os.path.dirname(__file__), "..", "artifacts")
os.makedirs(ART_DIR, exist_ok=True)

def _jira_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def _jira_auth():
    return (SETTINGS.jira_email, SETTINGS.jira_api_token)

class ActionHandler:
    def __init__(self):
        self.llm = LLMClient()

    def create_file(self, content: str, filename: str) -> bool:
        if not filename:
            filename = "notes.md"
        path = os.path.join(ART_DIR, filename)
        pathlib.Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def post_jira_comment(self, ticket_key: str, comment: str) -> bool:
        if SETTINGS.demo_mode or SETTINGS.dry_run or not SETTINGS.jira_base_url:
            print(f"[DRY-RUN] Would post comment to {ticket_key}:\n{comment}\n")
            return True
        url = f"{SETTINGS.jira_base_url}/rest/api/3/issue/{ticket_key}/comment"
        payload = {"body": comment}
        r = requests.post(url, headers=_jira_headers(), auth=_jira_auth(), json=payload, timeout=20)
        if r.status_code >= 200 and r.status_code < 300:
            return True
        print(f"Jira comment failed: {r.status_code} {r.text}")
        return False

    def research_cve(self, cve_id: str) -> CVEDetails:
        return self.llm.research_cve(cve_id)

    def generate_script(self, requirements: str) -> Script:
        return self.llm.generate_script(requirements)

