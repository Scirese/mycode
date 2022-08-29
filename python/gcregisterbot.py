# This file is a part of Scriese's shit code archive.
#
# Copyright 2022-2022 Scriese <nuclearlight91@gmail.com> and contributors.
#
# Use of this source code is governed by the GNU GPLv3 license that can be found through the following link
#
# https://github.com/Scirese/shitmounts/blob/main/LICENSE
#
# This script is designed to be a Telegram bot for Grasscutter's account registration.
# It can check the complexity of user's username using entropy and can refuse if it's not complex enough.
# (Because Grasscutter doesn't support real password) A string has 8 letters with no repetition is enough.
# The script takes user's telegram userID as in-game uid.


import json
import telebot
import requests
import math
from telebot.apihelper import ApiTelegramException

bot_token = ""
server_address = ""
server_token = ""
group = ""
welcome_message = """
欢迎使用注册机器人。
"""

bot = telebot.TeleBot(bot_token)


def extract_arg(arg):
    """Parse command received from user"""
    return arg.split()[1:]


def entropy(string, base=2.0):
    """Calculate the Entropy of a string"""
    dct = dict.fromkeys(list(string))
    pkvec = [float(string.count(c)) / len(string) for c in dct]
    h = -sum([pk * math.log(pk) / math.log(base) for pk in pkvec])
    return h


def runcommand(command):
    """Post command to OpenCommand plugin and execute it"""
    url = "https://" + server_address + "/opencommand/api"
    body = {
     "token": server_token,
     "action": "command",
     "data": command
    }
    resp = json.loads(requests.post(url, json=body).text)
    return resp


def are_u_in(chat_id, user_id):
    """Check if a user is in a Group or Channel"""
    try:
        bot.get_chat_member(chat_id, user_id)
        return True
    except ApiTelegramException as e:
        if e.result_json['description'] == 'Bad Request: user not found':
            return False


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, welcome_message + "\n使用 /register <用户名> 注册."
                                            "\n建议使用一串足够复杂的字符+你想要的名字来注册."
                                            "\n注册后的UID就是你的TelegramID.")


@bot.message_handler(commands=['register'])
def register(message):
    arg = extract_arg(message.text)

    if arg:
        if len(arg) > 1:
            bot.send_message(message.chat.id, "使用方法：/register <用户名>")
        else:
            if entropy(arg[0]) < 3:
                bot.send_message(message.chat.id, "你的用户名不够复杂.")
            else:
                if not are_u_in(group, message.from_user.id):
                    bot.send_message(message.chat.id, "请先加入" + group + "群组.")
                else:
                    command = "account create " + arg[0] + " " + str(message.from_user.id)
                    ret = runcommand(command)
                    if ret['retcode'] != 200:
                        reply = "注册失败！ 原因:\n" + ret["data"]
                    else:
                        reply = "注册成功！" \
                                "\n您的UID: " + message.from_user.id + \
                                "\n您的用户名: " + arg[0] + \
                                "\n快去愉快的玩耍吧!"
                    bot.send_message(message.chat.id, reply)
    else:
        bot.send_message(message.chat.id, "使用方法：/register <用户名>")


bot.infinity_polling()
