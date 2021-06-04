import os
import requests
import telebot

from flask import Flask, request

APP_NAME = os.environ["APP_NAME"]
PASTEBIN_API_KEY = os.environ["PASTEBIN_API_KEY"]
TELEGRAM_API_KEY = os.environ["TELEGRAM_API_KEY"]

bot = telebot.TeleBot(TELEGRAM_API_KEY)

server = Flask(__name__)


def get_paste_url(paste, language):
    data = {
        "api_option": "paste",
        "api_dev_key": PASTEBIN_API_KEY,
        "api_paste_private": "0",
        "api_paste_name": "Generated by " + APP_NAME,
        "api_paste_expire_date": "1D",
        "api_paste_format": language,
        "api_paste_code": paste
    }

    r = requests.post("https://pastebin.com/api/api_post.php", data=data)
    return r.text


def detect_language(text):
    kotlin = ['fun', 'Unit', 'val', 'var', 'suspend', 'vararg', 'typealias', 'init'
              'inline', 'crossinline', 'reified', 'noinline', 'object', 'when', 'override']
    java = ['void', 'public', '@Override', 'static', 'instanceof', 'new', 'extends', 'synchronized']
    ftext = text.split(' ')
    fkotlin = 0
    fjava = 0
    for word in ftext:
        if word in kotlin:
            fkotlin += 1
        if word in java:
            fjava += 1
    if fjava > fkotlin:
        return "java"
    if fjava < fkotlin:
        return "kotlin"
    else:
        return "text"


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    link = get_paste_url(message.text, detect_language(message.text))
    if link.startswith("https://"):
        bot.send_message(message.chat.id, link)
    else:
        bot.send_message(message.chat.id, "Error, sorry:(")


@server.route("/bot", methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


bot.remove_webhook()
bot.set_webhook(url="https://{}.herokuapp.com/bot".format(APP_NAME))
server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = Flask(__name__)
