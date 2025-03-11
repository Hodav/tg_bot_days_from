from config import tg_token
from telebot import TeleBot, types
import schedule
from threading import Thread
from time import sleep
from datetime import datetime

bot = TeleBot(tg_token)
# info = {'746143816': {'notice': "123321",
#         'date': datetime.today()}}
info = {}


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, text='Ну че погнали?')

    bot.send_message(message.chat.id, 'Напиши событие и начнем считать дни')
    bot.register_next_step_handler(message, add_event)


@bot.message_handler(content_types=['text'])
def mes_handler(message):
    if message.text == "Проёб":
        info[message.chat.id]['date'] = datetime.today()
        bot.send_message(message.chat.id, f'Прогресс аннулирован')


def create_keyboard_with_buttons():
    button_switch_event = types.KeyboardButton('Поменять событие')
    button_lose_event = types.KeyboardButton('Проёб')
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(button_lose_event) #button_switch_event,
    return keyboard


def add_event(message: types.Message) -> None:
    info[message.chat.id] = {
        'notice': message.text,
        'date': datetime.today()
    }
    keyboard = create_keyboard_with_buttons()
    bot.send_message(
        message.chat.id,
        f'Событие "{message.text}" успешно добавлено. '
        f'Уведомления будут приходить в 8 утра каждый день',
        reply_markup=keyboard
    )


def send_notification():
    for chat_id, info_item in info.items():
        difference = datetime.today() - info_item['date']
        bot.send_message(chat_id, f'С начала события "{info_item['notice']}" прошло {difference.days}')


def scheduler():
    schedule.every().day.at("08:00").do(send_notification)  # Установите время, например, 10:00 утра
    # schedule.every().second.do(send_notification)
    while True:
        schedule.run_pending()
        sleep(1)


Thread(target=scheduler).start()

if __name__ == '__main__':
    bot.polling(none_stop=True)
