import pandas as pd
import qrcode
from io import BytesIO
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"
# Use the 'Export to CSV' link for your Google Sheet
SHEET_CSV = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/gviz/tq?tqx=out:csv&sheet=customers"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[KeyboardButton("🔗 ភ្ជាប់គណនី (Link Account)", request_contact=True)],
          [KeyboardButton("QR របស់ខ្ញុំ (My QR Code)")]]
    await update.message.reply_text("សូមស្វាគមន៍មកកាន់ Le Moon Salon ✨", 
                                   reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True))

async def send_my_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    try:
        df = pd.read_csv(SHEET_CSV)
        user = df[df['telegram_id'].astype(str) == chat_id]
        
        if not user.empty:
            c_id = str(user.iloc[0]['id'])
            img = qrcode.make(c_id)
            bio = BytesIO()
            img.save(bio, 'PNG')
            bio.seek(0)
            await update.message.reply_photo(photo=bio, caption="នេះជាបាកូដសមាជិករបស់បង ✨")
        else:
            await update.message.reply_text("រកមិនឃើញគណនី! សូមចុះឈ្មោះនៅហាងសិន។")
    except:
        await update.message.reply_text("មានបញ្ហាបច្ចេកទេស។")

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, start))
    app.add_handler(MessageHandler(filters.Text("QR របស់ខ្ញុំ (My QR Code)"), send_my_qr))
    print("Bot is alive...")
    app.run_polling()
