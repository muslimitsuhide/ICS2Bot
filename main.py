import telebot
from telebot import types

bot = telebot.TeleBot('token')


# Константы для идентификации состояний
START_STATE =   1
HELP_STATE =    2
EVENTS_STATE =  3
SUPPORT_STATE = 4
DONATE_STATE =  5

@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Помощь по боту')
    markup.row(btn1)
    btn2 = types.KeyboardButton('Список мероприятий')
    markup.row(btn2)
    btn3 = types.KeyboardButton('Техническая поддержка')
    markup.row(btn3)
    btn4 = types.KeyboardButton('Донаты')
    markup.row(btn4)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}\n', reply_markup=markup)
    # состояние пользователя устанавливаем в START_STATE
    bot.register_next_step_handler(message, on_click, state=START_STATE)


def on_click(message, **kwargs):
    state = kwargs.get('state')
    if message.text == 'Помощь по боту':
        bot.send_message(message.chat.id, '1')
        bot.register_next_step_handler(message, on_click, state=HELP_STATE)
    elif message.text == 'Список мероприятий':
        bot.send_message(message.chat.id, '2')
        bot.register_next_step_handler(message, on_click, state=EVENTS_STATE)
    elif message.text == 'Техническая поддержка':
        bot.send_message(message.chat.id, '3')
        bot.register_next_step_handler(message, on_click, state=SUPPORT_STATE)
    elif message.text == 'Донаты':
        bot.send_message(message.chat.id, '4')
        bot.register_next_step_handler(message, on_click, state=DONATE_STATE)


bot.polling(none_stop=True)