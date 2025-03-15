from config import tg_token
from telebot import TeleBot, types
import schedule
from threading import Thread
from time import sleep
from datetime import date
from db_manager import DBManager
from utils import *

bot = TeleBot(tg_token)
db_manager = DBManager()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, text='Ну че погнали?')

    bot.send_message(message.chat.id, 'Напиши событие и начнем считать дни')
    bot.register_next_step_handler(message, add_event)


def change_name_event(message: types.Message) -> None:
    db_manager.update_name_event(message.chat.id, message.text)
    bot.send_message(message.chat.id, f'Событие изменено на "{message.text}"')


def change_date_event(message: types.Message) -> None:
    try:
        cur_date = date.fromisoformat(message.text)
        if is_future(cur_date):
            bot.send_message(
                message.chat.id,
                '<i><b>"Будущее не предопределено. Нет судьбы, кроме той, что мы создаем сами."</b></i>\n' +
                'Сара Коннор | "Терминатор 2: Судный день" (1991)\n\n' +
                'Ты укзала дату из будущего. Отметь ее в когда она настанет',
                parse_mode="HTML")
            return
        db_manager.update_event_dates(message.chat.id, str(cur_date))
        bot.send_message(message.chat.id, f'Дата успешно изменена на {str(cur_date)}')
        send_notification(*db_manager.read(message.chat.id))
    except Exception:
        bot.send_message(
            message.chat.id,
            'Дата введена не верно попробуй еще раз\n' +
            'Пример:\n2025-03-15')
        bot.register_next_step_handler(message, change_date_event)


@bot.message_handler(content_types=['text'])
def mes_handler(message):
    if message.text == "Начать сначала":
        user_data = db_manager.read(message.chat.id)
        if user_data:
            user_id, event_name, *event_dates = user_data
            db_manager.update_event_dates(user_id, join_date(','.join(event_dates), str(date.today())))
            bot.send_message(message.chat.id, f'Прогресс аннулирован')
    if message.text == "Поменять событие":
        bot.send_message(message.chat.id, 'Напиши новое событие')
        bot.register_next_step_handler(message, change_name_event)
    if message.text == 'Установить стартовую дату':
        bot.send_message(
            message.chat.id,
            'Напиши дату с которой начнем считать\n' +
            'в формате ГГГГ-ММ-ДД\n' +
            'Например:\n2025-03-15')
        bot.register_next_step_handler(message, change_date_event)


def create_keyboard_with_buttons() -> types.ReplyKeyboardMarkup:
    button_switch_event = types.KeyboardButton('Поменять событие')
    button_lose_event = types.KeyboardButton('Начать сначала')
    input_date_event = types.KeyboardButton('Установить стартовую дату')
    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    keyboard.add(button_lose_event, button_switch_event, input_date_event)  # button_switch_event,
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


def send_notification(chat_id, event_name, event_dates) -> None:
    if not event_dates:
        bot.send_message(chat_id, 'Данные о датах были стерты( \nНачнем с сегодня\nПростити')
        event_dates = str(date.today())
        db_manager.update_event_dates(chat_id, event_dates)

    event_dates_list = event_dates.split(',')
    last_date = date.fromisoformat(event_dates_list[-1])
    difference_date = date.today() - last_date
    days_from = difference_date.days

    result = 'С начала события "{0}" прошло {1} '
    if str(days_from)[-1] in '056789':
        result += 'дней'
    elif str(days_from)[-1] in '234':
        result += 'дня'
    else:
        result = result.replace('прошло', 'прошел') + 'день'

    bot.send_message(chat_id, result.format(event_name, days_from))

    if len(event_dates_list) > 1:
        difference_list = []
        for i in range(len(event_dates_list) - 1):
            cur_date = date.fromisoformat(event_dates_list[i])
            after_date = date.fromisoformat(event_dates_list[i + 1])
            dif = after_date - cur_date
            difference_list.append(str(dif.days))

        bot.send_message(chat_id, f'Предыдущие успехи\n{' | '.join(difference_list)}')


def send_notification_all_users() -> None:
    data = db_manager.read_all()

    for chat_id, event_name, event_dates in data:
        send_notification(chat_id, event_name, event_dates)


def scheduler():
    schedule.every().day.at("08:00").do(send_notification)  # Установите время, например, 10:00 утра
    # schedule.every(100).seconds.do(send_notification)
    while True:
        schedule.run_pending()
        sleep(1)


Thread(target=scheduler).start()

if __name__ == '__main__':
    bot.polling(none_stop=True)
