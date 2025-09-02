from __future__ import annotations
import os, json, uuid
from typing import Optional
from .models import Session, Exchange

SESSION_FILE = os.path.join(os.path.dirname(__file__), "..", ".pta_session.json")

class ChatSession:
    def __init__(self):
        self.session: Optional[Session] = None

    def start_session(self) -> Session:
        if os.path.exists(SESSION_FILE):
            try:
                data = json.load(open(SESSION_FILE, "r", encoding="utf-8"))
                self.session = Session.model_validate(data)
                return self.session
            except Exception:
                pass
        self.session = Session(id=str(uuid.uuid4()))
        self._save()
        return self.session

    def handle_user_input(self, text: str) -> str:
        self.remember_context(Exchange(role="user", text=text))
        # This is a placeholder; the main interactive flow lives in assistant.py
        reply = "Noted. Let's proceed."
        self.remember_context(Exchange(role="assistant", text=reply))
        return reply

    def remember_context(self, exchange: Exchange) -> None:
        if not self.session:
            self.start_session()
        self.session.exchanges.append(exchange)
        self._save()

    def suggest_follow_up(self):
        return ["Want me to draft a status comment?", "Shall I generate a checklist?"]

    def _save(self):
        if not self.session: return
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(self.session.model_dump(), f, indent=2, default=str)
