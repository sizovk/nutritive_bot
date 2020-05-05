import logging
import os
import telebot

bot = telebot.TeleBot(os.getenv("NUTRITIVE_BOT_TOKEN"))

@bot.message_handler(commands=["start", "help"])
def welcome_message(message):
    bot.reply_to(message, "Hey, my friend!")

if __name__ == "__main__":
    bot.infinity_polling()