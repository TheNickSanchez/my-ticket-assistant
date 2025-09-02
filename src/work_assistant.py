from __future__ import annotations
from typing import List, Tuple
from datetime import datetime, timezone
from .models import Ticket, WorkItem, WorkloadAnalysis, Action, ActionSuggestion
from .llm_client import LLMClient

def _days_ago(dt) -> float:
    if not dt: return 0.0
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (now - dt).total_seconds() / 86400.0

class WorkAssistant:
    def __init__(self):
        self.llm = LLMClient()

    def analyze_workload(self, tickets: List[Ticket]) -> WorkloadAnalysis:
        items: List[WorkItem] = []
        for t in tickets:
            score, reasons = self._score_ticket(t)
            items.append(WorkItem(ticket=t, score=score, reasons=reasons))

        items.sort(key=lambda wi: wi.score, reverse=True)
        summary = self.llm.analyze([wi.ticket for wi in items[:5]])  # optional NL summary
        return WorkloadAnalysis(ordered=items, summary=summary)

    def suggest_next_action(self, context: str) -> ActionSuggestion:
        # Very simple suggestion engine for now
        actions = []
        ctx = context.lower()
        if "cve" in ctx:
            actions.append(Action(name="research_cve", params={"cve_id": context.strip()}))
            actions.append(Action(name="generate_script", params={"requirements": "Audit current SSO/SAML configuration and enforce strict validation."}))
            actions.append(Action(name="draft_comment", params={"ticket_key": None}))
            msg = "I can research the CVE, draft a remediation checklist, and prepare a status comment."
        else:
            actions.append(Action(name="draft_comment", params={"ticket_key": None}))
            actions.append(Action(name="create_file", params={"filename": "notes.md", "content": "Session notes"}))
            msg = "I can draft a comment and create notes to move this forward."
        return ActionSuggestion(message=msg, actions=actions)

    def _score_ticket(self, t: Ticket) -> Tuple[float, List[str]]:
        score = 0.0
        reasons = []

        # Severity from labels (sev1..sev5) or priority
        if t.severity:
            sev_score = (6 - t.severity) * 2.5  # sev1 => +12.5
            score += sev_score
            reasons.append(f"sev{t.severity}: +{sev_score:.1f}")
        elif t.priority:
            pri_map = {"Highest": 12, "High": 9, "Medium": 6, "Low": 3, "Lowest": 1}
            p = pri_map.get(t.priority, 4)
            score += p
            reasons.append(f"priority {t.priority}: +{p}")

        # Age
        age = _days_ago(t.created_at)
        age_score = min(age, 10) * 0.6
        score += age_score
        reasons.append(f"age {age:.1f}d: +{age_score:.1f}")

        # No progress / no comments
        if (t.comments_count or 0) == 0:
            score += 3.0
            reasons.append("no comments: +3.0")

        # Blockers
        if t.blocking_count:
            b = min(t.blocking_count, 5) * 1.5
            score += b
            reasons.append(f"blocks {t.blocking_count}: +{b:.1f}")

        # CVE boost
        if "cve" in (t.summary or "").lower() or any("cve" in lb.lower() for lb in (t.labels or [])):
            score += 5.0
            reasons.append("security/CVE: +5.0")

        # VIP boost
        if any(lb.lower() in ("vip","ceo","exec") for lb in (t.labels or [])):
            score += 4.0
            reasons.append("exec mention: +4.0")

        return score, reasons
