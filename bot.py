import logging
import os
import telebot

from yaml_util import load_yml_file

bot = telebot.TeleBot(os.getenv("NUTRITIVE_BOT_TOKEN"))
messages_base = load_yml_file("messages.yml")
nutrients_base = load_yml_file("nutrients.yml")

@bot.message_handler(commands=["start", "help"])
def welcome_message(message):
    bot.reply_to(message, messages_base["welcome_message"].format(name="Kirill"))

if __name__ == "__main__":
    bot.infinity_polling()