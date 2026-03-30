import os
import json
from solcx import compile_standard, install_solc
from web3 import Web3


install_solc("0.8.0")


w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

if not w3.is_connected():
    raise Exception("❌ Could not connect to Ganache")

account = w3.eth.accounts[0]

print("Connected to Ganache")
print("Using Account:", account)

# ==========================
# LOAD CONTRACT FILE
# ==========================
current_dir = os.path.dirname(os.path.abspath(__file__))
contract_path = os.path.join(current_dir, "../blockchain/CarbonCredit.sol")

with open(contract_path, "r") as file:
    contract_source = file.read()

# ==========================
# COMPILE CONTRACT
# ==========================
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "CarbonCredit.sol": {
                "content": contract_source
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode"]
                }
            }
        },
    },
    solc_version="0.8.0",
)

abi = compiled_sol["contracts"]["CarbonCredit.sol"]["CarbonCredit"]["abi"]
bytecode = compiled_sol["contracts"]["CarbonCredit.sol"]["CarbonCredit"]["evm"]["bytecode"]["object"]

# ==========================
# DEPLOY CONTRACT
# ==========================
CarbonContract = w3.eth.contract(abi=abi, bytecode=bytecode)

tx_hash = CarbonContract.constructor().transact({
    "from": account,
    "gas": 3000000
})

tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress

print("✅ Contract Deployed Successfully!")
print("📍 Contract Address:", contract_address)

# ==========================
# SAVE ABI + ADDRESS
# ==========================
output_path = os.path.join(current_dir, "contract_data.json")

with open(output_path, "w") as f:
    json.dump({
        "abi": abi,
        "address": contract_address
    }, f, indent=4)

print("📄 contract_data.json saved inside blockchain folder")