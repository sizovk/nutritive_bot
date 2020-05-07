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

@bot.message_handler(commands=["all"])
def all_nutrients(message):
    index = 1
    nutrients_list = []
    for name, data in nutrients_base.items():
        nutrients_list.append(messages_base["nutrients_list_item"].format(index=index, name=data["name"], symbol=data["symbol"]))
        index += 1
    bot.reply_to(message, messages_base["all_nutrients"].format(nutrients_list="".join(nutrients_list)))

@bot.message_handler(commands=["info"])
def info_nutrient(message):
    given_text = message.text[6:]
    if given_text in nutrients_base:
        nutr = nutrients_base[given_text] 
        bot.reply_to(message, messages_base["info_nutrient"].format(name=nutr["name"], symbol=nutr["symbol"], produced=nutr["produced"], properties=nutr["properties"]))
    else:
        bot.reply_to(message, messages_base["no_nutrient_with_given_symbol"])

@bot.message_handler(content_types=["text"])
def only_text(message):
    bot.reply_to(message, messages_base["no_commands_message"])

if __name__ == "__main__":
    bot.infinity_polling()