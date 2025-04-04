import os
import textwrap
import logging
from logging import Logger
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from script import insert_keyword, fetch_all_keywords, delete_keyword


load_dotenv()

ICEFANTOM_USER_ID = 7616386027
ASHKN_USER_ID = 5459678848

env = os.environ.get("ENV")
if env == "dev":
    TOKEN = os.environ.get("TOKEN_DEV")
else:
    TOKEN = os.environ.get("TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = Logger("tg_bot_logger")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id not in [ICEFANTOM_USER_ID, ASHKN_USER_ID]:
        return

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=textwrap.dedent(
            """
        Welcome to The Markplaats BOT.
        This bot notifies you about new listings on https://markplaats.nl/.
        Usage:
        /start : shows you this message
        /setkeyword <KEYWORD> : add a keyword that you want to search new listings for.
        Example: `/setkeyword car` will notify you show you new listings made with the keyword 'car'
        /listkeywords: will show you all available keywords
        /deletekeyword <KEYWORD>: will delete a keyword and will not notify you about it any longer
        """
        ),
    )


async def set_keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id not in [ICEFANTOM_USER_ID, ASHKN_USER_ID]:
        return

    try:
        keyword = " ".join(context.args)
        print("Recieved new keyword:", keyword)
        res = insert_keyword(keyword)

        if res:
            await update.effective_message.reply_text(
                f"Successfully inserted {keyword} into database"
            )
        else:
            await update.effective_message.reply_text(
                "Something went wrong. Please try again!"
            )

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /setkeyword <keyword>")


async def list_keywords_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id not in [ICEFANTOM_USER_ID, ASHKN_USER_ID]:
        return

    try:
        res = fetch_all_keywords()
        keywords = [row["keyword"] for row in res if res]
        print(f"listing keywords: {keywords}")

        keywords_string = "\n".join(keywords)
        response = f"Keywords:\n {keywords_string}"
        await update.effective_message.reply_text(response)

    except Exception as e:
        print(e)
        await update.effective_message.reply_text("Some error occured")


async def delete_keyword_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id not in [ICEFANTOM_USER_ID, ASHKN_USER_ID]:
        return
    try:
        keyword = ' '.join(context.args)
        print("Recieved keyword:", keyword)
        res = delete_keyword(keyword=keyword)

        if res:
            await update.effective_message.reply_text(
                f"Successfully deleted {keyword} from database"
            )
        else:
            await update.effective_message.reply_text(
                "Something went wrong. Please try again!"
            )

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /deletekeyword <keyword>")


if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler(["start", "help"], start)
    set_keyword_handler = CommandHandler("setkeyword", set_keyword_command)
    list_keywords_handler = CommandHandler("listkeywords", list_keywords_command)
    delete_keyword_handler = CommandHandler("deletekeyword", delete_keyword_command)

    application.add_handler(start_handler)
    application.add_handler(set_keyword_handler)
    application.add_handler(list_keywords_handler)
    application.add_handler(delete_keyword_handler)

    application.run_polling()
