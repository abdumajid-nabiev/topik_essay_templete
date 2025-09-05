# ADMIN_ID = 691728393
# TOKEN = "7596936019:AAHi-MNYN0ojqRWNJqiGRp6Q5DDai4V_Tqw"  # replace with actual bot token
# bot.py — REPLACE your current bot.py with this exact file

import os
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# handlers (ensure these modules/files exist in your project)
from handlers import essay, grammar
from handlers.panel import control_panel, button_handler   # handler name is button_handler
from handlers.grammar import grammar_callback, grammar_command
import bot_admin

# TOKEN: prefer environment variable; fallback to placeholder (replace before production)
TOKEN = os.getenv("BOT_TOKEN") or "7596936019:AAHi-MNYN0ojqRWNJqiGRp6Q5DDai4V_Tqw"

def main():
    if TOKEN == "7596936019:AAHi-MNYN0ojqRWNJqiGRp6Q5DDai4V_Tqw":
        print("Warning: BOT_TOKEN not set. Set env BOT_TOKEN or replace the placeholder in bot.py")

    app = Application.builder().token(TOKEN).build()

    # --- Load saved admin/user data into app.bot_data (bot_admin expects Application) ---
    bot_admin.load_data(app)

    # --- Conversation handler for essay ---
    conv = ConversationHandler(
        entry_points=[CommandHandler("essay", essay.essay_command)],
        states={
            essay.ESSAY_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, essay.essay_input)
            ]
        },
        fallbacks=[CommandHandler("done", essay.done), CommandHandler("cancel", essay.cancel)],
    )
    app.add_handler(conv)

    # --- Global audit saver: save all incoming text messages (non-commands) ---
    # group=1 to run alongside conversation handlers
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), bot_admin.save_user_info), group=1)

    # --- Grammar command + callback handlers (pattern-specific) ---
    app.add_handler(CommandHandler("grammar", grammar_command))
    app.add_handler(CallbackQueryHandler(grammar_callback, pattern="^grammar\\|"))

    # --- Panel command + panel callback handlers (pattern-specific) ---
    app.add_handler(CommandHandler("panel", control_panel))
    
    # --- Regular commands ---
    app.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("안녕하세요! TOPIK Essay Master 봇입니다.")))
    app.add_handler(CommandHandler("help", lambda u, c: u.message.reply_text("/essay, /graph, /grammar 사용법 안내")))

    # --- Admin handlers from bot_admin.py (admin_dashboard etc.) ---
    for handler in bot_admin.admin_handlers:
        app.add_handler(handler)

    print("🤖 Bot running with polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
