from __future__ import annotations
import json
import os
import uuid
import bcrypt
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.core.repository import (
    UserRepository, OrganizationRepository, TradeCaseRepository,
    DocumentRepository, ConversationRepository, MessageRepository,
    users, orgs, cases, docs, conversations, messages
)

def create_org(name: str = "Test Org", plan: str = "Basic") -> Any:
    org_id = str(uuid.uuid4())
    from app.models.trade_models import Organization
    org = Organization(
        org_id=org_id,
        name=name,
        plan=plan,
        created_at=datetime.utcnow()
    )
    orgs.save(org_id, org)
    return org

def create_user(org_id: str, email: str = "test@example.com", role: str = "OWNER", password: str = "Password123!") -> Any:
    user_id = str(uuid.uuid4())
    from app.models.trade_models import User

    # Simple, direct bcrypt hashing
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = User(
        user_id=user_id,
        email=email,
        first_name="Test",
        last_name="User",
        password_hash=hashed_pw,
        org_id=org_id,
        role=role,
        created_at=datetime.utcnow()
    )
    users.save(user_id, user)
    return user

def create_case(org_id: str, title: str = "Test Case") -> Any:
    case_id = str(uuid.uuid4())
    from app.models.trade_models import TradeCase
    case = TradeCase(
        case_id=case_id,
        org_id=org_id,
        name=title,
        status="Open",
        origin={"country": "India"},
        destination={"country": "USA"},
        product="Test Product",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    cases.save(case_id, case)
    return case

def upload_test_doc(case_id: str, filename: str = "test.pdf", content: str = "This is test content") -> Any:
    doc_id = str(uuid.uuid4())
    from app.models.trade_models import Document

    from app.core.repository import DATA_DIR
    upload_dir = DATA_DIR / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / filename
    with open(file_path, "w") as f:
        f.write(content)

    doc = Document(
        document_id=doc_id,
        case_id=case_id,
        filename=filename,
        file_type="pdf",
        size_bytes=len(content),
        storage_path=str(file_path),
        status="Processed",
        uploaded_at=datetime.utcnow()
    )
    docs.save(doc_id, doc)
    return doc
