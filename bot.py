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
    "n26": ("N26", 15, """📲 N26
Buenas 👋
N26 es un banco sin comisiones de mantenimiento ni de tarjeta.
📝 Pasos para llevarte 15€:
1️⃣ Regístrate aquí:
https://n26.com/r/joseantg09824c?cid=CTK&lang=es
2️⃣ Haz una transacción de 20€
3️⃣ Recibe 15€ en metálico 🎁
Así de sencillo."""),

    "bbva": ("BBVA", 50, """🎁 BBVA
¡Hasta 450€ de regalo!
📝 Pasos a seguir:
1️⃣ Date de alta en BBVA con mi código amigo: 14D40040F15CBF
👉 Abre la cuenta online aquí:
https://www.bbva.es/general/hazte-cl...omisiones.html
2️⃣ Activa tu tarjeta de débito Aqua Débito
3️⃣ Haz un pago igual o superior a 50€
4️⃣ Recibirás 50€ de parte de BBVA
5️⃣ Si llevas tu nómina de 800€ o más, BBVA te da otros 400€"""),

    "imagin": ("Imagin", 50, """😄 Imagin
Si te das de alta en Imagin con el código A01IM88288299, te puedes llevar 50€ para comprar en Facilitea Shop 🛍️
Yo también recibo un incentivo, así que ganamos los dos.
👇 Enlace:
https://imagin.pwlnk.io/uj$&JA4Qc
📝 Pasos:
1️⃣ Abrir cuenta en Imagin con el código A01IM88288299
2️⃣ Realizar un ingreso mínimo de 50€
3️⃣ Hacer un mínimo de 3 movimientos con tarjeta
4️⃣ Activar Bizum"""),

    "openbank": ("Openbank", 70, """🏦 Openbank
Openbank es un banco sin comisiones de mantenimiento ni de tarjeta.
📝 Pasos a seguir:
1️⃣ Abre tu cuenta aquí:
https://www.openbank.es/hazte-cliente
2️⃣ Introduce alguno de estos códigos promocionales:
56173811620102120171
56173831512101914216
56173841010318186122
56173771731820171801
56173748131181719196
56173721514151613206
3️⃣ Haz gastos con tarjeta que sumen 50€ o más
4️⃣ Activa Bizum"""),

    "coinbase": ("Coinbase", 20, """🪙 Coinbase
20€ reales con Coinbase 
Coinbase es el exchange de crypto más conocido y regulado.
🎁 La oferta:
20€ de Coinbase (promo oficial)
📋 Cómo funciona:
1️⃣ Te registras con mi enlace:
https://coinbase.com/join/533ESYT?src=android-share
2️⃣ Compras 21€ de cualquier cripto
(Recomiendo USDT para evitar volatilidad y 21€ en vez de 20€ por comisiones y seguridad)
3️⃣ Coinbase nos da 20€ en BTC a ambos"""),

    "myinvestor": ("MyInvestor", 25, """🚀 MyInvestor
MyInvestor ofrece una promo de bienvenida de 25€ si te registras con mi enlace y utilizas mi código promocional.
📝 Pasos:
1️⃣ Regístrate aquí:
https://newapp.myinvestor.es/do/signup?promotionalCode=SUAPK
2️⃣ En el paso 6/7 introduce el código:
SUAPK
3️⃣ Cumple una de estas dos opciones:
Tener 1.000€ en efectivo en tu cuenta corriente
O invertir al menos 100€ en productos de inversión
4️⃣ En 24/48 horas recibes la bonificación de 25€"""),

    "kriptomat": ("Kriptomat", 25, """💎 Kriptomat
Kriptomat está regalando 25€ en BTC a los usuarios nuevos que se registren con mi enlace de invitación.
🔹 ¿Cómo funciona?
1️⃣ Regístrate aquí:
https://app.kriptomat.io/ref/join?referral=bunt8ba4
2️⃣ Ingresa unos 105€ mediante transferencia SEPA
(la comisión es de 1€)
❌ No uses tarjeta, la comisión es alta.
3️⃣ Compra al menos 100€ en cualquier cripto
(BTC, ETH...)
4️⃣ Mantén esta inversión durante 30 días
5️⃣ Recibirás automáticamente 25€ en Bitcoin 🚀
⚡ Consejo: invierte en una cripto sólida y espera los 30 días."""),

    "kraken": ("Kraken", 200, """💰 Kraken
🪙 Pasos a seguir:
1️⃣ Abrir cuenta en Kraken con mi código o enlace de invitación:
Referral code: sdbsc3hp
Referral link: https://invite.kraken.com/JDNW/06n4hbek
2️⃣ Verifica la cuenta
3️⃣ Deposita 202€
4️⃣ Compra 200€ en BTC
5️⃣ En máximo 14 días, recibes hasta 200€ de regalo en tu cuenta"""),

    "taptap": ("TapTap", 15, """💸 TapTap Send
Consigue dinero con TapTap Send.
📝 Pasos:
Necesitas banco español + Wise con cuenta en AUD (Australia)
❌ Revolut AUD no sirve
1️⃣ Descarga la app:
👉 https://taptapsend.onelink.me/Lrab/appreferral
2️⃣ Abre la cuenta y selecciona envío de EUR → AUD (Australia)
3️⃣ Introduce el código promocional:
👉 JOSEANTO113
✔️ Comprueba que te suman 15€ al enviar 50€ o más de EUR a AUD
📍 Si te piden una dirección australiana:
https://generate.plus/es/direccion/australia-au
4️⃣ Método de pago:
Elige el que quieras. Yo usé Apple Pay con Revolut."""),

    "aircash": ("Aircash", 5, """💳 Aircash
Es una promo muy fácil:
1️⃣ Descárgate la app de Aircash desde mi enlace y regístrate:
https://link.aircash.eu/Referral/Index?referralCode=joseantoniog58
2️⃣ Ingresa un mínimo de 10€ en tu cuenta
3️⃣ Yo recibiré 10€ por la promoción, de los que te daré 5€
4️⃣ Solo válido para Android"""),

    "bybit": ("Bybit", 55, """🔥 Bybit EU
Os dejo la promo de Bybit EU, un exchange de criptomonedas donde puedes comprar, vender y hacer trading con cientos de activos digitales.
📝 Pasos para ganar 55€:
Abre este enlace y verifica que te sale el código aplicado:
https://www.bybit.eu/invite?ref=QB63O3A
Si no te sale así, cierra el navegador y vuelve a abrir el enlace.
1️⃣ Verifica identidad y deposita 100€
Tienes 7 días desde el registro para depositar los 100€, si no, perderás la recompensa.
Solo por depositar, te acreditan 45€ en BTC en los próximos 3 días.
2️⃣ Si quieres ganar 10€ adicionales, abre Bybit EU desde el navegador y solicita la tarjeta gratuita (Bybit Card) aplicando este código:
QB63O3A
Importante meter el código al solicitar la tarjeta.
Después, debes gastar 100€ en una o varias compras.""")

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
            InlineKeyboardButton(text=f"{mark} {name} - {reward}€", callback_data=f"select_{key}")
        ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="✅ Confirmar", callback_data="confirm")
    ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🌐 Página web", url="https://www.cazaeuros.com")
    ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="💬 Hablar conmigo", url=f"https://t.me/{OWNER_USERNAME}")
    ])

    return keyboard

# ------------------ START ------------------

@dp.message(lambda message: message.text == "/start")
async def start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = load_user(user_id)

    await notify_admin(
        f"🚀 Nuevo usuario\n\n"
        f"👤 {message.from_user.username}\n"
        f"🆔 {message.from_user.id}"
    )

    await message.answer(
        "📲 Selecciona SOLO las apps en las que NO estás registrado.\n\n"
        "☑️ Marca las que NO tengas\n"
        "⬜ Deja sin marcar las que ya tienes\n\n"
        "👇 Empieza aquí:",
        reply_markup=get_keyboard(user_id)
    )

# ------------------ CAPTURAR MENSAJES ------------------

@dp.message()
async def capture_messages(message: types.Message):
    user = message.from_user

    await notify_admin(
        f"📩 Mensaje\n\n"
        f"👤 {user.username} ({user.id})\n"
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

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ HECHO", callback_data="done")],
        [InlineKeyboardButton(text="⏭ OMITIR", callback_data="skip")]
    ])

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

    if callback.data.startswith("select_"):
        key = callback.data.split("_")[1]

        if key in user_data[user_id]["selected"]:
            user_data[user_id]["selected"].remove(key)
        else:
            user_data[user_id]["selected"].append(key)

        save_user(user_id, user_data[user_id].get("step", 0), user_data[user_id]["selected"])
        await callback.message.edit_reply_markup(reply_markup=get_keyboard(user_id))
        await callback.answer()

    elif callback.data == "confirm":
        selected = user_data[user_id]["selected"]

        if not selected:
            await callback.answer("Selecciona al menos una promo", show_alert=True)
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

    elif callback.data == "done":
        user_data[user_id]["step"] += 1
        save_user(user_id, user_data[user_id]["step"], user_data[user_id]["selected"])
        await callback.answer()
        await send_next_step(callback.message, user_id)

    elif callback.data == "skip":
        user_data[user_id]["step"] += 1
        await callback.answer()
        await send_next_step(callback.message, user_id)

# ------------------ RUN ------------------

async def main():
    print("🚀 Bot iniciado")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
