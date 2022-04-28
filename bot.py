#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.
""" It is a main module which is start telegram.bot"""

import logging
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
instance_service = instance_service.Instance(None, None)

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
        ['Create instance'],
        ['List instances'],
        ['Remove instance'],
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
    update.message.reply_text(
        f'{user_service.get_user_email()}',
        reply_markup=ReplyKeyboardRemove())
    update.message.reply_text(
        'Wanna finish or take another measure ?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder=''))
    return GET_BANDWIDTH


def get_vultr_info(update: Update, context: CallbackContext) -> int:
    bandwidth = instance_service.get_instance_bandwidth(instance_service.id)[
        'bandwidth']
    reply_keyboard = []
    for date in bandwidth.keys():
        reply_keyboard.append([date])
    update.message.reply_text(
        'Select the date of bandwidth usage',
        reply_markup=ReplyKeyboardMarkup(
                                        reply_keyboard,
                                        one_time_keyboard=True,
                                        input_field_placeholder='Select date of usage:')
    )

    return CONVERT_DATA


def convert_data(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Cancel']]
    date = update.message.text
    bandwidth = instance_service.get_instance_bandwidth(instance_service.id)[
        'bandwidth']
    for i in bandwidth.keys():
        if date == i:
            incoming_bytes = bandwidth[str(i)]['incoming_bytes']
            outcoming_bytes = bandwidth[str(i)]['outgoing_bytes']
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

def get_instance_list(update: Update, context: CallbackContext):
    reply_keyboard = [[], ['Cancel']]
    for i in instance_service.list_instances():
        reply_keyboard[0].append(i.get('label'))
    update.message.reply_text('Select prefferable instance',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True,
                                                               input_field_placeholder=''))
    return GET_BANDWIDTH


def get_instance_properties(update: Update, context: CallbackContext):
    instance_service.label = update.message.text
    for i in instance_service.list_instances():
        if instance_service.label == i.get('label'):
            text = instance_service.get_instance_info(i.get('id'))
            instance_service.id = i.get('id')
    reply_keyboard = [['Get bandwidth'], ['Cancel']]
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
                    r'^(Get profile info)$'), get_profile_info),
                MessageHandler(Filters.regex(
                    r'^(Get bandwidth)$'), get_vultr_info),
                MessageHandler(Filters.regex(
                    r'^(List instances)$'), get_instance_list),
                MessageHandler(Filters.regex(r'^(Cancel)$'), cancel),
                MessageHandler(Filters.regex(r'(\w+)'), get_instance_properties)
            ],

            CONVERT_DATA: [MessageHandler(Filters.regex(
                r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'
            ), convert_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

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
