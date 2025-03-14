from config import tg_token
from telebot import TeleBot, types
import schedule
from threading import Thread
from time import sleep
from datetime import date
from db_manager import DBManager
from utils import join_date

bot = TeleBot(tg_token)
db_manager = DBManager()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, text='Ну че погнали?')

    bot.send_message(message.chat.id, 'Напиши событие и начнем считать дни')
    bot.register_next_step_handler(message, add_event)


@bot.message_handler(content_types=['text'])
def mes_handler(message):
    if message.text == "Проёб":
        user_data = db_manager.read(message.chat.id)
        if user_data:
            user_id, event_name, event_dates = user_data

            db_manager.update(user_id, event_name, join_date(event_dates, date.today()))
            bot.send_message(message.chat.id, f'Прогресс аннулирован')


def create_keyboard_with_buttons() -> types.ReplyKeyboardMarkup:
    button_switch_event = types.KeyboardButton('Поменять событие')
    button_lose_event = types.KeyboardButton('Проёб')
    keyboard = types.ReplyKeyboardMarkup(row_width=1)
    keyboard.add(button_lose_event) #button_switch_event,
    return keyboard


def add_event(message: types.Message) -> None:
    data = db_manager.read(message.chat.id)
    keyboard = create_keyboard_with_buttons()
    if data:
        db_manager.update(message.chat.id, message.text, str(date.today()))
    else:
        db_manager.create(message.chat.id, message.text, str(date.today()))

    bot.send_message(
        message.chat.id,
        f'Событие "{message.text}" успешно создано. '
        f'Уведомления будут приходить в 8 утра каждый день',
        reply_markup=keyboard
    )


def send_notification() -> None:
    data = db_manager.read_all()

    for chat_id, event_name, event_dates in data:
        result = 'С начала события "{0}" прошло {1} '
        last_date = date.fromisoformat(event_dates[-1])
        difference_date = date.today() - last_date
        days_from = difference_date.days

        if str(days_from)[-1] in '056789':
            result += 'дней'
        elif str(days_from)[-1] in '234':
            result += 'дня'
        else:
            result += 'день'

        bot.send_message(chat_id, result.format(event_name, days_from))


def scheduler():
    schedule.every().day.at("08:00").do(send_notification)  # Установите время, например, 10:00 утра
    # schedule.every(100).seconds.do(send_notification)
    while True:
        schedule.run_pending()
        sleep(1)


# Thread(target=scheduler).start()

if __name__ == '__main__':
    bot.polling(none_stop=True)
