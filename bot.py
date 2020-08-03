import json
import os
import logging

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

filename = 'my_films.json'

TOKEN = open('token.txt', 'r')
ADD, SHOW, DELETE = map(chr, range(3))
TYPE, SELECT_SHOW, STOP = map(chr, range(3, 6))
SHOW_ALL, SHOW_DONE, SHOW_TODO, START_OVER, SELECTING_ACTION, CURRENT_FEATURE, CURRENT_LEVEL = map(chr, range(6, 13))
FILM_INPUT = map(chr, range(13, 14))
END = ConversationHandler.END


def write_json(data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


if not os.path.exists('./my_films.json'):
    empty_j = {'films': []}
    write_json(empty_j)


def reader():
    with open(filename, 'r') as uptodatefilms:
        return json.load(uptodatefilms)


def _film_switcher(level):
    if level == SHOW_ALL:
        return 'all'
    elif level == SHOW_DONE:
        return 'done'
    elif level == SHOW_TODO:
        return 'todo'


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


def ask_add_film(update, context):
    text = 'Please enter film\'s title:'

    # buttons = [[
    #     InlineKeyboardButton(text='Back', callback_data=str(END))
    # ]]

    # keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPE


def add_film(title):
    outfilms = reader()
    film = {'films': []}
    film['films'].append({
        'name': title,
        'status': 'todo'
    })

    temp = outfilms['films']
    for p in film['films']:
        temp.append(p)
    write_json(outfilms)


def save_input(update, context):

    add_film(update.message.text)
    context.user_data[START_OVER] = True

    return start(update, context)


def select_show(update, context):
    """Choose category to show."""
    text = 'Choose category:'
    buttons = [
        InlineKeyboardButton(text='All', callback_data=str(SHOW_ALL)),
        InlineKeyboardButton(text='Watched' + u' (\U00002705)', callback_data=str(SHOW_DONE)),
        InlineKeyboardButton(text='To Watch' + u' (\U0000274C)', callback_data=str(SHOW_TODO)),
        InlineKeyboardButton(text='Back', callback_data=str(END))
    ]

    keyboard = InlineKeyboardMarkup(build_menu(buttons, n_cols=1))

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return SELECT_SHOW


def end_second_level(update, context):
    """Return to top level conversation."""
    context.user_data[START_OVER] = True
    start(update, context)

    return END


def show_content(update, context):
    level = update.callback_query.data
    context.user_data[CURRENT_LEVEL] = level

    button_list = []
    status_button = str()
    outfilms = reader()
    text = None

    for i in outfilms['films']:
        if str(i['status']) == 'done':
            status_button = u'\U00002705'
            text = 'Watched:'
        elif str(i['status']) == 'todo':
            status_button = u'\U0000274C'
            text = 'To Watch:'
        if _film_switcher(level) == str(i['status']):
            button_list.append(InlineKeyboardButton(text=str(i['name']), callback_data=str(i['name'])))
            button_list.append(InlineKeyboardButton(text=str(status_button), callback_data=str(i['status'])))

        elif _film_switcher(level) == 'all':
            text = 'All:'
            button_list.append(InlineKeyboardButton(text=str(i['name']), callback_data=str(i['name'])))
            button_list.append(InlineKeyboardButton(text=str(status_button), callback_data=str(i['status'])))

    footer = [InlineKeyboardButton(text='Back', callback_data=str(END))]
    keyboard = InlineKeyboardMarkup(build_menu(button_list, n_cols=2, footer_buttons=footer))

    if len(button_list) == 0:
        text = 'It\'s empty here!'

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[START_OVER] = True

    return SHOW


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


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
        entry_points={CallbackQueryHandler(show_content,
                                           pattern='^' + str(SHOW_DONE) + '$|^' + str(SHOW_TODO) + '$|^' + str(
                                               SHOW_ALL) + '$')},

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

    films_show_menu = ConversationHandler(
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

    add_menu = ConversationHandler(
        entry_points=[CallbackQueryHandler(ask_add_film, pattern='^' + str(ADD) + '$')],

        states={
            TYPE: [MessageHandler(Filters.text & ~Filters.command, save_input)],
        },

        fallbacks=[
            CallbackQueryHandler(end_second_level, pattern='^' + str(END) + '$'),
            CommandHandler('stop', stop_nested)
        ],

        map_to_parent={
            END: SELECTING_ACTION,
            STOP: END,
        }
    )

    selection_handlers = [
        films_show_menu,
        add_menu,
        CallbackQueryHandler(end, pattern='^' + str(END) + '$')
    ]

    main_menu = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ADD: [CallbackQueryHandler(start, pattern='^' + str(END) + '$')],
            SELECTING_ACTION: selection_handlers,
            SELECT_SHOW: selection_handlers,
            STOP: [CommandHandler('start', start)],
        },

        fallbacks=[CommandHandler('stop', stop)],
    )

    dp.add_handler(main_menu)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
