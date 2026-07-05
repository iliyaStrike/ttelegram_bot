import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, CHANNEL_1, CHANNEL_2, FILE_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ======================
# KEYBOARD
# ======================
join_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 عضویت در کانال‌ها", url=f"https://t.me/{CHANNEL_1.replace('@','')}")],
        [InlineKeyboardButton(text="✅ بررسی عضویت", callback_data="check")]
    ]
)


# ======================
# CHECK JOIN FUNCTION
# ======================
async def check_user(user_id: int):
    channels = [CHANNEL_1, CHANNEL_2]

    for channel in channels:
        print("CHECKING:", channel)

        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)

        print("STATUS:", channel, member.status)

        if member.status not in ["member", "administrator", "creator"]:
            return False

    return True


# ======================
# START COMMAND
# ======================
@dp.message(CommandStart())
async def start(message: Message):

    if await check_user(message.from_user.id):
        await message.answer("✅ شما عضو هستید")
        await message.answer_document(FILE_ID, caption="📁 فایل شما آماده است")
    else:
        await message.answer("❌ ابتدا عضو کانال‌ها شوید", reply_markup=join_kb)


# ======================
# CHECK BUTTON
# ======================
@dp.callback_query(F.data == "check")
async def check(callback: CallbackQuery):

    if await check_user(callback.from_user.id):
        await callback.message.edit_text("✅ عضویت تایید شد")
        await callback.message.answer_document(FILE_ID, caption="📁 فایل شما آماده است")
    else:
        await callback.answer("❌ هنوز عضو کانال نیستید", show_alert=True)


# ======================
# RUN
# ======================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())