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
    reg_btn = types.KeyboardButton('Регистрация')
    markup.row(reg_btn)
    exit_btn = types.KeyboardButton('Выход')
    markup.row(exit_btn)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}\nЧтобы начать пользоваться ботом, нужно зарегистрироваться!', reply_markup=markup)

    bot.register_next_step_handler(message, handle_registration)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, '🤖 ICS2 Bot дает возможность студентам записываться на любые учебные мероприятия заранее, дабы избежать неприятных ситуаций, которые, к сожалению, нередко возникают.\n\n'
                    '⭐️ Удобства:\n\n- Интуитивно понятный интерфейс;\n- Экономия времени и нервов;\n- Возможность заранее узнать, какие вопросы попадутся именно тебе на РК;\n'
                    '- Возможность узнавать о всех мероприятиях заблаговременно, чтобы успеть распланировать свой день.\n\n'
                    '💬 По вопросам работы бота связаться с его создателем можно тут — @muslimitsuhide 🦄.\n\n'
                    '🚀 Я также буду постепенно выносить часто задаваемые вопросы и проблемы в /faq.')
    

@bot.message_handler(commands=['faq'])
def faq(message):
    bot.send_message(message.chat.id, '<b>1. У меня ничего не происходит при отправке текста боту, что делать?</b>\n\n'
                    'Убедитесь, что вы сначала ввели команду /start. Если вы не уверены в этом, попробуйте сделать /start и снова нажать на кнопку. '
                    'Если проблема все еще осталась, обратитесь разработчику @muslimitsuhide.', parse_mode='HTML')


@bot.message_handler(commands=['add_event'])
def add_event(message):
    # проверяем, является ли пользователь админом
    if message.from_user.id == id:
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

    bot.send_message(message.chat.id, f'Имя: {name}\nФамилия: {surname}\nГруппа: {group_user}')
    new_markup = types.ReplyKeyboardMarkup()
    true_btn = types.KeyboardButton('✅')
    new_markup.row(true_btn)
    false_btn = types.KeyboardButton('❌')
    new_markup.row(false_btn)
    bot.register_next_step_handler(message, varif)
    bot.send_message(message.chat.id, 'Данные введены корректно?', reply_markup=new_markup)


def varif(message):
    if message.text == '✅':
        conn = sqlite3.connect('users.sql')
        cur = conn.cursor()

        cur.execute(f"INSERT INTO users (name, surname, group_user) VALUES ('%s', '%s', '%s')" % (name, surname, group_user))
        conn.commit()
        cur.close()
        conn.close()

        markup = types.ReplyKeyboardMarkup()
        help_btn = types.KeyboardButton('Помощь по боту')
        markup.row(help_btn)
        list_btn = types.KeyboardButton('Список мероприятий')
        markup.row(list_btn)
        sup_btn = types.KeyboardButton('Техническая поддержка')
        markup.row(sup_btn)
        donate_btn = types.KeyboardButton('Донаты')
        markup.row(donate_btn)
        # состояние пользователя устанавливаем в START_STATE
        bot.register_next_step_handler(message, on_click, state=START_STATE)
        bot.send_message(message.chat.id, 'Пользователь зарегестрирован!', reply_markup=markup)
    else:
        bot.send_message(message.chat.id,'Пользователь не зарегистрирован, регистрация отменена')
        main(message)


def on_click(message, **kwargs):
    state = kwargs.get('state')
    if message.text == 'Помощь по боту':
        bot.send_message(message.chat.id, '🤖 ICS2 Bot дает возможность студентам записываться на любые учебные мероприятия заранее, дабы избежать неприятных ситуаций, которые, к сожалению, нередко возникают.\n\n'
                        '⭐️ Удобства:\n\n- Интуитивно понятный интерфейс;\n- Экономия времени и нервов;\n- Возможность заранее узнать, какие вопросы попадутся именно тебе на РК;\n'
                        '- Возможность узнавать о всех мероприятиях заблаговременно, чтобы успеть распланировать свой день.\n\n'
                        '💬 По вопросам работы бота связаться с его создателем можно тут — @muslimitsuhide 🦄.\n\n'
                        '🚀 Я также буду постепенно выносить часто задаваемые вопросы и проблемы в /faq.')
        bot.register_next_step_handler(message, on_click, state=HELP_STATE)

    elif message.text == 'Список мероприятий':
        show_events(message.chat.id)
        bot.register_next_step_handler(message, on_click, state=EVENTS_STATE)

    elif message.text == 'Техническая поддержка':
        bot.send_message(message.chat.id, '💬 Для всех пользователей поддержка осуществляется через личные сообщения @muslimitsuhide.')
        bot.register_next_step_handler(message, on_click, state=SUPPORT_STATE)

    elif message.text == 'Донаты':
        bot.send_message(message.chat.id, '💬 Донатов не будет, мне стало впадлу.')
        bot.register_next_step_handler(message, on_click, state=DONATE_STATE)

    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите действие из предложенных кнопок.')


def show_events(chat_id):
    # получаем данные мероприятий из бд
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

    conn = sqlite3.connect('user_events.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS user_events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, event_id INTEGER, order_number INTEGER)')
    conn.commit()

    cur.close()
    conn.close()

    return events_data


def add_user_event(user_id, event_id):
    conn = sqlite3.connect('user_events.sql')
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM user_events WHERE user_id = ? AND event_id = ?', (user_id, event_id))
    result = cur.fetchone()
    count = result[0] if result else 0

    # проверяем, сколько уже пользователей записано на это мероприятие
    cur.execute('SELECT COUNT(*) FROM user_events WHERE event_id = ?', (event_id,))
    result = cur.fetchone()
    if result and count == 0:
        order_number = result[0] + 1
    else:
        order_number = 1

    # добавляем запись о пользователе на мероприятие
    cur.execute('INSERT INTO user_events (user_id, event_id, order_number) VALUES (?, ?, ?)', (user_id, event_id, order_number))
    conn.commit()

    cur.close()
    conn.close()

    return order_number, count


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    order_number, count = add_user_event(call.from_user.id, call.data)
    event_name, event_date = call.data.split("|")
    
    if "|" in call.data and count == 0:
        bot.answer_callback_query(call.id, f'Вы записались на мероприятие: {event_name}', show_alert=True)
        # получаем ID чата пользователя, чтобы отправить сообщение
        chat_id = call.message.chat.id

        # отправляем сообщение с информацией о мероприятии
        bot.send_message(chat_id, f'Вы записались на {event_name}\nДата: {event_date}\nВаш номер в очереди: {order_number}')

        # удаляем сообщения
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)
    else:
        chat_id = call.message.chat.id
        bot.send_message(chat_id, f'Вы уже записаны на {event_name}!\nДата: {event_date}\nВаш номер в очереди: {order_number}')

        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id - 1)

bot.polling(none_stop=True)