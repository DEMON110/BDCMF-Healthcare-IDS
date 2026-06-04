"""
deploy_sepolia.py
Deploy BDCMF smart contracts to Sepolia testnet.
"""
import os
import json
import time
from web3 import Web3
from eth_account import Account

SEPOLIA_RPC = os.getenv("SEPOLIA_RPC", "https://rpc.sepolia.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))
assert w3.is_connected(), "Failed to connect to Sepolia"

account = Account.from_key(PRIVATE_KEY)
ADDRESS = account.address

# Load compiled contract
with open("contracts/compiled/ConsentRegistry_abi.json") as f:
    ABI = json.load(f)
with open("contracts/compiled/ConsentRegistry_bytecode.txt") as f:
    BYTECODE = f.read().strip()

Contract = w3.eth.contract(abi=ABI, bytecode=BYTECODE)

def deploy_contract(name):
    tx = Contract.constructor().build_transaction({
        'from': ADDRESS,
        'nonce': w3.eth.get_transaction_count(ADDRESS),
        'gas': 2000000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'chainId': 11155111
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    print(f"[{name}] Deployed at {receipt.contractAddress} | Tx: {tx_hash.hex()} | Gas: {receipt.gasUsed}")
    return receipt.contractAddress, receipt.gasUsed, receipt.blockNumber

def measure_transaction(contract_address, func_name, *args):
    contract = w3.eth.contract(address=contract_address, abi=ABI)
    func = getattr(contract.functions, func_name)
    tx = func(*args).build_transaction({
        'from': ADDRESS,
        'nonce': w3.eth.get_transaction_count(ADDRESS),
        'gas': 500000,
        'gasPrice': w3.to_wei('10', 'gwei'),
        'chainId': 11155111
    })
    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    start = time.time()
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    latency = time.time() - start
    return receipt.gasUsed, latency

if __name__ == "__main__":
    import pandas as pd
    os.makedirs("results/tables", exist_ok=True)

    addr, gas, block = deploy_contract("ConsentRegistry")

    # Measure operations
    results = []
    for op, args in [
        ("registerPatient", (b'patient1',)),
        ("registerProvider", (b'provider1',)),
        ("requestConsent", (ADDRESS, b'vitals', b'research', 86400)),
    ]:
        g, lat = measure_transaction(addr, op, *args)
        results.append({'Operation': op, 'Gas': g, 'Latency_s': lat})

    pd.DataFrame(results).to_csv("results/tables/sepolia_gas.csv", index=False)
    print("Sepolia metrics saved.")
