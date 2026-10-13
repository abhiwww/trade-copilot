from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

@dataclass
class User:
    user_id: str
    email: str
    first_name: str
    last_name: str
    password_hash: str
    org_id: str
    role: str  # 'Owner', 'Admin', 'Trade Manager', 'Analyst', 'Reviewer', 'Viewer'
    job_title: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Organization:
    org_id: str
    name: str
    plan: str  # 'Basic', 'Pro', 'Enterprise'
    total_uploads: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TradeCase:
    case_id: str
    org_id: str
    name: str
    status: str  # 'Draft', 'Analyzing', 'Review', 'Completed'
    origin: Dict[str, str]  # {'country': 'India', 'state': '...', 'city': '...', 'port': '...'}
    destination: Dict[str, str]  # {'country': 'USA', 'state': '...', 'city': '...', 'port': '...'}
    product: str
    hs_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Document:
    document_id: str
    case_id: str
    filename: str
    file_type: str
    size_bytes: int
    storage_path: str
    status: str  # 'Uploaded', 'Processing', 'Processed', 'Failed'
    document_type: Optional[str] = None # 'commercial_invoice', 'packing_list', etc.
    uploaded_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Notification:
    notification_id: str
    user_id: str
    type: str  # 'FINDING_CREATED', 'DOCUMENT_PROCESSED', etc.
    title: str
    message: str
    severity: str # 'info', 'warning', 'critical'
    is_read: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ExtractedField:
    name: str
    value: Any
    normalized_value: Any
    confidence: float = 0.0
    page: Optional[int] = None
    source: str = "deterministic_parser"
    evidence_marker: Optional[Dict[str, Any]] = None  # {'bbox': [x, y, w, h], 'snippet': '...'}

@dataclass
class Evidence:
    evidence_id: str
    document_id: str
    field_name: str
    page: int
    bbox: List[float] # [x, y, width, height]
    snippet: str
    confidence: float
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class DocumentAnalysisResult:
    document_id: str
    document_type: str
    classification_confidence: float
    extracted_fields: List[ExtractedField] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    validation: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Conversation:
    conversation_id: str
    org_id: str
    user_id: str
    title: str = "New Chat"
    case_id: Optional[str] = None
    document_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Message:
    message_id: str
    conversation_id: str
    role: str  # 'user' | 'assistant'
    content: str
    findings: List[Dict[str, Any]] = field(default_factory=list)
    document_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ReconciliationFinding:
    category: str
    severity: str
    title: str
    description: str
    difference: Optional[float] = None
    evidence: List[str] = field(default_factory=list)
    confidence: float = 0.0
