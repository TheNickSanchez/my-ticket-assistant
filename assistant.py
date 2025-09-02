from __future__ import annotations
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from src.config.settings import SETTINGS
from src.ticket_fetcher import TicketFetcher
from src.work_assistant import WorkAssistant
from src.action_handler import ActionHandler
from src.chat_session import ChatSession
from src.models import Ticket

console = Console()

def _print_header(tickets_count: int):
    console.print(Panel.fit(f"[bold]Good morning![/bold] I pulled your [bold]{tickets_count}[/bold] open tickets.", title="🎯 Personal Ticket Assistant"))

def _print_priorities(ordered):
    table = Table(title="Prioritized Tickets", show_lines=False)
    table.add_column("Key", style="bold cyan")
    table.add_column("Summary", overflow="fold")
    table.add_column("Score", justify="right")
    table.add_column("Why", overflow="fold")
    for wi in ordered[:6]:
        table.add_row(wi.ticket.key, wi.ticket.summary, f"{wi.score:.1f}", "; ".join(wi.reasons))
    console.print(table)

@click.command()
@click.option("--ticket", "focus_ticket", type=str, help="Focus a specific ticket key (e.g., ABC-123)")
@click.option("--continue", "resume", is_flag=True, help="Resume previous session conversation")
def main(focus_ticket: str, resume: bool):
    sess = ChatSession(); sess.start_session()
    fetcher = TicketFetcher()
    assistant = WorkAssistant()
    actor = ActionHandler()

    tickets = fetcher.get_my_active_tickets()
    if focus_ticket:
        tickets = [t for t in tickets if t.key == focus_ticket] or tickets

    _print_header(len(tickets))

    analysis = assistant.analyze_workload(tickets)
    _print_priorities(analysis.ordered)

    top = analysis.ordered[0].ticket if analysis.ordered else None
    if not top:
        console.print("No tickets found. You're all clear!", style="green")
        return

    # Narrative summary
    console.print(Panel.fit(Markdown(f"""**Top Priority:** **{top.key}** — {top.summary}

**My take:**  
- Impact: inferred from priority/labels  
- Complexity: estimated medium unless marked otherwise  
- Next step: If this involves a CVE or auth issue, start with a configuration audit.

Shall I:
1. Research the CVE and create a remediation checklist  
2. Draft a technical investigation plan  
3. Prepare a status comment for the ticket

Type [bold]1[/bold]/[bold]2[/bold]/[bold]3[/bold] or "skip".
"""), title="Assistant Analysis"))

    choice = input("> ").strip().lower()

    if choice in ("1","research","cve") and "cve" in top.summary.lower():
        # Extract CVE id in a simple way
        words = [w.strip(".,;:()[]{}") for w in top.summary.split()]
        cve_id = next((w for w in words if w.upper().startswith("CVE-")), "CVE-UNKNOWN")
        details = actor.research_cve(cve_id)
        brief = f"""# {details.cve_id}: {details.title}

**Severity:** {details.severity}
**Affected components:** {', '.join(details.affected_components) or 'N/A'}
**Affected versions:** {', '.join(details.affected_versions) or 'N/A'}

## Description
{details.description}

## Mitigation
{details.mitigation or 'TBD'}

## Remediation
{details.remediation or 'TBD'}

## Test steps
- {'\n- '.join(details.test_steps)}

## References
- {'\n- '.join(details.references)}
"""
        actor.create_file(brief, f"{details.cve_id.lower()}-brief.md")
        console.print(f"Created technical brief: artifacts/{details.cve_id.lower()}-brief.md", style="green")

        script = actor.generate_script("Audit current SSO/SAML configuration and enforce strict validation.")
        actor.create_file(script.content, script.filename)
        console.print(f"Generated script: artifacts/{script.filename}", style="green")

        comment = f"Prepared {details.cve_id} brief and generated audit script. Starting with configuration audit and adding negative tests for malformed SAML responses."
        actor.post_jira_comment(top.key, comment)
        console.print("Status comment posted (or dry-run simulated).", style="green")

    elif choice in ("2","plan"):
        plan = f"""# Investigation Plan for {top.key}
- Scope and reproduce issue
- Gather logs and affected components
- Formulate hypotheses and design tests
- Implement fix, add regression tests
- Communicate status updates in Jira
"""
        actor.create_file(plan, f"{top.key.lower()}-investigation-plan.md")
        console.print(f"Created: artifacts/{top.key.lower()}-investigation-plan.md", style="green")

    elif choice in ("3","comment"):
        comment = f"Initial assessment completed for {top.key}. Drafting plan and starting execution steps."
        actor.post_jira_comment(top.key, comment)
        console.print("Status comment posted (or dry-run simulated).", style="green")
    else:
        console.print("Okay, skipping automated actions for now.")

    console.print(Panel.fit("Great work! Ready for the next one when you are.", title="✅ Progress"))

if __name__ == "__main__":
    main()
