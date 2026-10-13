from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TenantMixin:
    """
    Mixin to enforce strict tenant isolation.
    Every table inheriting from this mixin must have an org_id.
    """
    org_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True
    )
