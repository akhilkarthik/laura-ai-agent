import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
from llm.groq_client import chat
from linkedin.poster import post_to_linkedin

_LAST_POST = "last_post"
_HISTORY = "history"
MAX_HISTORY = 30


def _extract_post(text: str):
    match = re.search(r'<linkedin_post>(.*?)</linkedin_post>', text, re.DOTALL)
    if match:
        post = match.group(1).strip()
        surrounding = text.replace(match.group(0), '').strip()
        return post, surrounding
    return None, text


def _post_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("Post to LinkedIn", callback_data="post"),
        InlineKeyboardButton("Regenerate", callback_data="regen"),
        InlineKeyboardButton("Edit", callback_data="edit"),
    ]])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[_HISTORY] = []
    context.user_data.pop(_LAST_POST, None)
    await update.message.reply_text(
        "Hey! I'm Alex, your personal assistant.\n\n"
        "I can help you with:\n"
        "- LinkedIn posts — create, edit, rewrite, post\n"
        "- Edit or rewrite any content\n"
        "- Summarize articles or papers\n"
        "- Answer questions on any topic\n"
        "- Write emails, messages, anything\n\n"
        "Just talk to me naturally.\n\n"
        "/help — commands\n"
        "/clear — reset conversation"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "What I can do:\n\n"
        "LinkedIn:\n"
        "  'Write a LinkedIn post about [topic]'\n"
        "  'Make it shorter / more casual / bolder'\n"
        "  'Rewrite with a storytelling angle'\n\n"
        "Content:\n"
        "  'Edit this: [paste your text]'\n"
        "  'Summarize: [paste article]'\n"
        "  'Rewrite this in a professional tone'\n\n"
        "General:\n"
        "  Ask me anything — I remember our conversation\n\n"
        "/clear — wipe conversation history\n"
        "/start — fresh start"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data[_HISTORY] = []
    context.user_data.pop(_LAST_POST, None)
    await update.message.reply_text("Cleared. Fresh start.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    history = context.user_data.get(_HISTORY, [])

    history.append({"role": "user", "content": user_input})
    await update.message.chat.send_action("typing")

    try:
        response = await chat(history)
        history.append({"role": "assistant", "content": response})

        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]
        context.user_data[_HISTORY] = history

        post, surrounding = _extract_post(response)

        if post:
            context.user_data[_LAST_POST] = post
            if surrounding:
                await update.message.reply_text(surrounding)
            await update.message.reply_text(
                f"{'─' * 30}\n\n{post}\n\n{'─' * 30}",
                reply_markup=_post_keyboard()
            )
        else:
            await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error: {e}")


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "post":
        post = context.user_data.get(_LAST_POST)
        if not post:
            await query.edit_message_text("No post to publish. Ask me to write one first.")
            return
        await query.edit_message_text("Posting to LinkedIn...")
        try:
            post_id = post_to_linkedin(post)
            await query.edit_message_text(f"Posted to LinkedIn!\n\nPost ID: {post_id}")
        except Exception as e:
            await query.edit_message_text(f"Failed: {e}")

    elif query.data == "regen":
        history = context.user_data.get(_HISTORY, [])
        if not history:
            await query.edit_message_text("No context found. Send a new request.")
            return
        await query.edit_message_text("Regenerating...")
        try:
            history.append({"role": "user", "content": "Regenerate the LinkedIn post with a completely different hook and angle."})
            response = await chat(history)
            history.append({"role": "assistant", "content": response})
            context.user_data[_HISTORY] = history[-MAX_HISTORY:]

            post, surrounding = _extract_post(response)
            if post:
                context.user_data[_LAST_POST] = post

            display = post or response
            await query.edit_message_text(
                f"{'─' * 30}\n\n{display}\n\n{'─' * 30}",
                reply_markup=_post_keyboard()
            )
        except Exception as e:
            await query.edit_message_text(f"Error: {e}")

    elif query.data == "edit":
        post = context.user_data.get(_LAST_POST, '')
        await query.edit_message_text(
            f"{'─' * 30}\n\n{post}\n\n{'─' * 30}\n\n"
            "How should I edit it? Examples:\n"
            "- Make it shorter\n"
            "- More casual tone\n"
            "- Add a story angle\n"
            "- Stronger opening hook\n"
            "- Add emojis"
        )


def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback))

    webhook_url = os.getenv("WEBHOOK_URL")
    if webhook_url:
        port = int(os.getenv("PORT", 8000))
        print(f"Starting webhook mode on port {port}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="/webhook",
            webhook_url=f"{webhook_url}/webhook",
        )
    else:
        print("Bot is running in polling mode... Press Ctrl+C to stop.")
        app.run_polling()
