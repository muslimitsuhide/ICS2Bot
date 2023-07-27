import telebot

bot = telebot.TeleBot('token')


@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}\n')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Help information:')


bot.infinity_polling()