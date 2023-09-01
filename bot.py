from aiogram import Bot, Dispatcher, types, executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TOKEN
from review_parser import get_data_for_bot

scheduler = AsyncIOScheduler()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


async def on_startup(_):
    print('Бот включен')


async def start_scheduled(chat_id):
    """
        Функция для планировщика.
    :param chat_id: id чата куда бот будет кидать сообщения
    """
    await bot.send_message(chat_id=chat_id, text="Собираем негативные отзывы...")
    messages = get_data_for_bot()
    for message in messages:
        await bot.send_message(chat_id=chat_id, text=message)


@dp.message_handler(commands=['start'])
async def start_command(msg: types.Message):
    """
        Функция для запуска планировщика, когда в группе нажать команду start бот будет каждый день в 23:55 скидывать
        все негативные комментарии в группу
    """
    chat_id = msg.chat.id
    scheduler.add_job(start_scheduled, 'cron', day_of_week='mon-sun', hour=23, minute=55, args=(chat_id,))
    scheduler.start()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
