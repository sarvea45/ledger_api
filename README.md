
---

# Professional Double-Entry Ledger API

This project is a robust financial ledger API built with **FastAPI** and **PostgreSQL**. It serves as a secure backend for banking applications, implementing the core principles of double-entry bookkeeping and ensuring absolute data integrity through ACID-compliant transactions. 

## 🚀 Quick Start

### 1. Prerequisites

* 
**Docker and Docker Compose** 


* **Python 3.11+**

### 2. Launch the Database

```powershell
docker-compose up -d

```

> This initializes a PostgreSQL 16 container with the database name `bank_ledger`. 
> 
> 

### 3. Install Dependencies

```powershell
pip install -r requirements.txt

```

### 4. Run the API

```powershell
uvicorn main:app --reload

```

### 5. Validate the System

Run the automated grading script to verify ACID properties and concurrency:

```powershell
python test_ledger.py

```

---

## 🏗 Architecture & Design Decisions

### 1. Double-Entry Bookkeeping Model

Every financial movement is recorded as an immutable set of balanced ledger entries. 

* 
**Transfer Logic**: A single transfer generates exactly two entries: a negative amount (debit) for the source and a positive amount (credit) for the destination. 


* 
**Auditability**: By linking entries to a unique `transaction_id`, the system provides a verifiable trail where the sum of entries for any transfer is always zero. 



### 2. ACID Transactions & Concurrency

* 
**Atomicity**: All database operations for a transaction (creating the transaction record and the corresponding ledger entries) are wrapped in a `db.begin()` block. If any step fails, the entire operation rolls back. 


* 
**Isolation & Locking**: We utilize **Row-Level Locking** via `.with_for_update()`. This prevents race conditions by locking the specific account rows during a transfer, ensuring that the balance cannot be changed by another process between the "check" and "write" phases. 



### 3. Balance Integrity

* 
**On-Demand Calculation**: The system strictly follows the requirement that balance must not be a stored column. It is calculated by summing all ledger entries for an account in real-time. 


* 
**Overdraft Prevention**: Before committing any debit, the system calculates the balance within the locked transaction. If the resulting balance would be negative, the transaction is rejected with an HTTP 422 error. 



### 4. Data Immutability

Ledger entries are append-only. The API does not expose `UPDATE` or `DELETE` endpoints for the `ledger_entries` table, ensuring the transaction history remains a permanent source of truth. 

---

## 📊 Database Schema (ERD)

* 
**Accounts**: Stores unique identifiers, user associations, and account status (active/frozen). 


* 
**Transactions**: Represents the intent and type of movement (transfer, deposit, withdrawal). 


* 
**Ledger Entries**: The immutable record of every credit and debit, linked to both accounts and transactions. 



---

## 🛠 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/accounts` | Create a new user account. 

 |
| `GET` | `/accounts/{id}` | Retrieve account details and current calculated balance. 

 |
| `POST` | `/transfers` | Execute an atomic transfer between two accounts. 

 |
| `POST` | `/deposits` | Simulate a deposit into an account. 

 |
| `GET` | `/accounts/{id}/ledger` | Fetch a chronological list of all ledger entries for an account. 

 |

---

## ✅ Verification Results

The system successfully passed the `test_ledger.py` suite:

* **Overdraft Prevention**: Correctly blocked transfers exceeding the available balance with HTTP 422.
* **ACID Concurrency**: Successfully handled simultaneous requests using row-locks; in a test of 4 simultaneous $40 transfers from a $100 balance, exactly 2 succeeded and 2 failed.
* **Math Integrity**: Final audit confirmed the total system balance remained consistent with zero leakage ($20 remaining in Account A, $80 transferred to Account B).

---

