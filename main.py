import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler
from telegram.constants import ParseMode
load_dotenv()
TOKEN = os.getenv("TOKEN")

import commands

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
	query = update.callback_query
	
	await query.answer()

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
	pass

print("Initializing")
app = ApplicationBuilder().token(TOKEN).build()
print("Adding handlers")
for k in commands.COMMAND_LIST:
	app.add_handler(CommandHandler([k]+commands.COMMAND_LIST[k][0], commands.COMMAND_LIST[k][1]))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(None, message_handler))
print("Running")
app.run_polling()
