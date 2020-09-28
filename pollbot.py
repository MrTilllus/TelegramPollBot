#!/usr/bin/env python

import logging, re, datetime, time

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Location
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


bot_token = 'BOTTOKEN'
chat_id = 'CHATID'
pollreset = datetime.time(hour=22, minute=30)
polltime = datetime.time(hour=19, minute=30)
daytorunpoll = 6  # 0:Monday, 1:Tuesday, ....
daytoresetpoll = 3
text1 = 'first answer'
text2 = 'second answer'
day = 3 # day for the event || 0:Monday, 1:Tuesday, ....
# Poll Message in Poll function

textuser1 = 'positiv'
textuser2 = 'negative'
textuserended1 = 'positiv'
textuserended2 = 'negative'

pollendmessage = 'poll ended!'

#If you want to send a location comment out the line with the comment location
#loc = Location(0.0, 0.0) 


bot = telegram.Bot(token=bot_token)
polluser = []
query = False

keyboard = [[InlineKeyboardButton(text1, callback_data='1')], [
    InlineKeyboardButton(text2, callback_data='2')]]
keyboard_reset = []

reply_markup = InlineKeyboardMarkup(keyboard)
reset_markup = InlineKeyboardMarkup(keyboard_reset)

TYPING_CHOICE = range(1)


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead < 0:  # Target day already happened this week
        days_ahead += 7

    return d + datetime.timedelta(days_ahead)


def next_day():
    d = datetime.date(time.localtime()[0], time.localtime()[1], time.localtime()[2])
    next_day = next_weekday(d, day)
    next_day = str(next_day.strftime("%d.%m.%Y"))
    return next_day

pollmessage = ''

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def poll():
    global pollmessage
    pollmessage = next_day() + 'MESSAGE' #Message next_day() calculate the next date of the defined day
    # bot.sendLocation(chat_id=chat_id, location=loc) #location
    message = bot.send_message(chat_id=chat_id, text=pollmessage, reply_markup=reply_markup)

def pollen(update):
    poll()

def pollen_by_command(update, context):
    poll()

def button(update,context):
    global query
    query = update.callback_query
    # addtext = ""
    us = ""
    id = str(query.from_user['id'])
    des = str(query.data)
    if des == "0":
        bot.send_message(chat_id=chat_id, text='Poll over!')
        return

    if query.from_user["username"]:
        us = '@' + str(query.from_user["username"])
    elif query.from_user["first_name"]:
        us = str(query.from_user["first_name"])
    else:
        us = str(query.from_user["last_name"])

    if [id, des, us] in polluser:
        return
    else:
        if [id, "2", us] in polluser:
            polluser[polluser.index([id, "2", us])][1] = "1"
            
        elif [id, "1", us] in polluser:
            polluser[polluser.index([id, "1", us])][1] = "2"

        else:   
            polluser.append([id, des, us])

    query.edit_message_text(text = pollmessage + combineText(polluser), reply_markup = reply_markup)

def combineText(arr):
    text = ''
    for x in arr:
        des = x[1]
        us = x[2]
        if des == "1":
            text = text + " \n" + us + textuser1

        elif des == "2":
            text = text + " \n" + us + textuser2
    return text

def combineText_past(arr):
    text = ''
    for x in arr:
        des = x[1]
        us = x[2]
        if des == "1":
            text = text + " \n" + us + textuserended1

        elif des == "2":
            text = text + " \n" + us + textuserended2
    return text

def reset():
    global query
    global polluser

    if query:
        query.edit_message_text(text= pollendmessage + '\n' + combineText_past(polluser), reply_markup=reset_markup)
        query = False

    polluser = []

def reset_call(update):
    reset()

def reset_by_command(update, context):
    reset()


if __name__ == '__main__':
    updater = Updater(bot_token, use_context=True)
    jobQ = updater.job_queue

    dp = updater.dispatcher

    jobQ.run_daily(pollen, polltime, days=(daytorunpoll, ))
    jobQ.run_daily(reset_call, pollreset, days=(daytoresetpoll, ))

    dp.add_handler(CommandHandler("pollen", pollen_by_command))
    dp.add_handler(CommandHandler("reset", reset_by_command))
    dp.add_handler(CallbackQueryHandler(button))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()
