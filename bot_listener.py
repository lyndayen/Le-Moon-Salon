import pandas as pd
import qrcode
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"
# Replace YOUR_SHEET_ID with your real ID from the browser URL
SHEET_CSV = "https://docs.google.com/spreadsheets/d/1KQmhNfO3KegYlQthHvGRUKJIFAavgF8uJgXZSS1Z0d4/gviz/tq?tqx=out:csv&sheet=customers"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[KeyboardButton("🔗 ភ្ជាប់គណនី (Link Account)", request_contact=True)],
          [KeyboardButton("QR របស់ខ្ញុំ (My QR Code)")]]
    await update.message.reply_text("សួស្តី! សូមជ្រើសរើស៖", reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def send_my_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    try:
        df = pd.read_csv(SHEET_CSV)
        user = df[df['telegram_id'].astype(str) == chat_id]
        if not user.empty:
            img = qrcode.make(str(user.iloc[0]['id']))
            bio = BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            await update.message.reply_photo(photo=bio, caption="បាកូដរបស់អ្នក ✨")
        else:
            await update.message.reply_text("សូមទាក់ទងហាងដើម្បីចុះឈ្មោះលេខទូរស័ព្ទសិន!")
    except:
        await update.message.reply_text("កំពុងមានបញ្ហាភ្ជាប់ទៅទិន្នន័យ...")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, start))
    app.add_handler(MessageHandler(filters.Text("QR របស់ខ្ញុំ (My QR Code)"), send_my_qr))
    print("Bot is starting...")
    app.run_polling()
