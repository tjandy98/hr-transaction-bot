from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import sqlite3
import time

import logging
import uuid
ACTION, AMOUNT, AMOUNTRESPONSE, TRANSACTION, CATEGORIES, START = range(6)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

tempAmount = 0
tempComment = ""
tempCategory = ""


# -------- Insert your Telegram bot token below ------------
TOKEN = ""
def start_callback(update, context):
    reply_keyboard = [['Add Transaction', 'View Transactions']]
    update.message.reply_text("Hello! What can I do for you today?",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    user = update.message.from_user
    print(user.id)
    return CATEGORIES


def add_transaction(update, context):
    global tempCategory
    tempCategory = update.message.text

    update.message.reply_text("Please enter the amount: ")

    return AMOUNT


def add_transaction_response(update, context):
    user = update.message.from_user
    logger.info("Message from %s %s", user.first_name, update.message.text)

    user_response = update.message.text
    if (user_response.replace('.', '', 1).isdigit()):
        global tempAmount
        tempAmount = float(user_response)
        update.message.reply_text("Please enter comment or send /skip if you don't want to: ")

        return AMOUNTRESPONSE
    else:
        update.message.reply_text("Invalid amount entered! Please enter a valid number: ")

        return AMOUNT


def skip_comment(update, context):
    return AMOUNTRESPONSE


def save_transaction(update, context):
    global tempComment
    user_response = update.message.text
    if (user_response != "/skip"):
        tempComment = user_response



    uniqueid = str(uuid.uuid4())

    conn = sqlite3.connect('transactions.db')
    c = conn.cursor()
    temptime = time.strftime('%Y-%m-%d %H:%M:%S')
    user = update.message.from_user

    sql_statement = 'INSERT INTO transactions VALUES( "{}","{}", {}, "{}", "{}", "{}")'.format(uniqueid, user.id,
                                                                                               tempAmount, tempComment,
                                                                                               tempCategory, temptime)
    print(sql_statement)  # uuid,name,amount,comment,category,data
    c.execute(sql_statement)
    conn.commit()
    conn.close()
    update.message.reply_text("Transaction Saved!")
    update.message.reply_text("Send /start to show options")
    return ConversationHandler.END


def select_action_handler(update, context):
    user_response = update.message.text
    if (user_response == "Add Transaction"):

        reply_keyboard = [['Food', 'Transport', 'Entertainment']]

        update.message.reply_text("Please select a category: ",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return TRANSACTION
    elif (user_response == "View Transactions"):
        conn = sqlite3.connect('transactions.db')
        c = conn.cursor()

        c.execute('SELECT amount, comment, category, createdDate FROM transactions WHERE user={}'.format(update.message.from_user.id))
        conn.commit()
        data = c.fetchall()
        conn.close()
        import tabulate

        dataList = []
        for i in data:
            dataList.append(list(i))

        print(dataList)

        headers = ["amount", "comment", "category", "date"]
        htmlfile = tabulate.tabulate(dataList, headers=headers, tablefmt="html")
        print(htmlfile)
        formattedHtml = '<html> <head> <meta name="viewport" content="width=device-width, initial-scale=1.0"> <style type="text/css"> table,th,td{{border:1px solid black;}}</style> </head> <body>{} </body>  </html>'.format(
            htmlfile)

        Html_file = open("filename.html", "w")
        Html_file.write(formattedHtml)
        Html_file.close()
        print(tabulate.tabulate(dataList, headers=headers, tablefmt="html"))
        data = tabulate.tabulate(dataList, headers=headers)
        print(data)
        update.message.reply_text(data)

        context.bot.send_message(chat_id=update.effective_chat.id, text="Generating file...")

        context.bot.send_document(chat_id=update.message.chat_id, document=open("filename.html", 'rb'))

        update.message.reply_text("Send /start to show options")



    else:

        return START
    return ConversationHandler.END



def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_callback)],

        states={
            ACTION: [MessageHandler(Filters.regex('^(Add Transaction|View Transactions)$'),
                                    add_transaction)],
            AMOUNT: [MessageHandler(Filters.text, add_transaction_response), CommandHandler('skip', skip_comment)],
            AMOUNTRESPONSE: [MessageHandler(Filters.text, save_transaction)],
            TRANSACTION: [MessageHandler(Filters.text, add_transaction)],
            CATEGORIES: [MessageHandler(Filters.text, select_action_handler)],
            START: [MessageHandler(Filters.text, start_callback)]

        },
        fallbacks=[CommandHandler('cancel', unknown)]
    )


    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


main()