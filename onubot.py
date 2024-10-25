import time
import asyncio
import logging
import telnetlib
from aiogram import F
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from datetime import datetime                   #Импорт даты например для команды /info снизу
from aiogram.enums import ParseMode             #Позволяет форматировать выводимый текст HTML кодом. (команда /start в пример)

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="7849162908:AAEoFPhwhx5MvQpHyvC9qOx85jaP04lkiZ8")
# Диспетчер
dp = Dispatcher()
dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


#FUNCTIONS
def pon_head_scan(pon_line, onu_number):
    host = '192.168.208.141'

    tn = telnetlib.Telnet(host, 23)
    tn.read_until(b'>>User name:')
    tn.write(b'admin\n')
    tn.read_until(b'>>User password:')
    tn.write(b'admin\n')
    tn.read_until(b'OLT> ')
    tn.write(b'enable\n')
    tn.read_until(b'OLT# ')
    tn.write(b'config\n')
    tn.read_until(b'OLT(config)#')
    tn.write(b'interface epon 0/0\n')
    tn.read_until(b'OLT(config-interface-epon-0/0)#')

    if onu_number != 0: #Если введена линия и онушка
        byte_string = f"show ont optical-info {pon_line} {onu_number}\n"
        tn.write(bytes(byte_string, 'utf-8'))
        time.sleep(0.2)
        output = tn.read_very_eager().decode('utf-8')
        return output
    else:               #Если введена только линия
        byte_string = f"show ont optical-info {pon_line} all\n"
        tn.write(bytes(byte_string, 'utf-8'))
        time.sleep(0.6)
        tn.write(b'm')
        time.sleep(0.1)
        
        result = "------------------------------------------------------------------------------------------------------\n"
        result += "ID       MAC                        VOLTAGE      TX           RX           LAZER     TEMP°C\n"
        result += "------------------------------------------------------------------------------------------------------\n"
        
        output = tn.read_very_eager().decode('utf-8')[413:]
        for i in output.split("\n")[1:]:
            result += i[7:]+"\n"
        
        result += "------------------------------------------------------------------------------------------------------\n"

        return result


# ХЭНДЛЕРЫ
# Хэндлер на команду /start (здоровается по имени юзера)
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Hello, <b>{message.from_user.full_name}</b>\nВведи номер пон линии или номер линии 'пробел' номер онушки",
        parse_mode=ParseMode.HTML
    )

# Команда /info выводит время запуска бота
@dp.message(Command("info"))
async def cmd_info(message: types.Message, started_at: str):
    await message.answer(f"Бот запущен {started_at}")

# Команда /mem выводит состояни памяти бошки
@dp.message(Command("mem"))
async def cmd_mem(message: types.Message):
    host = '192.168.208.141'

    tn = telnetlib.Telnet(host, 23)
    tn.read_until(b'>>User name:')
    tn.write(b'admin\n')
    tn.read_until(b'>>User password:')
    tn.write(b'admin\n')
    tn.read_until(b'OLT> ')
    tn.write(b'enable\n')
    tn.read_until(b'OLT# ')
    tn.write(b'show memory\n')
    time.sleep(0.2)
    result = tn.read_very_eager().decode('utf-8')[11:-6]
    tn.close()
    await message.answer(result)

# хэндлер на любое слово (на адрес)
@dp.message(F.text)
async def any_message(message: Message):
    if len(message.text.split(' ')) == 1:
        try:
            pon_line = message.text
            print(f"skanning all in {pon_line}`st line")
            await message.answer(pon_head_scan(str(message.text), 0))
        except:
            await message.answer("Ошибка!! бгбг")

    if len(message.text.split(' ')) == 2:
        try:
            pon_line = message.text.split(' ')[0]
            onu_number = message.text.split(' ')[1]
            print(f"Scanning onu {pon_line}-{onu_number}")
            await message.answer(pon_head_scan(pon_line, onu_number))
        except:
            await message.answer("Ошибка!! бгбг")



# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())