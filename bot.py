#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import json
import logging
import requests
from hurry.filesize import size, verbose
from userprofile import User
from config import vultr_key , telegram_api_key , instance_id

from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)

user = User()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

GET_BANDWIDTH, CONVERT_DATA , GET_PROFILE_INFO = range(3)
JSON_DATA = None


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> int:
    '''Send a message when the command /start is issued.'''
    reply_keyboard = [['Get bandwidth'] ,['Get profile info'], ['Cancel']]
    update.message.reply_text(
        'Hi! I am admin here. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Do you want to get server data for some day? ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=''
        ),
    )
    return GET_BANDWIDTH


def help_command(update: Update, context: CallbackContext) -> None:
    '''Send a message when the command /help is issued.'''
    update.message.reply_text('Help!')


def cancel(update: Update, context: CallbackContext) -> int:
    '''Cancels and ends the conversation.'''
    user = update.message.from_user
    logger.info('User %s canceled the conversation.', user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def get_profile_info(update: Update,context: CallbackContext) -> int:
    reply_keyboard = [['Get bandwidth', 'Cancel']]
    logger.info('Getting user info')
    update.message.reply_text(f'{user.get_user_email()} \n {user.get_user_name()} \n {user.get_user_userid()}' ,reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Wanna finish or take another measure ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder=''))
    return GET_BANDWIDTH


def get_vultr_info(update: Update, context: CallbackContext) -> int:
    logger.info('Method get_vultr was executed')
    url = 'https://api.vultr.com/v2/instances/{}/bandwidth'.format(instance_id)
    headers = {'Authorization': 'Bearer {}'.format(vultr_key),
               'Content-Type': 'application/json'}

    data = {
        'bandwidth': {
            'server_time': {
                'incoming_bytes': '',
                'outgoing_bytes': ''
            }
        }
    }
    response = requests.get(url, data=json.dumps(data), headers=headers)
    global JSON_DATA
    JSON_DATA = response.json()
    reply_keyboard = [[]]
    for i in JSON_DATA['bandwidth']:
        reply_keyboard.append([i])
    update.message.reply_text('Select the date of bandwidth usage', reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Select date of usage:')
    )

    return CONVERT_DATA


def convert_data(update: Update, context: CallbackContext) -> int:
    global JSON_DATA
    global incoming_bytes
    global outcoming_bytes
    reply_keyboard = [['Get bandwidth', 'Get profile info']]
    logger.info('Method convert_data was executed')
    data = update.message.text
    for i in JSON_DATA['bandwidth']:
        if data == i:
            incoming_bytes = JSON_DATA['bandwidth'][str(i)]['incoming_bytes']
            outcoming_bytes = JSON_DATA['bandwidth'][str(i)]['outgoing_bytes']
            update.message.reply_text(
                '⬇️ ' + size(incoming_bytes, system=verbose) + ' \n' +
                '⬆️ ' + size(outcoming_bytes, system=verbose)
            )
    update.message.reply_text(
        'Wanna finish or take another measure ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder=''))
    return GET_BANDWIDTH


def main() -> None:
    '''Start the bot.'''

    # Create the Updater and pass it your bot's token.
    updater = Updater(telegram_api_key)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_BANDWIDTH: [
                MessageHandler(Filters.regex('^(Get profile info)$'), get_profile_info),
                MessageHandler(Filters.regex('^(Get bandwidth)$'), get_vultr_info),
                MessageHandler(Filters.regex('^(Cancel)$'), cancel)
                ],
                
            CONVERT_DATA: [MessageHandler(Filters.regex(
                '^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
            ), convert_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(CommandHandler('get_vultr_info', get_vultr_info))
    dispatcher.add_handler(CommandHandler('get_profile_info',get_profile_info))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()