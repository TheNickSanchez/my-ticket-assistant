from __future__ import annotations
from typing import List, Optional
from .models import Ticket, CVEDetails, Script
from config.settings import SETTINGS

class LLMClient:
    def analyze(self, tickets: List[Ticket]) -> str:
        provider = SETTINGS.llm_provider
        if provider == "openai":
            return self._openai_analyze(tickets)
        if provider == "ollama":
            return self._ollama_analyze(tickets)
        return self._stub_analyze(tickets)

    def research_cve(self, cve_id: str) -> CVEDetails:
        provider = SETTINGS.llm_provider
        if provider == "openai":
            return self._openai_research_cve(cve_id)
        if provider == "ollama":
            return self._ollama_research_cve(cve_id)
        return self._stub_research_cve(cve_id)

    def draft_comment(self, ticket: Ticket, summary: str) -> str:
        if SETTINGS.llm_provider == "stub":
            return f"""Update on {ticket.key}: Investigated and prepared a remediation plan. Key points:
- Scope: {ticket.summary}
- Plan: audit configuration, implement fix, add tests, communicate status
- Next: executing the first checklist item now.
"""
        # Simple template for real models; keep it deterministic
        return f"Status update for {ticket.key}: {summary.strip()}"

    def generate_script(self, requirements: str) -> Script:
        if SETTINGS.llm_provider == "stub":
            content = f"""#!/usr/bin/env python3
""""Auto-generated script (stub)"""
import sys, subprocess

def main():
    print('Running audit based on requirements:')
    print({requirements!r})
    # TODO: implement real checks and actions
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
"""
            return Script(filename="auto_script.py", content=content)

        # For real models we still template to keep things predictable
        content = f"""#!/usr/bin/env python3
""""Auto-generated script"""
# Requirements:
# {requirements}

def main():
    print('Executing generated steps...')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
"""
        return Script(filename="auto_script.py", content=content)

    # --- provider impls (lightweight, not calling heavy APIs here) ---
    def _stub_analyze(self, tickets: List[Ticket]) -> str:
        lines = []
        for t in tickets[:3]:
            lines.append(f"- {t.key}: {t.summary}")
        return "\n".join(lines) or "No tickets to analyze."

    def _openai_analyze(self, tickets: List[Ticket]) -> str:
        # Minimal placeholder to avoid hard dependency at runtime
        return self._stub_analyze(tickets)

    def _ollama_analyze(self, tickets: List[Ticket]) -> str:
        return self._stub_analyze(tickets)

    def _stub_research_cve(self, cve_id: str) -> CVEDetails:
        return CVEDetails(
            cve_id=cve_id,
            title=f"Research summary for {cve_id} (stub)",
            description="Authentication bypass via lax SAML response validation.",
            severity="Critical",
            affected_components=["SSO", "SAML"],
            affected_versions=["2.1","2.2","2.3"],
            mitigation="Enable strict SAML response validation and signature checks.",
            remediation="Upgrade to 2.4+ and add negative tests for malformed assertions.",
            test_steps=[
                "Attempt login with malformed SAML response (expect rejection)",
                "Run regression suite for auth flows",
            ],
            references=["https://example.invalid/{cve_id}"]
        )

    def _openai_research_cve(self, cve_id: str) -> CVEDetails:
        return self._stub_research_cve(cve_id)  # Replace with real call if desired

    def _ollama_research_cve(self, cve_id: str) -> CVEDetails:
        return self._stub_research_cve(cve_id)
