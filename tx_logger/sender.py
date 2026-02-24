"""
sender.py

Purpose:
Sends transactions on Sepolia and logs metadata.
Does NOT track confirmations.

Output:
data/sent_transactions.csv
"""

import os
import csv
import time
import random
from web3 import Web3
from datetime import datetime
from dotenv import load_dotenv

# =========================
# CONFIG
# =========================

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CHAIN_ID = 11155111  # Sepolia
TOTAL_TRANSACTIONS = 500  # Change as needed
CSV_PATH = "data/sent_transactions.csv"

# =========================
# WEB3 SETUP
# =========================

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

print("Using RPC:", RPC_URL)
print("Wallet address:", address)

# =========================
# FILE SETUP
# =========================

os.makedirs("data", exist_ok=True)

# Create CSV header if file does not exist
if not os.path.isfile(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rpc_url",
            "send_time",
            "tx_hash",
            "nonce",
            "gas_price"
        ])

# =========================
# TRANSACTION LOOP
# =========================

nonce = w3.eth.get_transaction_count(account.address)

for i in range(TOTAL_TRANSACTIONS):

    try:
        print(f"\nSending transaction {i+1}/{TOTAL_TRANSACTIONS}")

        tx = {
            "nonce": nonce,
            "to": address,  # self-transfer for experiment
            "value": 0,
            "gas": 21000,
            "gasPrice": w3.eth.gas_price,
            "chainId": CHAIN_ID,
        }

        send_time = datetime.utcnow()

        signed_tx = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print("Transaction sent:", tx_hash.hex())

        # Log send data
        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                RPC_URL,
                send_time.isoformat(),
                tx_hash.hex(),
                nonce,
                tx["gasPrice"]
            ])

        print("Data logged.")

        nonce += 1

        # Random sleep between 30–35 seconds (original code had 5–10 minutes comment)
        sleep_time = random.randint(30, 35)
        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

    except Exception as e:
        print("Error occurred:", e)
        print("Retrying in 60 seconds...")
        time.sleep(60)

print("\nFinished sending transactions.")
