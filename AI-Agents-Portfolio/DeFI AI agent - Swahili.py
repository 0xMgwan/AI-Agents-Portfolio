import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv

# Pakia mazingira
load_dotenv()

# Muunganisho wa Mtandao wa Celo
CELO_RPC_URL = "https://alfajores-forno.celo-testnet.org"
web3 = Web3(Web3.HTTPProvider(CELO_RPC_URL))

# Akaunti ya Mtumiaji
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT = web3.eth.account.from_key(PRIVATE_KEY)
ACCOUNT_ADDRESS = ACCOUNT.address

# Anwani ya Mkataba na ABI
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
with open("abi.json", "r") as file:
    CONTRACT_ABI = json.load(file)

contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Kazi za AI Agent
def angalia_saldo():
    """Hakikisha kiasi cha akiba, hisa, na mkopo"""
    mwanachama = contract.functions.members(ACCOUNT_ADDRESS).call()
    hisa, akiba, mkopo, niMwanachama = mwanachama
    print(f"Hisa: {hisa}, Akiba: {web3.fromWei(akiba, 'ether')} cUSD, Mkopo: {web3.fromWei(mkopo, 'ether')} cUSD")
    return hisa, akiba, mkopo

def nunua_hisa(kiasi):
    """Nunua hisa na sehemu itengewe akiba"""
    tx = contract.functions.purchaseShares(kiasi).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'value': web3.toWei(kiasi, 'ether'),
        'gas': 2000000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    })
    tuma_muamala(tx)

def omba_mkopo(kiasi):
    """Omba mkopo kulingana na hisa"""
    tx = contract.functions.applyForLoan(web3.toWei(kiasi, 'ether')).build_transaction({
        'from': ACCOUNT_ADDRESS,
        'gas': 2000000,
        'gasPrice': web3.eth.gas_price,
        'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    })
    tuma_muamala(tx)

def lipa_mkopo():
    """Lipa mkopo kiotomatiki ikiwa akiba inatosha"""
    _, akiba, mkopo = angalia_saldo()
    if mkopo > 0 and akiba >= mkopo:
        tx = contract.functions.repayLoan().build_transaction({
            'from': ACCOUNT_ADDRESS,
            'value': mkopo,
            'gas': 2000000,
            'gasPrice': web3.eth.gas_price,
            'nonce': web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        })
        tuma_muamala(tx)

def tuma_muamala(tx):
    """Saini na kutuma muamala"""
    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    print(f"✅ Muamala umetumwa: {tx_hash.hex()}")
    return tx_hash.hex()

# AI inafanya maamuzi kwa njia ya Kiswahili
while True:
    hisa, akiba, mkopo = angalia_saldo()

    if mkopo > 0 and akiba >= mkopo:
        print("🤖 AI: Ninalipa mkopo wako kiotomatiki...")
        lipa_mkopo()

    # Inakagua kila dakika 5
    time.sleep(300)
