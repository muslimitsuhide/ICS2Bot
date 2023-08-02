import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('token')

name = None
surname = None
group_user = None

new_event_name = None
new_event_date = None

# константы для идентификации состояний
START_STATE =   1
HELP_STATE =    2
EVENTS_STATE =  3
SUPPORT_STATE = 4
DONATE_STATE =  5

@bot.message_handler(commands=['start'])
def main(message):
    conn = sqlite3.connect('users.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), surname varchar(50), group_user varchar(20))')
    conn.commit()
    cur.close()
    conn.close()

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Регистрация')
    markup.row(btn1)
    btn2 = types.KeyboardButton('Выход')
    markup.row(btn2)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}\nЧтобы начать пользоваться ботом, нужно зарегистрироваться!', reply_markup=markup)

    bot.register_next_step_handler(message, handle_registration)


@bot.message_handler(commands=['add_event'])
def add_event(message):
    # проверяем, является ли пользователь админом
    if message.from_user.id == admin_id:
        conn = sqlite3.connect('events.sql')
        cur = conn.cursor()

        cur.execute('CREATE TABLE IF NOT EXISTS events (event_id int auto_increment primary key, event_name varchar(50), event_date varchar(50))')
        conn.commit()
        cur.close()
        conn.close()

        bot.send_message(message.chat.id, 'Введите название мероприятия:')
        bot.register_next_step_handler(message, event_name_input)
    else:
        bot.send_message(message.chat.id, 'Вы не обладаете правами администратора')


def event_name_input(message):
    global new_event_name
    new_event_name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите дату мероприятия:')
    bot.register_next_step_handler(message, event_date_input)


def event_date_input(message):
    global new_event_date
    new_event_date = message.text.strip()
    
    conn = sqlite3.connect('events.sql')
    cur = conn.cursor()

    cur.execute(f"INSERT INTO events (event_name, event_date) VALUES ('%s', '%s')" % (new_event_name, new_event_date))
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Мероприятие добавлено!') 


def handle_registration(message):
    if message.text == 'Регистрация':
        bot.send_message(message.chat.id, 'Введите свое настоящее имя:')
        bot.register_next_step_handler(message, user_name)
    elif message.text == 'Выход':
        bot.send_message(message.chat.id, 'Вы отменили регистрацию.', reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите действие из предложенных кнопок.')


def user_name(message): 
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, f'Введите свою настоящую фамилию:')
    bot.register_next_step_handler(message, user_surname)


def user_surname(message): 
    global surname
    surname = message.text.strip()
    bot.send_message(message.chat.id, f'Введите свою группу:')
    bot.register_next_step_handler(message, user_group)


def user_group(message): 
    global group_user
    group_user = message.text.strip()

    bot.send_message(message.chat.id, f'Данные введены корректно?\nИмя: {name}\nФамилия: {surname}\nГруппа: {group_user}')
    new_markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('✅')
    new_markup.row(btn1)
    btn2 = types.KeyboardButton('❌')
    new_markup.row(btn2)
    bot.register_next_step_handler(message, varif)
    bot.send_message(message.chat.id, 'Нажмите кнопку:', reply_markup=new_markup)


def varif(message):
    if message.text == '✅':
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()

        cur.execute(f"INSERT INTO users (name, surname, group_user) VALUES ('%s', '%s', '%s')" % (name, surname, group_user))
        conn.commit()
        cur.close()
        conn.close()

        markup = types.ReplyKeyboardMarkup()
        btn1 = types.KeyboardButton('Помощь по боту')
        markup.row(btn1)
        btn2 = types.KeyboardButton('Список мероприятий')
        markup.row(btn2)
        btn3 = types.KeyboardButton('Техническая поддержка')
        markup.row(btn3)
        btn4 = types.KeyboardButton('Донаты')
        markup.row(btn4)
        # состояние пользователя устанавливаем в START_STATE
        bot.register_next_step_handler(message, on_click, state=START_STATE)
        bot.send_message(message.chat.id, 'Пользователь зарегестрирован!', reply_markup=markup)
    else:
        bot.send_message(message.chat.id,'Пользователь не зарегистрирован, регистрация отменена')
        main(message)


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
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите действие из предложенных кнопок.')


def show_events(chat_id):
    # Получаем данные мероприятий из бд
    events_data = get_events_data()

    if not events_data:
        bot.send_message(chat_id, 'Нет доступных мероприятий.')
        return

    markup = types.InlineKeyboardMarkup()
    for event_name, event_date in events_data:
        callback_data = f'{event_name}|{event_date}'
        event_btn = types.InlineKeyboardButton(event_name, callback_data=callback_data)
        markup.add(event_btn)

    bot.send_message(chat_id, 'Выберите мероприятие:', reply_markup=markup)


def get_events_data():
    conn = sqlite3.connect('events.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS events (event_id INTEGER PRIMARY KEY AUTOINCREMENT, event_name VARCHAR(50), event_date VARCHAR(20))')
    conn.commit()

    cur.execute('SELECT event_name, event_date FROM events')
    events_data = cur.fetchall()

    conn.close()

    return events_data


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # нужно продумать момент с тем, чтобы один пользователь только один раз мог записываться на мероприятие
    if "|" in call.data:
        event_name, event_date = call.data.split("|")
        bot.answer_callback_query(call.id, f'Вы записались на мероприятие: {event_name}', show_alert=True)
        # получаем ID чата пользователя, чтобы отправить сообщение
        chat_id = call.message.chat.id

        # отправляем сообщение с информацией о мероприятии
        bot.send_message(chat_id, f'Вы записались на мероприятие: {event_name}\nДата: {event_date}')

        # удаляем сообщения
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)

bot.polling(none_stop=True)