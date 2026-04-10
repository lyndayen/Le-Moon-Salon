from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import pandas as pd
import requests
from io import BytesIO

TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"
# Your Google Sheet CSV Export Link (Simplest way to read for the bot)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/gviz/tq?tqx=out:csv&sheet=customers"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Main Menu Buttons
    keyboard = [
        [KeyboardButton("ផ្ញើលេខទូរស័ព្ទ (Link Account)", request_contact=True)],
        [KeyboardButton("មើលបាកូដរបស់ខ្ញុំ (View QR Code)")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "សូមស្វាគមន៍មកកាន់ Le Moon Salon! ✨\nសូមជ្រើសរើសម៉ឺនុយខាងក្រោម៖",
        reply_markup=reply_markup
    )

async def send_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    
    # 1. Read Google Sheet to find the Customer ID
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        # Find row where telegram_id matches this user
        user_row = df[df['telegram_id'].astype(str) == chat_id]
        
        if not user_row.empty:
            customer_id = user_row.iloc[0]['id']
            # 2. Send the QR code image
            # Note: The image must be accessible or stored locally where the bot runs
            qr_path = f"qrcodes/{customer_id}.png"
            
            with open(qr_path, 'rb') as photo:
                await update.message.reply_photo(photo=photo, caption="នេះគឺជា QR Code សម្រាប់ប្រើប្រាស់នៅហាង។ ✨")
        else:
            await update.message.reply_text("សូមចុច 'Link Account' ជាមុនសិន ឬទាក់ទងមកហាងដើម្បីចុះឈ្មោះ។")
    except Exception as e:
        await update.message.reply_text("មានបញ្ហាបច្ចេកទេស។ សូមព្យាយាមម្តងទៀតក្រោយ!")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, start)) # Reuse start logic for link
    app.add_handler(MessageHandler(filters.Text("មើលបាកូដរបស់ខ្ញុំ (View QR Code)"), send_qr))
    
    print("Bot is listening for QR requests...")
    app.run_polling()
