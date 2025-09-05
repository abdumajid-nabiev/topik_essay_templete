# import json
# from datetime import datetime
# from telegram import Update
# from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes


# ADMINS = [691728393]
# user_essays = {}
# USERS_FILE = "users_info.json"
# ESSAYS_FILE = "essays_info.json"

# def save_essay(user_id, text):
#     essays_info = app.bot_data.setdefault("essays_info", {})
#     essays_info.setdefault(str(user_id), [])
#     essays_info[str(user_id)].append(text)
#     save_data(app.bot_data)  # persist to JSON

# def load_data(app):
#     try:
#         with open(USERS_FILE, "r", encoding="utf-8") as f:
#             app.bot_data["users_info"] = json.load(f)
#     except:
#         app.bot_data["users_info"] = {}

#     try:
#         with open(ESSAYS_FILE, "r", encoding="utf-8") as f:
#             app.bot_data["essays_info"] = json.load(f)
#     except:
#         app.bot_data["essays_info"] = {}

# # Save data
# def save_data(context):
#     with open(USERS_FILE, "w", encoding="utf-8") as f:
#         json.dump(context.bot_data.get("users_info", {}), f, ensure_ascii=False, indent=2)
#     with open(ESSAYS_FILE, "w", encoding="utf-8") as f:
#         json.dump(context.bot_data.get("essays_info", {}), f, ensure_ascii=False, indent=2)

# # Save user essay with timestamp
# async def save_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user = update.effective_user
#     user_id = str(user.id)

#     # Profile
#     context.bot_data.setdefault("users_info", {})
#     context.bot_data["users_info"][user_id] = {
#         "first_name": user.first_name,
#         "last_name": user.last_name,
#         "username": user.username
#     }

#     # Essays
#     context.bot_data.setdefault("essays_info", {})
#     context.bot_data["essays_info"].setdefault(user_id, [])
#     context.bot_data["essays_info"][user_id].append({
#         "text": update.message.text,
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     })

#     save_data(context)

# # Admin dashboard — neat version
# async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     if update.effective_user.id not in ADMINS:
#         await update.message.reply_text("❌ You are not authorized to use this command.")
#         return

#     users_info = context.bot_data.get("users_info", {})
#     essays_info = context.bot_data.get("essays_info", {})

#     if not users_info:
#         await update.message.reply_text("No users have interacted yet.")
#         return

#     reply_text = "🛡️ **Admin Dashboard** 🛡️\n\n"
#     for user_id, info in users_info.items():
#         reply_text += f"👤 {info.get('first_name','')} {info.get('last_name','')} (@{info.get('username','')}) — ID: {user_id}\n"
#         user_essays = essays_info.get(user_id, [])
#         if not user_essays:
#             reply_text += "   ✏️ No essays submitted yet.\n"
#         for idx, essay in enumerate(user_essays, 1):
#             text_preview = essay["text"] if len(essay["text"]) < 50 else essay["text"][:50] + "..."
#             reply_text += f"   ✏️ Essay {idx} [{essay['timestamp']}]: {text_preview}\n"
#         reply_text += "\n"

#     # Split long messages into chunks of 4000 chars
#     for i in range(0, len(reply_text), 4000):
#         await update.message.reply_text(reply_text[i:i+4000], parse_mode="Markdown")

# # Handlers to import in bot.py
# admin_handlers = [
#     CommandHandler("admin_dashboard", admin_dashboard),
#     MessageHandler(filters.TEXT & (~filters.COMMAND), save_user_info)
# ]

# bot_admin.py
import json
from datetime import datetime
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

# --- ADMIN + runtime state ---
ADMINS = [691728393]

# In-memory buffer for ongoing essays (used by handlers/essay.py)
user_essays = {}

# persistent storage file names
USERS_FILE = "users_info.json"
ESSAYS_FILE = "essays_info.json"

# reference to the Application (set in load_data)
APP = None


# ------- persistence helpers -------
def load_data(app):
    """
    Initialize app.bot_data from JSON files and store app reference.
    Call this once from bot.py with the Application instance.
    """
    global APP
    APP = app

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            app.bot_data["users_info"] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.bot_data["users_info"] = {}

    try:
        with open(ESSAYS_FILE, "r", encoding="utf-8") as f:
            app.bot_data["essays_info"] = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        app.bot_data["essays_info"] = {}


def save_data():
    """
    Persist current bot_data -> files. Uses the stored APP reference.
    """
    global APP
    if APP is None:
        # nothing to save if app not initialized
        return
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(APP.bot_data.get("users_info", {}), f, ensure_ascii=False, indent=2)
        with open(ESSAYS_FILE, "w", encoding="utf-8") as f:
            json.dump(APP.bot_data.get("essays_info", {}), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Failed to save data:", e)


def save_essay(user_id, text, score=None):
    """
    Save essay into app.bot_data['essays_info'] with optional score/timestamp.
    This is for finalized essays (/done).
    """
    global APP
    if APP is None:
        # fallback: keep in module-level dict (won't persist)
        return

    essays_info = APP.bot_data.setdefault("essays_info", {})
    entry = {"text": text, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    if score is not None:
        entry["score"] = score
    essays_info.setdefault(str(user_id), []).append(entry)
    save_data()


# ------- handlers for saving simple interactions -------
async def save_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Save basic user profile and store incoming text messages into
    bot_data['essays_info'] as incremental records (useful audit log).
    This handler is safe to attach as a global MessageHandler.
    """
    if not update.message or not update.effective_user:
        return

    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text or ""

    # Save profile
    context.bot_data.setdefault("users_info", {})
    context.bot_data["users_info"][user_id] = {
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or ""
    }

    # Append the message (audit log)
    context.bot_data.setdefault("essays_info", {})
    context.bot_data["essays_info"].setdefault(user_id, [])
    context.bot_data["essays_info"][user_id].append({
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "auto_saved": True
    })

    # Persist
    save_data()


# ------- admin dashboard -------
async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin-only dashboard. Shows user profile + ALL saved essays (with timestamps).
    Uses plain text (no markdown) to avoid Telegram parse errors.
    """
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return

    users_info = context.bot_data.get("users_info", {})
    essays_info = context.bot_data.get("essays_info", {})

    if not users_info:
        await update.message.reply_text("No users have interacted yet.")
        return

    def safe_preview(s: str, n=200):
        return (s[:n] + "...") if s and len(s) > n else (s or "")

    reply_lines = []
    reply_lines.append("🛡️ Admin Dashboard\n")
    for user_id, info in users_info.items():
        name = f"{info.get('first_name','')} {info.get('last_name','')}".strip()
        uname = info.get("username", "")
        reply_lines.append(f"👤 {name} (@{uname}) — ID: {user_id}")
        user_entries = essays_info.get(user_id, [])
        if not user_entries:
            reply_lines.append("   ✏️ No essays or messages saved.")
        else:
            for idx, e in enumerate(user_entries, 1):
                ts = e.get("timestamp", "N/A")
                score = e.get("score")
                score_str = f" | score: {score}" if score is not None else ""
                preview = safe_preview(e.get("text",""), 300)
                reply_lines.append(f"   ✏️ [{idx}] {ts}{score_str} — {preview}")
        reply_lines.append("")  # blank line separator

    # send in chunks
    reply_text = "\n".join(reply_lines)
    for i in range(0, len(reply_text), 4000):
        await update.message.reply_text(reply_text[i:i+4000])

# Handlers to register from bot.py
admin_handlers = [
    CommandHandler("admin_dashboard", admin_dashboard),
    MessageHandler(filters.TEXT & (~filters.COMMAND), save_user_info),
]
