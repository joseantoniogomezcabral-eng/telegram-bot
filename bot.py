import asyncio
import sqlite3
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8262473875

CHANNEL_USERNAME = "@cazaeuros"
OWNER_USERNAME = "cazaeuross"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ------------------ NOTIFY ADMIN ------------------

async def notify_admin(text):
    try:
        await bot.send_message(ADMIN_ID, text)
    except:
        pass

# ------------------ CHECK SUB ------------------

async def check_subscription(user_id):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:
        return False

# ------------------ DB ------------------

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    step INTEGER,
    selected TEXT
)
""")
conn.commit()

def save_user(user_id, step, selected):
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, step, selected) VALUES (?, ?, ?)",
        (user_id, step, ",".join(selected))
    )
    conn.commit()

def load_user(user_id):
    cursor.execute("SELECT step, selected FROM users WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row:
        step, selected = row
        return {
            "step": step,
            "selected": selected.split(",") if selected else []
        }

    return {"step": 0, "selected": []}

# ------------------ APPS ------------------

apps = {

    "n26": (
        "N26",
        15,
        """📲 N26

Banco sin comisiones.

📝 Pasos:

1️⃣ Regístrate:
https://n26.com/r/joseantg09824c?cid=CTK&lang=es

2️⃣ Haz una transacción de 20€

3️⃣ Recibe 15€ en metálico 🎁"""
    ),

    "bbva": (
        "BBVA",
        50,
        """🎁 BBVA — Hasta 450€

📝 Pasos:

1️⃣ Regístrate con código:
14D40040F15CBF

👉 https://www.bbva.es

2️⃣ Activa tarjeta Aqua Débito

3️⃣ Haz un pago de 50€

4️⃣ Recibes 50€

5️⃣ +400€ si domicilias nómina"""
    ),

    "imagin": (
        "Imagin",
        50,
        """😄 Imagin — 50€

📝 Pasos:

1️⃣ Regístrate con código:
A01IM88288299

👉 https://imagin.pwlnk.io/uj$&JA4Qc

2️⃣ Ingresa 50€

3️⃣ Haz 3 pagos con tarjeta

4️⃣ Activa Bizum"""
    ),

    "openbank": (
        "Openbank",
        70,
        """🏦 Openbank — 70€

📝 Pasos:

1️⃣ Regístrate:
https://www.openbank.es/hazte-cliente

2️⃣ Usa códigos promocionales

3️⃣ Gasta 50€ con tarjeta

4️⃣ Activa Bizum"""
    ),

    "coinbase": (
        "Coinbase",
        20,
        """🪙 Coinbase — 20€

📝 Pasos:

1️⃣ Regístrate:
https://coinbase.com/join/533ESYT?src=android-share

2️⃣ Compra 21€ en cripto

3️⃣ Recibes 20€ en BTC 🎁"""
    ),

    "myinvestor": (
        "MyInvestor",
        25,
        """🚀 MyInvestor — 25€

📝 Pasos:

1️⃣ Regístrate:
https://newapp.myinvestor.es/do/signup?promotionalCode=SUAPK

2️⃣ Código: SUAPK

3️⃣ Cumple requisitos

4️⃣ Recibes 25€"""
    ),

    "kriptomat": (
        "Kriptomat",
        25,
        """💎 Kriptomat — 25€ BTC

📝 Pasos:

1️⃣ Regístrate:
https://app.kriptomat.io/ref/join?referral=bunt8ba4

2️⃣ Deposita ~105€

3️⃣ Compra 100€ en cripto

4️⃣ Mantén 30 días

5️⃣ Recibes 25€"""
    ),

    "kraken": (
        "Kraken",
        200,
        """💰 Kraken — hasta 200€

📝 Pasos:

1️⃣ Regístrate:
https://invite.kraken.com/JDNW/06n4hbek

2️⃣ Verifica cuenta

3️⃣ Deposita y compra BTC

4️⃣ Recibes recompensa"""
    ),

    "taptap": (
        "TapTap",
        15,
        """💸 TapTap — 15€

📝 Pasos:

1️⃣ Descarga:
https://taptapsend.onelink.me/Lrab/appreferral

2️⃣ Envía EUR → AUD

3️⃣ Código:
JOSEANTO113"""
    ),

    "aircash": (
        "Aircash",
        5,
        """💳 Aircash — 5€

📝 Pasos:

1️⃣ Regístrate:
https://link.aircash.eu/Referral/Index?referralCode=joseantoniog58

2️⃣ Ingresa 10€

3️⃣ Recibes dinero"""
    ),

    "bybit": (
        "Bybit",
        55,
        """📊 Bybit — 55€

📝 Pasos:

1️⃣ Regístrate:
https://www.bybit.eu/invite?ref=QB63O3A

2️⃣ Deposita 100€

3️⃣ Recibes recompensa"""
    )

}

user_data = {}

# ------------------ UTIL ------------------

def progress_bar(done, total):
    if total == 0:
        return "░░░░░░░░░░"

    percent = int((done / total) * 10)

    return "█" * percent + "░" * (10 - percent)

def get_keyboard(user_id):

    selected = user_data[user_id]["selected"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for key, (name, reward, _) in apps.items():

        mark = "☑️" if key in selected else "⬜"

        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"{mark} {name} - {reward}€",
                callback_data=f"select_{key}"
            )
        ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="✅ Confirmar",
            callback_data="confirm"
        )
    ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="🌐 Página web",
            url="https://www.cazaeuros.com"
        )
    ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="💬 Hablar conmigo",
            url=f"https://t.me/{OWNER_USERNAME}"
        )
    ])

    return keyboard

# ------------------ START ------------------

@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):

    user_id = message.from_user.id

    subscribed = await check_subscription(user_id)

    if not subscribed:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="📢 Unirme al canal",
                        url="https://t.me/cazaeuros"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="✅ Ya me uní",
                        callback_data="check_sub"
                    )
                ]
            ]
        )

        await message.answer(
            "⚠️ Para usar el bot debes unirte al canal oficial.\n\n"
            "👇 Entra y luego pulsa el botón:",
            reply_markup=keyboard
        )

        return

    user_data[user_id] = load_user(user_id)

    await notify_admin(
        f"🚀 Nuevo usuario\n\n"
        f"👤 @{message.from_user.username}\n"
        f"🆔 {message.from_user.id}"
    )

    await message.answer(
        "📲 Selecciona SOLO las apps en las que NO estás registrado.\n\n"
        "☑️ Marca las que NO tengas\n"
        "⬜ Deja sin marcar las que ya tienes\n\n"
        "👇 Empieza aquí:",
        reply_markup=get_keyboard(user_id)
    )

# ------------------ MENSAJES ------------------

@dp.message()
async def capture_messages(message: types.Message):

    if message.text == "/start":
        return

    user = message.from_user

    await notify_admin(
        f"📩 Mensaje\n\n"
        f"👤 @{user.username} ({user.id})\n"
        f"💬 {message.text}"
    )

# ------------------ PASOS ------------------

async def send_next_step(message, user_id):

    data = user_data[user_id]

    selected = data["selected"]

    step = data["step"]

    if step >= len(selected):

        await message.answer("🎉 Has terminado todas las promos")

        return

    app_key = selected[step]

    name, reward, instructions = apps[app_key]

    total = len(selected)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ HECHO",
                    callback_data="done"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⏭ OMITIR",
                    callback_data="skip"
                )
            ]
        ]
    )

    await message.answer(
        f"📱 {name} — {reward}€\n\n"
        f"{instructions}\n\n"
        f"📊 [{progress_bar(step, total)}] {step}/{total}",
        reply_markup=keyboard
    )

# ------------------ CALLBACKS ------------------

@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):

    user_id = callback.from_user.id

    if user_id not in user_data:
        user_data[user_id] = load_user(user_id)

    # -------- CHECK SUB --------

    if callback.data == "check_sub":

        subscribed = await check_subscription(user_id)

        if not subscribed:

            await callback.answer(
                "❌ Aún no estás unido al canal",
                show_alert=True
            )

            return

        await callback.message.answer(
            "✅ Verificación completada.\n\n"
            "📲 Ya puedes usar el bot.",
            reply_markup=get_keyboard(user_id)
        )

        await callback.answer()

    # -------- SELECT --------

    elif callback.data.startswith("select_"):

        key = callback.data.split("_")[1]

        if key in user_data[user_id]["selected"]:
            user_data[user_id]["selected"].remove(key)

        else:
            user_data[user_id]["selected"].append(key)

        save_user(
            user_id,
            user_data[user_id].get("step", 0),
            user_data[user_id]["selected"]
        )

        await callback.message.edit_reply_markup(
            reply_markup=get_keyboard(user_id)
        )

        await callback.answer()

    # -------- CONFIRM --------

    elif callback.data == "confirm":

        selected = user_data[user_id]["selected"]

        if not selected:

            await callback.answer(
                "Selecciona al menos una promo",
                show_alert=True
            )

            return

        user_data[user_id]["step"] = 0

        save_user(user_id, 0, selected)

        total_money = sum(apps[a][1] for a in selected)

        await notify_admin(
            f"💰 Usuario empezó\n\n"
            f"🆔 {user_id}\n"
            f"📊 {', '.join(selected)}\n"
            f"💸 {total_money}€"
        )

        await callback.message.answer(
            f"💰 Total estimado: {total_money}€\n"
            f"[{progress_bar(0, len(selected))}]"
        )

        await callback.answer()

        await send_next_step(callback.message, user_id)

    # -------- DONE --------

    elif callback.data == "done":

        user_data[user_id]["step"] += 1

        save_user(
            user_id,
            user_data[user_id]["step"],
            user_data[user_id]["selected"]
        )

        await callback.answer()

        await send_next_step(callback.message, user_id)

    # -------- SKIP --------

    elif callback.data == "skip":

        user_data[user_id]["step"] += 1

        await callback.answer()

        await send_next_step(callback.message, user_id)

# ------------------ RUN ------------------

async def main():

    print("🚀 Bot iniciado correctamente")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
