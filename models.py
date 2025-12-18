from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from database import Base

# Account Status as required by the Core Requirements
class AccountStatus(enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"

# Transaction Status to track the lifecycle of a transfer/deposit/withdrawal
class TransactionStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class Account(Base):
    __tablename__ = "accounts"
    
    # Balance must not be a stored column; calculated on-demand [cite: 5, 27, 36]
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    account_type = Column(String, nullable=False) # e.g., checking, savings [cite: 6, 15]
    currency = Column(String, default="USD") # [cite: 6, 15]
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE) # [cite: 16]

    # Relationship to ledger for easier querying
    ledger_entries = relationship("LedgerEntry", back_populates="account")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String) # transfer, deposit, withdrawal [cite: 19]
    description = Column(String) # [cite: 19]
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED)
    created_at = Column(DateTime, default=datetime.utcnow) # [cite: 19]

    # A transaction links the pair of ledger entries [cite: 52, 53]
    entries = relationship("LedgerEntry", back_populates="transaction")

class LedgerEntry(Base):
    """
    An immutable record of a single credit or debit. 
    Entries cannot be updated or deleted. 
    """
    __tablename__ = "ledger_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False) # [cite: 22]
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False) # [cite: 22]
    
    # High-precision numeric type to avoid floating-point errors [cite: 21, 23, 25]
    amount = Column(Numeric(19, 4), nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow) # [cite: 23]

    # Relationships
    account = relationship("Account", back_populates="ledger_entries")
    transaction = relationship("Transaction", back_populates="entries")