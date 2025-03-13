import telebot
import os
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.solana_utils import create_wallet, import_wallet, get_balance, create_token

from dotenv import load_dotenv

# Load env variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Store user data (temporary)
user_wallets = {}

# Start Command
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🆕 Create Wallet"), KeyboardButton("🔑 Import Private Key"))
    bot.send_message(message.chat.id, "🌠 Welcome to Hunter!\n🚀 The Fastest All-In-One Token Creator!", reply_markup=markup)

# Handle Wallet Creation
@bot.message_handler(func=lambda msg: msg.text == "🆕 Create Wallet")
def handle_create_wallet(message):
    wallet_address, private_key = create_wallet()
    user_wallets[message.chat.id] = {"address": wallet_address, "private_key": private_key}
    bot.send_message(message.chat.id, f"✅ Wallet Created!\n\n💳 Your Solana Wallet:\n→ {wallet_address}\n\nUse /menu to view options.")

# Handle Private Key Import
@bot.message_handler(func=lambda msg: msg.text == "🔑 Import Private Key")
def handle_import_wallet(message):
    bot.send_message(message.chat.id, "🔑 Send your Solana private key:")
    bot.register_next_step_handler(message, save_private_key)

def save_private_key(message):
    private_key = message.text
    wallet_address = import_wallet(private_key)
    user_wallets[message.chat.id] = {"address": wallet_address, "private_key": private_key}
    bot.send_message(message.chat.id, f"✅ Wallet Imported!\n\n💳 Your Solana Wallet:\n→ {wallet_address}\n\nUse /menu to view options.")

# Show Menu
@bot.message_handler(commands=['menu'])
def show_menu(message):
    user = user_wallets.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "⚠️ No wallet found. Please create or import one.")
        return
    
    balance = get_balance(user["address"])
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("💰 View Balance"), KeyboardButton("🪙 Create Token"))
    
    bot.send_message(message.chat.id, f"💳 Your Solana Wallets:\n→ Wallet - {balance} SOL\n→ {user['address']}", reply_markup=markup)

# Handle View Balance
@bot.message_handler(func=lambda msg: msg.text == "💰 View Balance")
def handle_balance(message):
    user = user_wallets.get(message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "⚠️ No wallet found. Please create or import one.")
        return
    
    balance = get_balance(user["address"])
    bot.send_message(message.chat.id, f"💰 Balance: {balance} SOL")

# Handle Token Creation
@bot.message_handler(func=lambda msg: msg.text == "🪙 Create Token")
def handle_create_token(message):
    bot.send_message(message.chat.id, "📤 Upload your token image:")
    bot.register_next_step_handler(message, get_token_name)

def get_token_name(message):
    bot.send_message(message.chat.id, "✏️ Enter Token Name:")
    bot.register_next_step_handler(message, get_token_symbol)

def get_token_symbol(message):
    name = message.text
    bot.send_message(message.chat.id, "🔤 Enter Token Symbol:")
    bot.register_next_step_handler(message, get_token_description, name)

def get_token_description(message, name):
    symbol = message.text
    bot.send_message(message.chat.id, "📝 Enter Token Description:")
    bot.register_next_step_handler(message, confirm_token_creation, name, symbol)

def confirm_token_creation(message, name, symbol):
    description = message.text
    user = user_wallets.get(message.chat.id)
    
    if not user:
        bot.send_message(message.chat.id, "⚠️ No wallet found. Please create or import one.")
        return

    bot.send_message(message.chat.id, "⚡ Creating Token... Please wait!")
    tx_hash, token_address = create_token(name, symbol, description, user["private_key"])
    
    bot.send_message(message.chat.id, f"✅ Token Created!\n\n🔗 Explorer: https://solscan.io/token/{token_address}\n🔹 TX: {tx_hash}")

bot.polling()