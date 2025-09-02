from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Ticket(BaseModel):
    id: str
    key: str
    summary: str
    priority: Optional[str] = None
    severity: Optional[int] = None  # 1 (highest) .. 5 (lowest)
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    comments_count: int = 0
    labels: List[str] = []
    issue_type: Optional[str] = None
    blocking_count: int = 0
    reporter: Optional[str] = None
    assignee: Optional[str] = None

class TicketDetail(Ticket):
    description: Optional[str] = None
    links: List[str] = []
    dependencies: List[str] = []

class WorkItem(BaseModel):
    ticket: Ticket
    score: float
    reasons: List[str]

class WorkloadAnalysis(BaseModel):
    ordered: List[WorkItem]
    summary: str

class Action(BaseModel):
    name: str
    params: Dict[str, Any] = {}

class ActionSuggestion(BaseModel):
    message: str
    actions: List[Action]

class Result(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class CVEDetails(BaseModel):
    cve_id: str
    title: str
    description: str
    severity: str
    affected_components: List[str] = []
    affected_versions: List[str] = []
    mitigation: Optional[str] = None
    remediation: Optional[str] = None
    test_steps: List[str] = []
    references: List[str] = []

class Script(BaseModel):
    filename: str
    content: str

class Exchange(BaseModel):
    role: str
    text: str
    ts: datetime = Field(default_factory=datetime.utcnow)

class Session(BaseModel):
    id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    exchanges: List[Exchange] = []

