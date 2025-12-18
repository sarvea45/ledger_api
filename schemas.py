from pydantic import BaseModel, Field
from decimal import Decimal

class AccountCreate(BaseModel):
    user_id: str
    account_type: str
    currency: str = "USD"

class TransferCreate(BaseModel):
    source_account_id: str
    destination_account_id: str
    amount: Decimal = Field(gt=0)
    description: str

class TransactionRequest(BaseModel):
    account_id: str
    amount: Decimal = Field(gt=0)
    description: str