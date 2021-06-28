#!/usr/bin/env python
# pylint: disable=C0116,W0613

import os
import logging
from typing import Dict

from telegram import Update
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


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
    update.message.reply_markdown_v2(fr"Olá, {user.mention_markdown_v2()}\!"
        fr" Eu sou um robô calculadora\!")
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    logger.info("help command")
    update.message.reply_text("Digite a operação que você deseja fazer e eu te direi o resultado. Exemplos:")
    update.message.reply_text("3 + 4")
    update.message.reply_text("5 - 10")
    update.message.reply_text("4 * 5")
    update.message.reply_text("9 / 2")
    update.message.reply_text(str(context.user_data))
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def info(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /info is issued."""
    logger.info("Bot information")
    update.message.reply_text(context.user_data)
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def process_calculation(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /process_calculation is issued."""
    message_received = update.message.text

    logger.info(F"process_calculation command. message received: {message_received}")
    try:
        result = eval(message_received)
    except SyntaxError as e:
        logger.warn(F"Exxception (SyntaxError). message received: {message_received}")
        result = F"não entendi a expressão '{message_received}'. Você pode tentar novamente"
    except Exception as e:
        logger.warn(F"Exception (general). message received: {message_received}")
        result = F"não entendi a expressão '{message_received}'. Você pode tentar novamente"

    update.message.reply_text(result)
    context.user_data.update(__set_or_update_amount_of_messages__(context.user_data))


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    persistence = PicklePersistence(filename='.persistent_data')
    token = os.environ.get("TOKEN")
    updater = Updater(token, persistence=persistence)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("info", info))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_calculation))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
