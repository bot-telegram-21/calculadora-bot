#!/usr/bin/env python
# pylint: disable=C0116,W0613

import os
import logging
import html
import json
import traceback

from telegram import Update, ParseMode
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    Filters,
    PicklePersistence,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Rotate logger file daily
logger = logging.getLogger(__name__)
logger_handler = logging.handlers.TimedRotatingFileHandler(".persistent_data/logs.txt", 'midnight', 1)
logger.addHandler(logger_handler)

# Get developer chat ID to report calculations that didn't work
DEVELOPER_CHAT_ID = os.environ.get("DEVELOPER_CHAT_ID")


def error_handler(update: object, context: CallbackContext) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def __set_or_update_amount_of_messages__(user_data: dict) -> dict:
    if "amount_of_messages" in user_data.keys():
        user_data["amount_of_messages"] += 1
    else:
        user_data["amount_of_messages"] = 0
    return user_data


def start(update: Update, context: CallbackContext) -> None:
    """Start the conversation and ask user for input."""
    logger.info("Started bot")
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr"Olá, {user.mention_markdown_v2()}\!"
        fr" Eu sou um robô calculadora\!"
    )
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    logger.info("help command")
    update.message.reply_text("Digite a operação que você deseja fazer e eu te direi o resultado. Exemplos:")
    update.message.reply_text("3 + 4")
    update.message.reply_text("5 - 10")
    update.message.reply_text("4 * 5")
    update.message.reply_text("9 / 2")
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def info(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /info is issued."""
    logger.info("Bot information")
    update.message.reply_text(context.user_data)
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def pre_process_calculation(message_received: str) -> str:
    """Remove common mistakes on typing expressions"""
    new_message = message_received.replace(",", ".")
    new_message = new_message.replace("x", "*")

    new_message = new_message.replace("de", "")
    new_message = new_message.replace("por", "")

    new_message = new_message.replace("mais", "+")
    new_message = new_message.replace("com", "+")
    new_message = new_message.replace("e", "+")

    new_message = new_message.replace("menos", "-")

    new_message = new_message.replace("vezes", "*")
    new_message = new_message.replace("multiplicado", "*")

    new_message = new_message.replace("sobre", "/")
    new_message = new_message.replace("dividido", "/")
    return new_message


def process_calculation(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /process_calculation is issued."""
    shall_raise_error = False
    if update.message is None:
        return

    message_received = update.message.text
    expression = pre_process_calculation(message_received)

    logger.info(F"process_calculation command. message received: {expression}")
    try:
        result = eval(expression)
        logger.info(F"command result: {result}")
    except SyntaxError as e:
        logger.warning(F"Exception (SyntaxError). message received: {expression}")
        result = F"não entendi a expressão '{expression}'. Você pode tentar novamente ou digitar \\ajuda"
        shall_raise_error = True
    except Exception as e:
        logger.warning(F"Exception (general). message received: {expression}")
        result = F"não entendi a expressão '{expression}'. Você pode tentar novamente ou digitar \\ajuda"
        shall_raise_error = True

    update.message.reply_text(result)
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))
    if shall_raise_error:
        raise Exception(F"Error with message: '{message_received}'\n\n translated to '{expression}'")


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='.persistent_data/user_data')
    token = os.environ.get("TOKEN")
    updater = Updater(token, persistence=persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("ajuda", help_command))
    dispatcher.add_handler(CommandHandler("info", info))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_calculation))

    dispatcher.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
