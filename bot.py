import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = open('token.txt', 'r')
ADD, SHOW, DELETE = map(chr, range(3))
TYPE, SELECT_SHOW, STOP = map(chr, range(3, 6))
SHOW_ALL, SHOW_DONE, SHOW_TODO, START_OVER, SELECTING_ACTION, CURRENT_FEATURE = map(chr, range(6, 12))
END = ConversationHandler.END


def start(update, context):
    """Send message on `/start`."""
    text = 'You may add/delete a film or show existing ones. To abort, simply type /stop.'
    buttons = [[
        InlineKeyboardButton(text='Add film', callback_data=str(ADD)),
        InlineKeyboardButton(text='Delete film', callback_data=str(DELETE))
    ], [
        InlineKeyboardButton(text='Show films', callback_data=str(SHOW)),
        InlineKeyboardButton(text='Done', callback_data=str(END))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)

    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text('Hi, I\'m S&B bot and here to help manage you film data.')
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def select_show(update, context):
    """Choose category to show."""
    text = 'Chose what to show:'
    buttons = [[
        InlineKeyboardButton(text=u'\U00002705', callback_data=str(SHOW_DONE)),
        InlineKeyboardButton(text=u'\U0000274C', callback_data=str(SHOW_TODO))
    ], [
        InlineKeyboardButton(text='All', callback_data=str(SHOW_ALL)),
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]

    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECT_SHOW


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


def show_content(update, context):
    text = 'Some films:'
    buttons = [[
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SHOW


def end_showing(update, context):
    select_show(update, context)

    return END


def stop(update, context):
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return END


def stop_nested(update, context):
    """Completely end conversation from within nested conversation."""
    update.message.reply_text('Okay, bye.')

    return STOP


def end(update, context):
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = 'See you!'
    update.callback_query.edit_message_text(text=text)

    return END


def main():
    updater = Updater(str(TOKEN.read()), use_context=True)

    dp = updater.dispatcher

    show_titles = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_content, pattern='^' + str(SHOW_ALL) + '$')],

        states={},

        fallbacks=[
            CallbackQueryHandler(end_showing, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # Return to second level menu
            END: SELECT_SHOW,
            # End conversation alltogether
            STOP: STOP,
        }
    )

    add_member_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(select_show, pattern='^' + str(SHOW) + '$')],

        states={
            SELECT_SHOW: [show_titles]
        },

        fallbacks=[
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            # Return to top level menu
            END: SELECTING_ACTION,
            # End conversation alltogether
            STOP: END,
        }
    )

    selection_handlers = [
        add_member_conv,
        CallbackQueryHandler(end, pattern='^' + str(END) + '$')
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SELECTING_ACTION: selection_handlers,
            SELECT_SHOW: selection_handlers,
            STOP: [CommandHandler('start', start)],
        },

        fallbacks=[CommandHandler('stop', stop)],
    )

    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
