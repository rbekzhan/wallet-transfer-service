import uuid
import enum

from sqlalchemy import MetaData
from datetime import datetime
from sqlalchemy import (
    Table, Column, String, Numeric, DateTime, Boolean, Enum, ForeignKey, UniqueConstraint, Integer
)
from sqlalchemy.dialects.postgresql import UUID


metadata = MetaData()

VerifyCode = Table(
    "verify_code", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True),
    Column("phone_number", String, nullable=False),
    Column("code", String, nullable=False),
    Column("confirmed_client_code", String(4), nullable=True),
    Column("confirm_code", Boolean, nullable=False),
    Column("attempt_count", Integer, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, onupdate=datetime.utcnow)
)

UserTable = Table(
    "user", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True),
    Column("phone_number", String, nullable=False, unique=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, onupdate=datetime.utcnow),
)


class TxStatus(str, enum.Enum):
    created = "created"
    processing = "processing"
    completed = "completed"
    failed = "failed"


Accounts = Table(
    "accounts", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), nullable=False, index=True),
    Column("currency", String(3), nullable=False),
    Column("balance", Numeric(18, 4), nullable=False, default=0),
    Column("is_active", Boolean, default=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, onupdate=datetime.utcnow),
    UniqueConstraint("user_id", "currency", name="uix_user_currency"),
)


Transfers = Table(
    "transfers", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("from_account_id", UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False),
    Column("to_account_id", UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False),
    Column("source_amount", Numeric(18, 4), nullable=True),
    Column("target_amount", Numeric(18, 4), nullable=True),
    Column("rate_used", Numeric(18, 8), nullable=False),
    Column("fee_fixed", Numeric(18, 4), default=0),
    Column("fee_percent", Numeric(5, 2), default=0),
    Column("fee_amount", Numeric(18, 4), default=0),
    Column("status", Enum(TxStatus), default=TxStatus.created),
    Column("error", String, nullable=True),
    Column("idempotency_key", String(64), index=True),
    Column("created_at", DateTime, default=datetime.utcnow),
)

