#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import json
import logging
import requests
import hurry.filesize
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    ConversationHandler
)
import vps_config as cfg
import plugins.user_service as user_service
import plugins.instance_service as instance_service

user_service = user_service.User()
instance_service = instance_service.Instance()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

GET_BANDWIDTH, CONVERT_DATA, GET_PROFILE_INFO = range(3)
JSON_DATA = None


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> int:
    '''Send a message when the command /start is issued.'''
    reply_keyboard = [
        ['Get bandwidth'],
        ['Get profile info'],
        ['List instances'],
        ['Cancel']]
    update.message.reply_text(
        'Hi! I am admin here. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Wnat do you want for today? ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder=''
        ),
    )
    return GET_BANDWIDTH

def cancel(update: Update, context: CallbackContext) -> int:
    '''Cancels and ends the conversation.'''
    user = update.message.from_user
    logger.info('User %s canceled the conversation.', user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def get_profile_info(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Get bandwidth', 'Cancel']]
    logger.info('Getting user info')
    update.message.reply_text(
        f'{user_service.get_user_email()}\n{user_service.get_user_name()}\n{user_service.get_user_userid()}',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Wanna finish or take another measure ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder=''))
    return GET_BANDWIDTH


def get_vultr_info(update: Update, context: CallbackContext) -> int:
    logger.info('Method get_vultr was executed')
    url = 'https://api.vultr.com/v2/instances/{}/bandwidth'.format(
        cfg.api_keys['INSTANCE_ID'])
    headers = {'Authorization': 'Bearer {}'.format(cfg.api_keys['VULTR_KEY']),
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
    reply_keyboard = [['Get bandwidth', 'Get profile info', 'Cancel']]
    logger.info('Method convert_data was executed')
    data = update.message.text
    for i in JSON_DATA['bandwidth']:
        if data == i:
            incoming_bytes = JSON_DATA['bandwidth'][str(i)]['incoming_bytes']
            outcoming_bytes = JSON_DATA['bandwidth'][str(i)]['outgoing_bytes']
            update.message.reply_text(
                '⬇️ ' + hurry.filesize.size(incoming_bytes, system=hurry.filesize.verbose) + ' \n' +
                '⬆️ ' +
                hurry.filesize.size(
                    outcoming_bytes, system=hurry.filesize.verbose)
            )
    update.message.reply_text(
        'Wanna finish or take another measure ?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                         one_time_keyboard=True,
                                         input_field_placeholder=''))
    return GET_BANDWIDTH

# TODO make list readable and update id with OS names only
def get_instance_list(update: Update, context: CallbackContext):
    reply_keyboard = [[], ['Cancel']]
    for i in instance_service.list_instances():
        reply_keyboard[0].append(i.get('id'))
        print(i.get('id'))
    update.message.reply_text('Select prefferable instance',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True,
                                                               input_field_placeholder=''))
    return GET_BANDWIDTH

# TODO: Make 
def get_instance_properties(update: Update, context: CallbackContext):
    reply_keyboard = [['List instances'], ['Cancel']]
    text = json.dumps(instance_service.get_instance_info(update.message.text))
    update.message.reply_text(text,
                              reply_markup=ReplyKeyboardMarkup(
                                                               reply_keyboard,
                                                               one_time_keyboard=True,
                                                               input_field_placeholder=''))
    return GET_BANDWIDTH


def main() -> None:
    '''Start the bot.'''

    # Create the Updater and pass it your bot's token.
    updater = Updater(cfg.api_keys['TELEGRAM_API_KEY'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            GET_BANDWIDTH: [
                MessageHandler(Filters.regex(
                    '^(Get profile info)$'), get_profile_info),
                MessageHandler(Filters.regex(
                    '^(Get bandwidth)$'), get_vultr_info),
                MessageHandler(Filters.regex(
                    '^(List instances)$'), get_instance_list),
                MessageHandler(Filters.regex('^(Cancel)$'), cancel),
                MessageHandler(Filters.regex('(\w+)'),get_instance_properties)
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
    dispatcher.add_handler(CommandHandler(
        'get_profile_info', get_profile_info))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()