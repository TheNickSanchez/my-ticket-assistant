from __future__ import annotations
import os, json, time
from typing import List
from datetime import datetime
import requests
from .models import Ticket, TicketDetail
from .config.settings import SETTINGS

CACHE_FILE = os.path.join(os.path.dirname(__file__), "..", ".ticket_cache.json")

def _jira_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

def _jira_auth():
    return (SETTINGS.jira_email, SETTINGS.jira_api_token)

def _map_issue(issue: dict) -> Ticket:
    fields = issue.get("fields", {})
    comments = fields.get("comment", {}).get("total", 0) if fields.get("comment") else 0
    priority = (fields.get("priority") or {}).get("name")
    created = fields.get("created")
    updated = fields.get("updated")
    labels = fields.get("labels") or []
    issuetype = (fields.get("issuetype") or {}).get("name")
    summary = fields.get("summary") or ""
    # Try to extract severity from labels like sev1/sev2
    sev = None
    for lb in labels:
        if lb.lower().startswith("sev"):
            try:
                sev = int(lb.lower().replace("sev", ""))
            except: pass

    return Ticket(
        id=issue.get("id",""),
        key=issue.get("key",""),
        summary=summary,
        priority=priority,
        severity=sev,
        status=(fields.get("status") or {}).get("name"),
        created_at=datetime.fromisoformat(created.replace("Z","+00:00")) if created else None,
        updated_at=datetime.fromisoformat(updated.replace("Z","+00:00")) if updated else None,
        comments_count=comments,
        labels=labels,
        issue_type=issuetype,
        blocking_count=0,  # Can be enhanced by parsing issue links
        reporter=(fields.get("reporter") or {}).get("displayName"),
        assignee=(fields.get("assignee") or {}).get("displayName"),
    )

class TicketFetcher:
    def __init__(self):
        self.base = SETTINGS.jira_base_url
        self.session = requests.Session()

    def get_my_active_tickets(self) -> List[Ticket]:
        if SETTINGS.demo_mode or not self.base:
            return self._demo_tickets()

        jql = f"{SETTINGS.jira_jql_assignee} AND {SETTINGS.jira_jql_status}"
        url = f"{self.base}/rest/api/3/search"
        params = {
            "jql": jql,
            "maxResults": 50,
            "fields": "summary,priority,status,labels,issuetype,created,updated,comment,reporter,assignee"
        }
        r = self.session.get(url, headers=_jira_headers(), params=params, auth=_jira_auth(), timeout=20)
        r.raise_for_status()
        data = r.json()
        issues = data.get("issues", [])
        tickets = [ _map_issue(i) for i in issues ]
        self._cache({'tickets': [t.model_dump() for t in tickets], 'ts': time.time()})
        return tickets

    def get_ticket_details(self, ticket_key: str) -> TicketDetail:
        if SETTINGS.demo_mode or not self.base:
            for t in self._demo_tickets():
                if t.key == ticket_key:
                    return TicketDetail(**t.model_dump(), description="Demo ticket details.")
            raise ValueError(f"Ticket {ticket_key} not found in demo mode") 

        url = f"{self.base}/rest/api/3/issue/{ticket_key}"
        params = {"expand": "renderedFields,renderedDescription"}
        r = self.session.get(url, headers=_jira_headers(), params=params, auth=_jira_auth(), timeout=20)
        r.raise_for_status()
        issue = r.json()
        t = _map_issue(issue)
        desc = (issue.get("fields",{}).get("description") or "") if isinstance(issue.get("fields",{}).get("description"), str) else ""
        return TicketDetail(**t.model_dump(), description=desc)

    def refresh_cache(self) -> None:
        self._cache({"tickets": [], "ts": time.time()})

    # --- helpers ---
    def _cache(self, obj: dict):
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(obj, f, indent=2, default=str)
        except Exception:
            pass

    def _demo_tickets(self) -> List[Ticket]:
        demo_path = os.path.join(os.path.dirname(__file__), "..", "tests", "sample_tickets.json")
        with open(demo_path, "r", encoding="utf-8") as f:
            arr = json.load(f)
        return [Ticket(**x) for x in arr]
