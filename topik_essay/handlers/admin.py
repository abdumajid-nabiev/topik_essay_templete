from telegram import Update
from telegram.ext import ContextTypes

# List of your admin user IDs
ADMINS = [691728393]  # <-- replace with your Telegram ID(s)

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("❌ Access denied. You are not an admin.")
        return

    # Example: gather user info from your database (replace with your storage logic)
    users_info = context.bot_data.get("users_info", {})
    essays_info = context.bot_data.get("essays_info", {})

    if not users_info:
        await update.message.reply_text("No users registered yet.")
        return

    text = "🛡 Admin Dashboard\n\n"

    for uid, info in users_info.items():
        name = info.get("name", "N/A")
        username = info.get("username", "N/A")
        essay = essays_info.get(uid, "No essay submitted.")
        text += f"👤 {name} (@{username})\n📝 {essay[:50]}...\n\n"  # show first 50 chars

    await update.message.reply_text(text)
