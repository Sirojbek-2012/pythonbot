from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

Maxsulot = [
    {"id": 1, "nomi": "Olma", "narx": 10000},
    {"id": 2, "nomi": "Banan", "narx": 15000},
    {"id": 3, "nomi": "Nok", "narx": 20000}
]

carts = {}

ADMIN_ID = 12345678

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Mahsulotlar", "Savatcha"], ["Biz haqimizda"]]
    await update.message.reply_text("Asosiy menyu:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == "Mahsulotlar":
        msg = "Mahsulotlar ro'yxati:\n"
        for p in Maxsulot:
            msg += f"{p['id']}. {p['nomi']} - {p['narx']} so'm\n"
        msg += "\nMahsulot qo'shish uchun ID raqamini yuboring."
        await update.message.reply_text(msg)

    elif text == "Savatcha":
        cart = carts.get(user_id, [])
        if not cart:
            await update.message.reply_text("Savatchangiz bo'sh.")
        else:
            msg = "Savatchangiz:\n"
            total = 0
            for item in cart:
                msg += f"- {item['nomi']} - {item['narx']} so'm\n"
                total += item['narx']
            msg += f"\nJami: {total} so'm\n\nTasdiqlash uchun telefon raqamingizni yuboring."
            contact_button = [[KeyboardButton("Raqam yuborish", request_contact=True)]]
            await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup(contact_button, resize_keyboard=True))

    elif text == "Biz haqimizda":
        await update.message.reply_text("Bu oddiy e-commerce bot. Mahsulot tanlang va buyurtma bering!")

    elif text.isdigit():
        product_id = int(text)
        product = next((p for p in Maxsulot if p['id'] == product_id), None)
        if product:
            carts.setdefault(user_id, []).append(product)
            await update.message.reply_text(f"{product['nomi']} savatchaga qo'shildi.")
        else:
            await update.message.reply_text("Bunday mahsulot topilmadi.")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    phone = update.message.contact.phone_number
    user_id = user.id
    cart = carts.get(user_id, [])
    if not cart:
        await update.message.reply_text("Savatchangiz bo'sh.")
        return
    total = sum(item['narx'] for item in cart)
    order_text = f"Yangi buyurtma:\nUser: {user.full_name}\nPhone: {phone}\nJami: {total} so'm"
    for item in cart:
        order_text += f"\n- {item['nomi']} - {item['narx']} so'm"
    await context.bot.send_message(ADMIN_ID, order_text)
    carts[user_id] = []
    await update.message.reply_text("Buyurtma qabul qilindi. Rahmat ")

app = ApplicationBuilder().token("token").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.CONTACT, handle_contact))

print("Bot ishga tushdi")
app.run_polling()
