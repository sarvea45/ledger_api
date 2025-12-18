from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
import models, schemas, database

# 1. Initialize the FastAPI app (This fixes your NameError)
app = FastAPI(title="Double-Entry Ledger API")

# 2. Ensure tables are created on startup
@app.on_event("startup")
def init_tables():
    models.Base.metadata.create_all(bind=database.engine)

# 3. Helper to calculate balance from the ledger (On-Demand)
def calculate_balance(db: Session, account_id: str) -> Decimal:
    res = db.query(func.sum(models.LedgerEntry.amount)).filter(models.LedgerEntry.account_id == account_id).scalar()
    return Decimal(res or 0)

@app.post("/accounts")
def create_account(acc: schemas.AccountCreate, db: Session = Depends(database.get_db)):
    new_acc = models.Account(**acc.model_dump())
    db.add(new_acc)
    db.commit()
    db.refresh(new_acc)
    return new_acc

@app.get("/accounts/{account_id}")
def get_account(account_id: str, db: Session = Depends(database.get_db)):
    acc = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not acc: raise HTTPException(404, "Account not found")
    return {"id": acc.id, "balance": calculate_balance(db, account_id)}

@app.post("/deposits")
def deposit(req: schemas.TransactionRequest, db: Session = Depends(database.get_db)):
    try:
        with db.begin():
            tx = models.Transaction(type="deposit", description=req.description)
            db.add(tx)
            db.flush()
            db.add(models.LedgerEntry(account_id=req.account_id, transaction_id=tx.id, amount=req.amount))
        return {"status": "deposited"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transfers")
def transfer_funds(req: schemas.TransferCreate, db: Session = Depends(database.get_db)):
    try:
        with db.begin():
            # ACID: Acquire row-level locks
            src = db.query(models.Account).with_for_update().filter(models.Account.id == req.source_account_id).first()
            dst = db.query(models.Account).with_for_update().filter(models.Account.id == req.destination_account_id).first()
            
            if not src or not dst:
                raise HTTPException(404, "One or both accounts not found")

            if calculate_balance(db, req.source_account_id) < req.amount:
                raise HTTPException(422, "Insufficient funds")

            tx = models.Transaction(type="transfer", description=req.description)
            db.add(tx); db.flush()

            # Double-Entry: One Debit, One Credit
            db.add(models.LedgerEntry(account_id=src.id, transaction_id=tx.id, amount=-req.amount))
            db.add(models.LedgerEntry(account_id=dst.id, transaction_id=tx.id, amount=req.amount))
        return {"status": "success"}
    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(500, detail=str(e))

@app.get("/accounts/{account_id}/ledger")
def get_ledger(account_id: str, db: Session = Depends(database.get_db)):
    return db.query(models.LedgerEntry).filter(models.LedgerEntry.account_id == account_id).all()