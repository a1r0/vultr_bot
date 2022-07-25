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
import services.user_service as user_service
import services.instance_service as instance_service

user_service = user_service.User()
instance_service = instance_service.Instance(None, None)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# States of conversation while user navigates trough chat
MAIN, CONVERT_DATA, INSTANCES , INSTANCE , USER_MANAGEMENT , USER= range(6)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> int:
    '''Send a message when the command /start is issued.'''
    reply_keyboard = [
        ['User management'],
        ['Instance management'],
        ['Cancel']]
    update.message.reply_text(
        'Hi! I am admin here. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Wnat do you want for today? ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return MAIN


def cancel(update: Update, context: CallbackContext) -> int:
    '''Cancels and ends the conversation.'''
    user = update.message.from_user
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# TODO implement User service
def start_user_menu(update: Update , context: CallbackContext) -> int:
    reply_keyboard = [
        ['List active users'],
        # ['Create user'],
        ['Back to main']]
    update.message.reply_text('Select prefferable menu', reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True))
    return USER_MANAGEMENT

def start_instance_menu(update: Update , context: CallbackContext) -> int:
    reply_keyboard = [
        # ['Create instance'] , 
        ['List instances'] ,
        # ['Remove instance']
        ]
    update.message.reply_text('Select what do you want to do', reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True))
    return INSTANCES

def list_active_users(update: Update , context: CallbackContext) -> int:
    userlist = user_service.get_user_list()
    reply_keyboard = [['User management']]
    for i in userlist:
        reply_keyboard.append([i['name']])
    update.message.reply_text('Select which user to modify', reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True))
    return USER

    
# TODO implement getting user info by inique id
def get_user_menu(update: Update , context: CallbackContext) -> int:
    reply_keyboard = [
        ['Update user'] , 
        ['Delete user'] , 
        ['Get detailed information'], 
        ['User management']]
    update.message.reply_text('Under development 😥', reply_markup=ReplyKeyboardMarkup(reply_keyboard , one_time_keyboard=True))
    return USER


def get_instance_bandwidth_info(update: Update, context: CallbackContext) -> int:
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

    return INSTANCE


def convert_bandwidth_data(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Get bandwidth'],['Back to main']]
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
    return INSTANCE


def list_instances(update: Update, context: CallbackContext):
    reply_keyboard = [[]]
    for i in instance_service.list_instances():
        reply_keyboard[0].append(i.get('label'))
    update.message.reply_text('Select prefferable instance',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True,
                                                               input_field_placeholder=''))
    return INSTANCE


def get_instance_properties(update: Update, context: CallbackContext):
    instance_service.label = update.message.text
    reply_keyboard = [['Get bandwidth'],['Back to main']]
    for i in instance_service.list_instances():
        if instance_service.label == i.get('label'):
            # text = instance_service.get_instance_info(i.get('id'))
            text = "Choose preferrable methods of your instance"
            instance_service.id = i.get('id')
            update.message.reply_text(text,
                                      reply_markup=ReplyKeyboardMarkup(
                                          reply_keyboard,
                                          one_time_keyboard=True,
                                          input_field_placeholder=''))
        else:
            update.message.reply_text('Unexpected error',
                                      reply_markup=ReplyKeyboardMarkup(
                                          reply_keyboard,
                                          one_time_keyboard=True,
                                          input_field_placeholder=''))

    return INSTANCE

def main() -> None:
    '''Start the bot.'''

    # Create the Updater and pass it your bot's token.
    updater = Updater(cfg.api_keys['TELEGRAM_API_KEY'])

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [
                MessageHandler(Filters.regex(r'^(Back to main)$') , start),
                MessageHandler(Filters.regex(
                    r'^(User management)$'), start_user_menu),
                MessageHandler(Filters.regex(
                    r'^(Instance management)$'), start_instance_menu),
                MessageHandler(Filters.regex(r'^(Cancel)$') , cancel),
            ],

            INSTANCES:
            [   
                MessageHandler(Filters.regex(
                    r'^(List instances)$'), list_instances),
                
                MessageHandler(Filters.regex(r'^(Back to main)$') , start),
            ],

            INSTANCE: [
                MessageHandler(Filters.regex(
                    r'^(Get bandwidth)$'), get_instance_bandwidth_info),
                MessageHandler(Filters.regex(r'^(Back to main)$') , start),
                MessageHandler(Filters.regex(
                    r'^\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])$'),
                    convert_bandwidth_data),
                MessageHandler(Filters.regex(r'(\w+)'),get_instance_properties)
            ],
            USER_MANAGEMENT: [
                MessageHandler(Filters.regex(
                    r'^(List active users)$'), list_active_users),
                MessageHandler(Filters.regex(
                    r'^(User management)$'), start_user_menu),
                MessageHandler(Filters.regex(r'^(Back to main)$') , start)
            ],
            USER: [MessageHandler(Filters.regex(r'(\w+)'),get_user_menu)]
        },
        fallbacks=[
            CommandHandler('cancel', cancel)
        ],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
