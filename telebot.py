import os
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# Environment variables
TOKEN = os.environ["TOKEN"]       # Railway’de ekle
API_KEY = os.environ["API_KEY"]   # Railway’de ekle

# /start komutu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌤️ Hava Durumu", callback_data="weather")],
        [InlineKeyboardButton("❌ Çıkış", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Merhaba, Hoşgeldiniz!", reply_markup=reply_markup)

# Butonlar için callback
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "weather":
        await query.edit_message_text("Lütfen hava durumunu öğrenmek istediğiniz şehri yazın:")
        context.user_data["expecting_city"] = True

    elif query.data == "exit":
        await query.edit_message_text("Görüşürüz! 👋")

# Kullanıcı mesajlarını yakala
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("expecting_city"):
        city = update.message.text
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=tr"
        response = requests.get(url).json()

        if response.get("cod") != 200:
            await update.message.reply_text("Şehir bulunamadı ❌")
        else:
            temp = response["main"]["temp"]
            desc = response["weather"][0]["description"]
            humidity = response["main"]["humidity"]
            message = f"🌤️ {city} için hava durumu:\nSıcaklık: {temp}°C\nDurum: {desc}\nNem: {humidity}%"
            await update.message.reply_text(message)

        context.user_data["expecting_city"] = False

# Botu oluştur
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Botu başlat
if __name__ == "__main__":
    print("Bot başlatılıyor...")
    app.run_polling()
