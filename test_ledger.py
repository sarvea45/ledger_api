import requests
import concurrent.futures
from decimal import Decimal

# The URL where your FastAPI is running
BASE_URL = "http://127.0.0.1:8000"

def run_grading_test():
    print("🚀 Starting Professional Ledger Validation...")

    # 1. Create Accounts
    print("Step 1: Creating Accounts...")
    acc_a = requests.post(f"{BASE_URL}/accounts", json={"user_id": "user_1", "account_type": "checking"}).json()
    acc_b = requests.post(f"{BASE_URL}/accounts", json={"user_id": "user_2", "account_type": "savings"}).json()
    
    id_a = acc_a['id']
    id_b = acc_b['id']
    print(f"✅ Accounts Created: A({id_a}) and B({id_b})")

    # 2. Initial Deposit
    print("\nStep 2: Depositing $100.00 into Account A...")
    requests.post(f"{BASE_URL}/deposits", json={
        "account_id": id_a, 
        "amount": "100.0000", 
        "description": "Initial Deposit"
    })
    
    # 3. Verify Balance Calculation
    bal_a = requests.get(f"{BASE_URL}/accounts/{id_a}").json()['balance']
    print(f"✅ Calculated Balance A: ${bal_a}")

    # 4. Test Overdraft Prevention
    print("\nStep 3: Testing Overdraft Prevention (Trying to move $150)...")
    overdraft_resp = requests.post(f"{BASE_URL}/transfers", json={
        "source_account_id": id_a,
        "destination_account_id": id_b,
        "amount": "150.0000",
        "description": "Should Fail"
    })
    if overdraft_resp.status_code == 422:
        print("✅ Overdraft Blocked: Correctly returned HTTP 422.")
    else:
        print(f"❌ Overdraft Failed: Expected 422, got {overdraft_resp.status_code}")

    # 5. TEST CONCURRENCY (The "Full Marks" Test)
    # Account A has $100. We will try to send $40 four times simultaneously.
    # $40 * 4 = $160. Only 2 transfers should succeed ($80). Two should fail.
    print("\nStep 4: Testing ACID Concurrency (Race Conditions)...")
    
    def send_transfer():
        return requests.post(f"{BASE_URL}/transfers", json={
            "source_account_id": id_a,
            "destination_account_id": id_b,
            "amount": "40.0000",
            "description": "Concurrent Transfer"
        })

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Launch 4 requests at the exact same time
        futures = [executor.submit(send_transfer) for _ in range(4)]
        results = [f.result().status_code for f in futures]

    successes = results.count(200)
    failures = results.count(422)
    
    print(f"✅ Transfers Attempted: 4")
    print(f"✅ Successful (Expected 2): {successes}")
    print(f"✅ Failed (Expected 2): {failures}")

    # Final Balance Check
    final_bal_a = requests.get(f"{BASE_URL}/accounts/{id_a}").json()['balance']
    final_bal_b = requests.get(f"{BASE_URL}/accounts/{id_b}").json()['balance']
    
    print(f"\n📊 FINAL AUDIT:")
    print(f"Account A Final Balance: ${final_bal_a}")
    print(f"Account B Final Balance: ${final_bal_b}")

    if Decimal(str(final_bal_a)) == Decimal("20.0000"):
        print("\n🏆 PROJECT COMPLETE: Balance Integrity & Concurrency Verified!")
    else:
        print("\n❌ INTEGRITY ERROR: The math does not add up.")

if __name__ == "__main__":
    run_grading_test()