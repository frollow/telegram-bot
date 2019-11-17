import telebot
from telebot import apihelper

# proxy can be taken from https://hideip.me/ru/proxy/socks5list
apihelper.proxy = {'https': 'socks5h://167.86.121.208:40032'}
bot = telebot.TeleBot("849096211:AAFch0p-tgdAGIs40yNPD_UrCBBuEjroWZY")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, calculate())


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, message.text)


def calculate():
    sum = 4 + 8
    return sum


bot.polling()
