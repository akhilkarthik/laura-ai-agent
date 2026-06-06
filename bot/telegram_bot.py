import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from llm.groq_client import generate_linkedin_post
from linkedin.poster import post_to_linkedin

_LAST_POST = "last_post"
_LAST_TOPIC = "last_topic"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "LinkedIn Post Agent ready!\n\n"
        "Send me any topic or rough idea and I'll craft a professional LinkedIn post.\n\n"
        "Example: why RAG is transforming AI research"
    )


def _post_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Post to LinkedIn", callback_data="post"),
        InlineKeyboardButton("Regenerate", callback_data="regen"),
    ]])


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = update.message.text
    context.user_data[_LAST_TOPIC] = topic
    await update.message.reply_text("Generating your LinkedIn post...")

    try:
        post = await generate_linkedin_post(topic)
        context.user_data[_LAST_POST] = post
        await update.message.reply_text(
            f"{'─' * 30}\n\n{post}\n\n{'─' * 30}",
            reply_markup=_post_keyboard()
        )
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "post":
        post = context.user_data.get(_LAST_POST)
        if not post:
            await query.edit_message_text("No post found. Send a topic first.")
            return
        await query.edit_message_text("Posting to LinkedIn...")
        try:
            post_id = post_to_linkedin(post)
            await query.edit_message_text(
                f"Posted to LinkedIn successfully!\n\nPost ID: {post_id}"
            )
        except Exception as e:
            await query.edit_message_text(f"Failed to post: {e}")

    elif query.data == "regen":
        topic = context.user_data.get(_LAST_TOPIC)
        if not topic:
            await query.edit_message_text("No topic found. Send a topic first.")
            return
        await query.edit_message_text(f"Regenerating post for: {topic}...")
        try:
            post = await generate_linkedin_post(topic)
            context.user_data[_LAST_POST] = post
            await query.edit_message_text(
                f"{'─' * 30}\n\n{post}\n\n{'─' * 30}",
                reply_markup=_post_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(f"Error: {e}")


def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()
