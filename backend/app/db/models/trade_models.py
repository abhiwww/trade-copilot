from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey, Table, Column, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import List, Optional, Any, Union
from app.db.base import Base, TenantMixin

class Organization(Base):
    __tablename__ = "organizations"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = mapped_column(String(255), nullable=False)
    plan = mapped_column(String(50), default="Enterprise")
    settings = mapped_column(JSON, default=dict)
    created_at = mapped_column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="organization")
    trade_cases = relationship("TradeCase", back_populates="organization")

class User(Base, TenantMixin):
    __tablename__ = "users"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = mapped_column(String(255), nullable=False, unique=True, index=True)
    first_name = mapped_column(String(100))
    last_name = mapped_column(String(100))
    password_hash = mapped_column(String(255), nullable=False)
    role = mapped_column(String(50))
    job_title = mapped_column(String(100))
    phone = mapped_column(String(50))
    timezone = mapped_column(String(50), default="UTC")
    language = mapped_column(String(10), default="en")
    created_at = mapped_column(DateTime, server_default=func.now())

    organization = relationship("Organization", back_populates="users")

class TradeCase(Base, TenantMixin):
    __tablename__ = "trade_cases"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = mapped_column(String(255), nullable=False)
    status = mapped_column(String(50), default="Draft")
    origin = mapped_column(JSON, nullable=False)
    destination = mapped_column(JSON, nullable=False)
    product = mapped_column(String(255))
    hs_code = mapped_column(String(50))
    created_at = mapped_column(DateTime, server_default=func.now())
    updated_at = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="trade_cases")
    documents = relationship("Document", back_populates="trade_case")

class Document(Base, TenantMixin):
    __tablename__ = "documents"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = mapped_column(String(36), ForeignKey("trade_cases.id"), nullable=False)
    filename = mapped_column(String(255), nullable=False)
    file_type = mapped_column(String(20))
    size_bytes = mapped_column(Integer)
    storage_path = mapped_column(String(512), nullable=False)
    status = mapped_column(String(50), default="Uploaded")
    document_type = mapped_column(String(100))
    uploaded_at = mapped_column(DateTime, server_default=func.now())
    hash = mapped_column(String(64), index=True)

    trade_case = relationship("TradeCase", back_populates="documents")

class Conversation(Base, TenantMixin):
    __tablename__ = "conversations"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    case_id = mapped_column(String(36), ForeignKey("trade_cases.id"), nullable=True)
    title = mapped_column(String(255), default="New Chat")
    created_at = mapped_column(DateTime, server_default=func.now())
    updated_at = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    messages = relationship("Message", back_populates="conversation")

class Message(Base, TenantMixin):
    __tablename__ = "messages"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = mapped_column(String(36), ForeignKey("conversations.id"), nullable=False)
    role = mapped_column(String(20), nullable=False)
    content = mapped_column(Text, nullable=False)
    findings = mapped_column(JSON, default=list)
    document_ids = mapped_column(JSON, default=list)
    created_at = mapped_column(DateTime, server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")

class Notification(Base, TenantMixin):
    __tablename__ = "notifications"
    __allow_unmapped__ = True

    id = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    type = mapped_column(String(100), nullable=False)
    title = mapped_column(String(255), nullable=False)
    message = mapped_column(Text, nullable=False)
    severity = mapped_column(String(50), nullable=False)
    is_read = mapped_column(Boolean, default=False)
    created_at = mapped_column(DateTime, server_default=func.now())

class ConversationDocument(Base):
    __tablename__ = "conversation_documents"
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), primary_key=True)
