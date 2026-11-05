import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Bot tokeningizni shu yerga yozing
BOT_TOKEN = "9139601912:AAE44-iG-AKbU-OGBR0eNrmEqNpKedAk3dQ"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Xotiradagi ma'lumotlar tuzilmasi ---
waiting_queue = []  # Suhbatdosh kutayotgan foydalanuvchilar navbati (ID lar ro'yxati)
active_chats = {}   # Hozirda suhbatda bo'lganlar: {user_id: partner_id}

# --- Asosiy tugmalar ---
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Suhbatdosh qidirish")],
        [KeyboardButton(text="ℹ️ Bot haqida")]
    ],
    resize_keyboard=True
)

chat_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❌ Suhbatni to'xtatish")]
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    if user_id in active_chats:
        await message.answer("Siz hozirda suhbatdasiz. Uni tugatish uchun tugmani bosing.", reply_markup=chat_menu)
        return
    
    await message.answer(
        "👋 Assalomu alaykum! Anonim chat botiga xush kelibsiz.\n\n"
        "Suhbatdosh topish tugmasini bosing va bot sizga tasodifiy sherik topib beradi.",
        reply_markup=main_menu
    )


@dp.message(F.text == "🔍 Suhbatdosh qidirish")
async def search_partner(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_chats:
        await message.answer("Siz allaqachon suhbatdasiz!", reply_markup=chat_menu)
        return
    
    if user_id in waiting_queue:
        await message.answer("Siz allaqachon qidiruvdasiz. Suhbatdosh topilishi kutilmoqda...", reply_markup=chat_menu)
        return

    # Agar navbatda kimdir bo'lsa, uni suhbatga ulaymiz
    if waiting_queue:
        partner_id = waiting_queue.pop(0)  # Navbat boshidagi odamni olamiz
        
        # O'zaro bog'laymiz
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        # Har ikkala foydalanuvchiga xabar beramiz
        await bot.send_message(user_id, "🎉 Suhbatdosh topildi! Gaplashavering.", reply_markup=chat_menu)
        await bot.send_message(partner_id, "🎉 Suhbatdosh topildi! Gaplashavering.", reply_markup=chat_menu)
    else:
        # Hech kim bo'lmasa, navbatga qo'shamiz
        waiting_queue.append(user_id)
        await message.answer("⏳ Suhbatdosh qidirilmoqda... Iltimos kuting.", reply_markup=chat_menu)


@dp.message(F.text == "❌ Suhbatni to'xtatish")
async def stop_chat(message: types.Message):
    user_id = message.from_user.id

    # Agar foydalanuvchi qidiruvda bo'lsa, navbatdan chiqarib tashlaymiz
    if user_id in waiting_queue:
        waiting_queue.remove(user_id)
        await message.answer("❌ Qidiruv to'xtatildi.", reply_markup=main_menu)
        return

    # Agar suhbatda bo'lsa, suhbatni ikkala tomon uchun ham yopamiz
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        
        # Lug'atdan tozalaymiz
        del active_chats[user_id]
        del active_chats[partner_id]

        # Xabar yuboramiz
        await message.answer("❌ Suhbat yakunlandi.", reply_markup=main_menu)
        await bot.send_message(partner_id, "⚠️ Suhbatdosh suhbatni tark etdi.", reply_markup=main_menu)
    else:
        await message.answer("Siz hozirda hech qanday suhbatda emassiz.", reply_markup=main_menu)


@dp.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: types.Message):
    await message.answer("🤖 Bu bot Aiogram 3 yordamida yasalgan anonim suhbat tizimi.")


# --- Xabarlarni bir-biriga yetkazish (Matn, rasm, video, voice va hokazo) ---
@dp.message()
async def pass_message(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        try:
            # message.copy_to() orqali istalgan turdagi xabar (rasm, voice, video, matn) sherigiga xavfsiz ko'chiriladi
            await message.copy_to(chat_id=partner_id)
        except Exception as e:
            logging.error(f"Xabar yuborishda xatolik: {e}")
    else:
        await message.answer("Iltimos, avval suhbatdosh topish tugmasini bosing!", reply_markup=main_menu)


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Bot ishga tushdi va ishlamoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())