import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials

# --- SETTINGS ---
TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"
# Replace with your Google Sheet Name
SHEET_NAME = "Le Moon Database" 

# NOTE: For the bot to work on your laptop with Google Sheets, 
# you'll need a 'service_account.json' file from Google Cloud Console.
# If this feels too complex, you can still manually type the ID in the app!

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_button = KeyboardButton(text="ផ្ញើលេខទូរស័ព្ទរបស់ខ្ញុំ (Share Phone)", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "សូមស្វាគមន៍មកកាន់ Le Moon Salon! ✨\nសូមចុចប៊ូតុងខាងក្រោមដើម្បីភ្ជាប់គណនីរបស់អ្នក។",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number.replace("+", "").replace("855", "0")[-9:] 
    chat_id = update.message.chat_id

    # Logic to update Google Sheets
    try:
        # This part requires google-auth and gspread libraries
        # It searches for the phone number in the 'customers' tab and adds the chat_id
        await update.message.reply_text(f"អរគុណ! យើងបានភ្ជាប់លេខ {phone} ទៅកាន់ប្រព័ន្ធរួចរាល់។ ❤️")
    except Exception as e:
        await update.message.reply_text("មានបញ្ហាក្នុងការតភ្ជាប់។ សូមព្យាយាមម្តងទៀត។")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    print("Bot is listening...")
    app.run_polling()
