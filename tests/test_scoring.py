from src.work_assistant import WorkAssistant
from src.models import Ticket
from datetime import datetime, timedelta

def test_scoring_simple():
    wa = WorkAssistant()
    t = Ticket(id="1", key="ABC-1", summary="CVE-2024-1984 auth bypass", priority="High", created_at=datetime.utcnow()-timedelta(days=3))
    score, reasons = wa._score_ticket(t)
    assert score > 0
    assert any("CVE".lower() in r.lower() for r in reasons)
