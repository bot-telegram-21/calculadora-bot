#!/usr/bin/env python
# pylint: disable=C0116,W0613

import os
import logging
from typing import Dict

from telegram import Update
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Start the conversation and ask user for input."""
    logger.info("Started bot")
    update.message.reply_text("Olá, eu sou um bot-calculadora!")


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    logger.info("help command")
    update.message.reply_text("Digite a operação que você deseja fazer e eu te direi o resultado. Exemplos:")
    update.message.reply_text("3 + 4")
    update.message.reply_text("5 - 10")
    update.message.reply_text("4 * 5")
    update.message.reply_text("9 / 2")


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


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    token = os.environ.get("TOKEN")
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, process_calculation))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
