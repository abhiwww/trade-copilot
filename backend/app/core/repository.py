from __future__ import annotations
import uuid
from pathlib import Path
from typing import Any, List, Optional, Type, TypeVar, Generic
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.models.trade_models import User, Organization, TradeCase, Document, Notification, Conversation, Message
from app.db.models.trade_models import (
    Organization as OrgModel,
    User as UserModel,
    TradeCase as CaseModel,
    Document as DocModel,
    Notification as NotifModel,
    Conversation as ConvoModel,
    Message as MsgModel
)

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

T = TypeVar("T")
M = TypeVar("M") # SQLAlchemy Model

class BaseRepository(Generic[T, M]):
    def __init__(self, session: AsyncSession, model_class: Type[M], domain_class: Type[T]):
        self.session = session
        self.model_class = model_class
        self.domain_class = domain_class

    async def get_all(self) -> List[T]:
        result = await self.session.execute(select(self.model_class))
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def get_by_id(self, id: str) -> Optional[T]:
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, id: str, item: Any):
        existing = await self.get_by_id(id)

        if existing:
            # Update existing record
            data = item.__dict__ if hasattr(item, '__dict__') else item
            data.pop('id', None)
            data.pop('user_id', None)
            data.pop('org_id', None)

            await self.session.execute(
                update(self.model_class)
                .where(self.model_class.id == id)
                .values(**data)
            )
        else:
            # Create new record - map domain fields to DB fields
            data = dict(item.__dict__ if hasattr(item, '__dict__') else item)

            # Remove domain-specific ID fields
            for field in ['user_id', 'org_id', 'case_id', 'document_id', 'notification_id', 'conversation_id', 'message_id']:
                data.pop(field, None)
            data['id'] = id

            # Only include fields that exist in the DB model
            valid_fields = {c.name for c in self.model_class.__table__.columns}
            data = {k: v for k, v in data.items() if k in valid_fields}

            model_instance = self.model_class(**data)
            self.session.add(model_instance)

    async def delete(self, id: str):
        await self.session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )

    def _to_domain(self, model: Any) -> T:
        """
        Converts a SQLAlchemy model instance to a domain dataclass.
        """
        # Extract all attributes that are not internal SQLAlchemy state
        data = {
            c.name: getattr(model, c.name)
            for c in model.__table__.columns
        }
        # Handle any specific mappings (e.g. id -> user_id)
        if hasattr(self.domain_class, 'user_id') and 'id' in data:
            data['user_id'] = data.pop('id')
        if hasattr(self.domain_class, 'org_id') and 'id' in data:
            data['org_id'] = data.pop('id')
        if hasattr(self.domain_class, 'case_id') and 'id' in data:
            data['case_id'] = data.pop('id')
        if hasattr(self.domain_class, 'conversation_id') and 'id' in data:
            data['conversation_id'] = data.pop('id')
        if hasattr(self.domain_class, 'notification_id') and 'id' in data:
            data['notification_id'] = data.pop('id')
        if hasattr(self.domain_class, 'document_id') and 'id' in data:
            data['document_id'] = data.pop('id')
        if hasattr(self.domain_class, 'message_id') and 'id' in data:
            data['message_id'] = data.pop('id')

        return self.domain_class(**data)

class UserRepository(BaseRepository[User, UserModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel, User)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

class OrganizationRepository(BaseRepository[Organization, OrgModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, OrgModel, Organization)

class TradeCaseRepository(BaseRepository[TradeCase, CaseModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CaseModel, TradeCase)

    async def get_by_org(self, org_id: str) -> List[TradeCase]:
        result = await self.session.execute(
            select(CaseModel).where(CaseModel.org_id == org_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

class DocumentRepository(BaseRepository[Document, DocModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, DocModel, Document)

    async def get_by_case(self, case_id: str) -> List[Document]:
        result = await self.session.execute(
            select(DocModel).where(DocModel.case_id == case_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def get_by_hash(self, file_hash: str, org_id: str) -> Optional[Document]:
        result = await self.session.execute(
            select(DocModel).where(
                DocModel.hash == file_hash,
                DocModel.org_id == org_id
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

class NotificationRepository(BaseRepository[Notification, NotifModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, NotifModel, Notification)

    async def get_by_user(self, user_id: str) -> List[Notification]:
        result = await self.session.execute(
            select(NotifModel).where(NotifModel.user_id == user_id)
        )
        return [self._to_domain(m) for m in result.scalars().all()]

class ConversationRepository(BaseRepository[Conversation, ConvoModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ConvoModel, Conversation)

    async def get_by_org(self, org_id: str) -> List[Conversation]:
        result = await self.session.execute(
            select(ConvoModel)
            .where(ConvoModel.org_id == org_id)
            .order_by(ConvoModel.updated_at.desc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

class MessageRepository(BaseRepository[Message, MsgModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MsgModel, Message)

    async def get_by_conversation(self, conversation_id: str) -> List[Message]:
        result = await self.session.execute(
            select(MsgModel)
            .where(MsgModel.conversation_id == conversation_id)
            .order_by(MsgModel.created_at.asc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

# Repository Container to handle session injection
class RepositoryContainer:
    def __init__(self, session: AsyncSession):
        self.users = UserRepository(session)
        self.orgs = OrganizationRepository(session)
        self.cases = TradeCaseRepository(session)
        self.docs = DocumentRepository(session)
        self.notifications = NotificationRepository(session)
        self.conversations = ConversationRepository(session)
        self.messages = MessageRepository(session)
