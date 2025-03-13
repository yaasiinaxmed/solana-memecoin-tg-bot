from solana.rpc.api import Client
from solders.keypair import Keypair  # ✅ Correct import for Solana accounts
import os
import random
from solders.pubkey import Pubkey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RPC_URL = os.getenv("QUICKNODE_RPC")

# Check if RPC_URL is set
if not RPC_URL:
    raise ValueError("QUICKNODE_RPC is not set in .env file")

client = Client(RPC_URL)

def create_wallet():
    """Creates a new Solana wallet"""
    wallet = Keypair()
    return str(wallet.pubkey()), wallet.secret().hex()  # ✅ Fixed key format

def import_wallet(private_key: str):
    """Imports an existing Solana wallet"""
    try:
        wallet = Keypair.from_bytes(bytes.fromhex(private_key))
        return str(wallet.pubkey())
    except ValueError:
        return "Invalid private key"

def get_balance(wallet_address: str):
    """Fetches the SOL balance of a wallet"""
    try:
        pubkey = Pubkey.from_string(wallet_address)  # Convert to correct format
        balance = client.get_balance(pubkey)["result"]["value"]
        return balance / 1e9  # Convert lamports to SOL
    except Exception as e:
        return f"Error fetching balance: {str(e)}"
    
def create_token(name: str, symbol: str, description: str, private_key: str):
    """Creates an SPL token on Solana (Mock Function)"""
    try:
        token_address = f"SPL_{random.randint(1000, 9999)}"
        tx_hash = f"TX_{random.randint(1000, 9999)}"
        return tx_hash, token_address
    except Exception as e:
        return f"Error creating token: {str(e)}"
