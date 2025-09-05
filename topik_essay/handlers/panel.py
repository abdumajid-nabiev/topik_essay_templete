# handlers/panel.py
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# Panel buttons must use callback_data starting with "panel|..."
async def control_panel(update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Generate sheet", callback_data="panel|generate_sheet")],
        [InlineKeyboardButton("AI analyze", callback_data="panel|ai_analysis")],
        [InlineKeyboardButton("Clear highlights", callback_data="panel|clear_highlights")],
        [InlineKeyboardButton("Export PDF", callback_data="panel|export_pdf")],
    ]
    await update.message.reply_text("Control panel:", reply_markup=InlineKeyboardMarkup(kb))

async def button_handler(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()                       # MUST await
    data = query.data or ""

    # Only handle panel-prefixed callbacks here
    if not data.startswith("panel|"):
        # not for us — return and let other handlers handle it
        return

    action = data.split("|", 1)[1]  # e.g. "generate_sheet"
    if action == "generate_sheet":
        await query.edit_message_text("✅ Essay sheet generated")
    elif action == "ai_analysis":
        await query.edit_message_text("🤖 AI analysis started")
    elif action == "clear_highlights":
        await query.edit_message_text("🧹 Highlights cleared")
    elif action == "export_pdf":
        await query.edit_message_text("📄 PDF exported")
    else:
        await query.edit_message_text("Unknown panel action")
