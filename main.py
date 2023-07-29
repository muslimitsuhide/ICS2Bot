import telebot
from telebot import types

bot = telebot.TeleBot('token')


# константы для идентификации состояний
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
        show_events(message.chat.id)
        bot.register_next_step_handler(message, on_click, state=EVENTS_STATE)
    elif message.text == 'Техническая поддержка':
        bot.send_message(message.chat.id, '3')
        bot.register_next_step_handler(message, on_click, state=SUPPORT_STATE)
    elif message.text == 'Донаты':
        bot.send_message(message.chat.id, '4')
        bot.register_next_step_handler(message, on_click, state=DONATE_STATE)


def show_events(chat_id):
    markup = types.InlineKeyboardMarkup()
    # данные будут браться из бд
    markup.add(types.InlineKeyboardButton('Мероприятие 1', callback_data='1'))
    markup.add(types.InlineKeyboardButton('Мероприятие 2', callback_data='2'))
    markup.add(types.InlineKeyboardButton('Мероприятие 3', callback_data='3'))
    markup.add(types.InlineKeyboardButton('Выход', callback_data='exit'))
    bot.send_message(chat_id, 'Выберите мероприятие:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # нужно продумать момент с тем, чтобы один пользователь только один раз мог записываться на мероприятие
    if call.data.isdigit(): 
        event_number = call.data
        bot.answer_callback_query(call.id, f'Вы записались на мероприятие: {event_number}', show_alert=True)
        # получаем ID чата пользователя, чтобы отправить сообщение
        chat_id = call.message.chat.id

        # отправляем сообщение с информацией о мероприятии
        bot.send_message(chat_id, f'Вы записались на мероприятие: {event_number}')

        # удаляем сообщение
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)

bot.polling(none_stop=True)