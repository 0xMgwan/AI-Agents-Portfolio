import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Celo Network RPC (Alfajores Testnet)
CELO_RPC_URL = "https://alfajores-forno.celo-testnet.org"
web3 = Web3(Web3.HTTPProvider(CELO_RPC_URL))

# Wallet setup
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = web3.eth.account.from_key(PRIVATE_KEY)
ACCOUNT_ADDRESS = ACCOUNT.address

# Smart contract address & ABI (Replace with your deployed contract)
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
with open("abi.json", "r") as file:
    CONTRACT_ABI = json.load(file)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# AI-Driven Savings & Loan Automation

def check_balance():
    """Fetch user's savings, shares, and loan balance"""
    member = contract.functions.members(ACCOUNT_ADDRESS).call()
    shares, savings, loan, isMember = member
    print(f"Shares: {shares}, Savings: {web3.fromWei(savings, 'ether')} cUSD, Loan: {web3.fromWei(loan, 'ether')} cUSD")
    return shares, savings, loan

def purchase_shares(amount):
    """Buy shares with a portion allocated to savings"""
    tx = contract.functions.purchaseShares(amount).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'value': web3.toWei(amount, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    })
    send_transaction(tx)

def apply_for_loan(amount):
    """Apply for a loan based on shareholding"""
    tx = contract.functions.applyForLoan(web3.toWei(amount, 'ether')).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'gas': 2000000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    })
    send_transaction(tx)

def repay_loan():
    """Automatically repay loan if due"""
    _, _, loan = check_balance()
    if loan > 0:
        tx = contract.functions.repayLoan().build_transaction({
            'from': ACCOUNT_ADDRESS,
            'value': loan,
            'gas': 2000000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        })
        send_transaction(tx)

def send_transaction(tx):
    """Sign and send a transaction"""
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"Transaction sent: {tx_hash.hex()}")
    return tx_hash.hex()

# AI Decision-making Example: Auto-Repay Loan if Savings are Sufficient
while True:
    shares, savings, loan = check_balance()

    # Auto-repay loan if savings are greater than loan amount
    if loan > 0 and savings >= loan:
        print("💡 Auto-repaying loan...")
        repay_loan()

    # Sleep before checking again (e.g., every 5 minutes)
    time.sleep(300)
