from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

TOKEN = "8631946181:AAG4XQshcQHY3HqgGTvjiXb_RmZtr34jTwE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Khmer UI for the Bot
    contact_button = KeyboardButton(text="ផ្ញើលេខទូរស័ព្ទរបស់ខ្ញុំ (Share Phone Number)", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "សូមស្វាគមន៍មកកាន់ Le Moon Salon! ✨\n\nសូមចុចប៊ូតុងខាងក្រោមដើម្បីភ្ជាប់គណនីរបស់អ្នក សម្រាប់ការទទួលវិក្កយបត្រឌីជីថល។",
        reply_markup=reply_markup
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    phone = contact.phone_number.replace("+", "").replace("855", "0")[-9:] 
    chat_id = update.message.chat_id

    conn = sqlite3.connect('salon.db')
    cur = conn.cursor()
    cur.execute("SELECT name FROM customers WHERE phone LIKE ?", (f'%{phone}%',))
    user = cur.fetchone()

    if user:
        cur.execute("UPDATE customers SET telegram_id = ? WHERE phone LIKE ?", (str(chat_id), f'%{phone}%'))
        conn.commit()
        await update.message.reply_text(f"អរគុណបង {user[0]}! គណនីត្រូវបានភ្ជាប់ជោគជ័យ។ អ្នកនឹងទទួលបានវិក្កយបត្រនៅទីនេះរាល់ពេលប្រើប្រាស់សេវាកម្ម។ ❤️")
    else:
        await update.message.reply_text("រកមិនឃើញលេខទូរស័ព្ទក្នុងប្រព័ន្ធទេ។ សូមចុះឈ្មោះនៅហាងជាមុនសិន! 🙏")
    conn.close()

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    print("Bot Listener is Running... (Bot កំពុងដំណើរការ)")
    app.run_polling()