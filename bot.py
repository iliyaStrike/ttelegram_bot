import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, CHANNEL_1, CHANNEL_2, FILE_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

files = {}
waiting_admin = {}

ADMIN_ID = 123456789  # آیدی خودت


# =====================
# KEYBOARD
# =====================
start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="عضویت در کانال‌ها ✅", callback_data="check_join")]
    ]
)


# =====================
# CHECK JOIN
# =====================
async def check_join(user_id):
    channels = [CHANNEL_1, CHANNEL_2]

    for channel in channels:
        member = await bot.get_chat_member(channel, user_id)
        if member.status not in ["member", "administrator", "creator"]:
            return False
    return True


# =====================
# START
# =====================
@dp.message(CommandStart())
async def start(message: Message):

    args = message.text.split()

    # لینک فایل
    if len(args) > 1:
        code = args[1]

        if code not in files:
            await message.answer("❌ فایل پیدا نشد")
            return

        if await check_join(message.from_user.id):
            await message.answer(f"📁 فایل شما:\n{files[code]}")
        else:
            await message.answer("❌ اول عضو کانال شو", reply_markup=start_keyboard)
        return

    # حالت عادی
    if await check_join(message.from_user.id):
        await message.answer("✅ عضویت تایید شد")
        await message.answer_document(FILE_ID, caption="🎉 فایل پیشفرض")
    else:
        await message.answer("❌ اول عضو کانال شو", reply_markup=start_keyboard)


# =====================
# CHECK BUTTON
# =====================
@dp.callback_query(F.data == "check_join")
async def check_callback(callback: CallbackQuery):

    if await check_join(callback.from_user.id):
        await callback.message.edit_text("✅ عضویت تایید شد")
        await callback.message.answer_document(FILE_ID, caption="🎉 فایل شما")
    else:
        await callback.answer("❌ هنوز عضو نیستی", show_alert=True)


# =====================
# ADMIN PANEL
# =====================
@dp.message(Command("add"))
async def add(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    waiting_admin[message.from_user.id] = True
    await message.answer("📁 لینک فایل رو بفرست")


@dp.message(F.text)
async def save_file(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    if not waiting_admin.get(message.from_user.id):
        return

    link = message.text

    if not link.startswith("http"):
        await message.answer("❌ فقط لینک بفرست")
        return

    code = str(random.randint(1000, 9999))
    files[code] = link

    waiting_admin[message.from_user.id] = False

    await message.answer(
        f"✅ ذخیره شد!\n\n🔗 لینک:\nhttps://t.me/YOUR_BOT?start={code}"
    )


# =====================
# MAIN
# =====================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())