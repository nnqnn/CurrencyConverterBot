import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config

API_KEY = config.ER_API_KEY
BASE_URL = "https://v6.exchangerate-api.com/v6/{}/latest/{}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

def get_exchange_rates(base_currency: str):
    url = BASE_URL.format(API_KEY, base_currency.upper())
    response = requests.get(url)
    data = response.json()
    if data["result"] == "success":
        return data["conversion_rates"]
    return None

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот-конвертер валют.\n\nИспользуй /rate USD, чтобы узнать курсы валют.\n\nИспользуй /convert 1 USD RUB, чтобы конвертировать сумму одной валюты в другую!")

@dp.message_handler(commands=['rate'])
async def get_rate(message: types.Message):
    try:
        args = message.text.split()
        if len(args) != 2:
            await message.reply("Использование: \n\n/rate <КОД_ВАЛЮТЫ>, например: /rate USD")
            return
        base_currency = args[1].upper()
        rates = get_exchange_rates(base_currency)
        if rates:
            rates_text = "\n".join([f"{key}: {value}" for key, value in list(rates.items())])
            await message.reply(f"Курсы валют для {base_currency}:\n{rates_text}")
        else:
            await message.reply("Ошибка получения курсов валют.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("Произошла ошибка. Попробуйте позже.")

@dp.message_handler(commands=['convert'])
async def convert_currency(message: types.Message):
    try:
        args = message.text.split()
        if len(args) != 4:
            await message.reply("Использование: /convert <СУММА> <ИЗ_ВАЛЮТЫ> <В_ВАЛЮТУ>, например: /convert 100 USD EUR")
            return
        amount, from_currency, to_currency = float(args[1]), args[2].upper(), args[3].upper()
        rates = get_exchange_rates(from_currency)
        if rates and to_currency in rates:
            converted_amount = amount * rates[to_currency]
            await message.reply(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency}")
        else:
            await message.reply("Ошибка получения курсов валют.")
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.reply("Произошла ошибка. Проверьте введённые данные.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
