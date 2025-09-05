from telegram import Update
from telegram.ext import ContextTypes
import json

GRAMMAR_FILE = "data/grammar.json"

async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(GRAMMAR_FILE, "r", encoding="utf-8") as f:
        grammar = json.load(f)
    msg = "📚 TOPIK Writing Grammar Patterns:\n"
    for func, patterns in grammar.items():
        msg += f"\n{func}:\n"
        for p in patterns:
            msg += f" - {p}\n"
    await update.message.reply_text(msg)

# handlers/grammar.py
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from core import grammar_db
from typing import Optional

# UI localization (labels only) - grammar forms/examples remain Korean
LABELS = {
    "en": {
        "title": "TOPIK Writing — Grammar Inventory",
        "by_function": "By function",
        "by_level": "By TOPIK level",
        "all": "All patterns",
        "next": "▶ Next",
        "prev": "◀ Prev",
        "back": "◀ Back",
        "page": "Page",
        "no_results": "No matching grammar patterns found.",
        "usage": "Usage:\n/grammar - open menu\n/grammar <keyword> - search pattern or example\n/grammar setlang <en|uz|kr> - set UI language (default en)"
    },
    "uz": {
        "title": "TOPIK Yozuv — Grammatika roʻyxati",
        "by_function": "Funktsiyaga koʻra",
        "by_level": "TOPIK darajasi boʻyicha",
        "all": "Barcha shakllar",
        "next": "▶ Keyingi",
        "prev": "◀ Oldingi",
        "back": "◀ Orqaga",
        "page": "Sahifa",
        "no_results": "Mos grammatik naqsh topilmadi.",
        "usage": "Foydalanish:\n/grammar - menyu\n/grammar <soʻz> - qidiruv\n/grammar setlang <en|uz|kr> - tilni sozlash"
    },
    "kr": {
        "title": "TOPIK 쓰기 — 문법 목록",
        "by_function": "기능별",
        "by_level": "TOPIK 레벨별",
        "all": "전체 문형",
        "next": "▶ 다음",
        "prev": "◀ 이전",
        "back": "◀ 뒤로",
        "page": "페이지",
        "no_results": "일치하는 문형이 없습니다.",
        "usage": "사용법:\n/grammar - 메뉴\n/grammar <키워드> - 검색\n/grammar setlang <en|uz|kr> - UI 언어 설정"
    }
}

PER_PAGE = 5

# ------------------ Helpers ------------------
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    """Determine user's UI language. Default 'en'."""
    lang = context.user_data.get("locale")
    if lang in ("en","uz","kr"):
        return lang
    # fallback: try chat language or bot_data default
    return context.bot_data.get("default_locale","en")

def make_main_keyboard(lang: str):
    L = LABELS[lang]
    kb = [
        [InlineKeyboardButton(L["by_function"], callback_data="grammar|func|1|none")],
        [InlineKeyboardButton(L["by_level"], callback_data="grammar|level|1|none")],
        [InlineKeyboardButton(L["all"], callback_data="grammar|all|1|none")],
    ]
    return InlineKeyboardMarkup(kb)

def render_entry_text(e: dict) -> str:
    # show pattern (Korean), example (Korean), level(s), meaning in EN/UZ
    levels = ",".join(e.get("levels", []))
    en = e.get("meaning_en","")
    uz = e.get("meaning_uz","")
    return f"{e.get('pattern')}\n레벨: {levels}\n예문: {e.get('example_kr','')}\nEN: {en}\nUZ: {uz}"

# ------------------ Command Handler ------------------
async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /grammar [args]
    /grammar setlang en|uz|kr
    /grammar <keyword> -> search
    """
    args = context.args or []
    lang = get_lang(context)

    # set language
    if len(args) >= 2 and args[0].lower() == "setlang":
        desired = args[1].lower()
        if desired in ("en","uz","kr"):
            context.user_data["locale"] = desired
            await update.message.reply_text(f"UI language set to {desired}")
        else:
            await update.message.reply_text("Allowed: en, uz, kr")
        return

    if len(args) >= 1:
        # treat as search keyword
        keyword = " ".join(args)
        entries = grammar_db.filter_entries(keyword=keyword)
        if not entries:
            await update.message.reply_text(LABELS[lang]["no_results"])
            return
        # show first page of search results
        page = 1
        page_entries, total = grammar_db.paginate(entries, page=page, per_page=PER_PAGE)
        text_lines = [f"{LABELS[lang]['title']} — search: {keyword}\n"]
        for e in page_entries:
            text_lines.append(render_entry_text(e))
            text_lines.append("-"*20)
        kb = [
            [InlineKeyboardButton(LABELS[lang]["prev"], callback_data=f"grammar|search|{page-1}|{keyword}", ) if page>1 else InlineKeyboardButton(" ", callback_data="noop") ,
             InlineKeyboardButton(LABELS[lang]["next"], callback_data=f"grammar|search|{page+1}|{keyword}") if total > PER_PAGE else InlineKeyboardButton(" ", callback_data="noop")]
        ]
        await update.message.reply_text("\n".join(text_lines), reply_markup=InlineKeyboardMarkup(kb))
        return

    # no args -> show main menu
    kb = make_main_keyboard(lang)
    await update.message.reply_text(LABELS[lang]["title"] + "\n\n" + LABELS[lang]["usage"], reply_markup=kb)

# ------------------ Callback handler ------------------
async def grammar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data  # format: grammar|action|page|payload
    parts = data.split("|", 3)
    if len(parts) < 4:
        return
    _, action, page_s, payload = parts
    page = max(1, int(page_s or "1"))
    lang = get_lang(context)
    L = LABELS[lang]

    if action == "func":
        # payload 'none' -> show list of functions
        if payload == "none" and page == 1:
            funcs = grammar_db.list_functions()
            kb = []
            for f in funcs:
                kb.append([InlineKeyboardButton(f, callback_data=f"grammar|funclist|1|{f}")])
            kb.append([InlineKeyboardButton(L["back"], callback_data="grammar|back|1|none")])
            await query.edit_message_text("Functions:", reply_markup=InlineKeyboardMarkup(kb))
            return

    if action == "funclist":
        # payload contains function name, show paginated entries
        func = payload
        entries = grammar_db.filter_entries(function=func)
        page_entries, total = grammar_db.paginate(entries, page=page, per_page=PER_PAGE)
        if not page_entries:
            await query.edit_message_text(L["no_results"])
            return
        lines = [f"{func} — {L['page']} {page}\n"]
        for e in page_entries:
            lines.append(render_entry_text(e))
            lines.append("-"*20)
        kb = []
        # prev/next
        prev_btn = InlineKeyboardButton(L["prev"], callback_data=f"grammar|funclist|{page-1}|{func}") if page>1 else InlineKeyboardButton(" ", callback_data="noop")
        next_btn = InlineKeyboardButton(L["next"], callback_data=f"grammar|funclist|{page+1}|{func}") if (page*PER_PAGE) < total else InlineKeyboardButton(" ", callback_data="noop")
        kb.append([prev_btn, next_btn])
        kb.append([InlineKeyboardButton(L["back"], callback_data="grammar|func|1|none")])
        await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))
        return

    if action == "level":
        # show levels list
        levels = grammar_db.list_levels()
        if payload == "none" and page==1:
            kb = []
            for lvl in levels:
                kb.append([InlineKeyboardButton(lvl, callback_data=f"grammar|levellist|1|{lvl}")])
            kb.append([InlineKeyboardButton(L["back"], callback_data="grammar|back|1|none")])
            await query.edit_message_text("TOPIK levels:", reply_markup=InlineKeyboardMarkup(kb))
            return

    if action == "levellist":
        lvl = payload
        entries = grammar_db.filter_entries(level=lvl)
        page_entries, total = grammar_db.paginate(entries, page=page, per_page=PER_PAGE)
        if not page_entries:
            await query.edit_message_text(L["no_results"])
            return
        lines = [f"Level {lvl} — {L['page']} {page}\n"]
        for e in page_entries:
            lines.append(render_entry_text(e))
            lines.append("-"*20)
        prev_btn = InlineKeyboardButton(L["prev"], callback_data=f"grammar|levellist|{page-1}|{lvl}") if page>1 else InlineKeyboardButton(" ", callback_data="noop")
        next_btn = InlineKeyboardButton(L["next"], callback_data=f"grammar|levellist|{page+1}|{lvl}") if (page*PER_PAGE) < total else InlineKeyboardButton(" ", callback_data="noop")
        kb = [[prev_btn, next_btn], [InlineKeyboardButton(L["back"], callback_data="grammar|level|1|none")]]
        await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))
        return

    if action == "all":
        # list everything paginated
        entries = grammar_db.filter_entries()
        page_entries, total = grammar_db.paginate(entries, page=page, per_page=PER_PAGE)
        if not page_entries:
            await query.edit_message_text(L["no_results"])
            return
        lines = [f"{L['all']} — {L['page']} {page}\n"]
        for e in page_entries:
            lines.append(render_entry_text(e))
            lines.append("-"*20)
        prev_btn = InlineKeyboardButton(L["prev"], callback_data=f"grammar|all|{page-1}|none") if page>1 else InlineKeyboardButton(" ", callback_data="noop")
        next_btn = InlineKeyboardButton(L["next"], callback_data=f"grammar|all|{page+1}|none") if (page*PER_PAGE) < total else InlineKeyboardButton(" ", callback_data="noop")
        kb = [[prev_btn, next_btn], [InlineKeyboardButton(L["back"], callback_data="grammar|back|1|none")]]
        await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))
        return

    if action == "search":
        # payload contains the search keyword
        keyword = payload
        entries = grammar_db.filter_entries(keyword=keyword)
        page_entries, total = grammar_db.paginate(entries, page=page, per_page=PER_PAGE)
        if not page_entries:
            await query.edit_message_text(L["no_results"])
            return
        lines = [f"Search: {keyword} — {L['page']} {page}\n"]
        for e in page_entries:
            lines.append(render_entry_text(e))
            lines.append("-"*20)
        prev_btn = InlineKeyboardButton(L["prev"], callback_data=f"grammar|search|{page-1}|{keyword}") if page>1 else InlineKeyboardButton(" ", callback_data="noop")
        next_btn = InlineKeyboardButton(L["next"], callback_data=f"grammar|search|{page+1}|{keyword}") if (page*PER_PAGE) < total else InlineKeyboardButton(" ", callback_data="noop")
        kb = [[prev_btn, next_btn], [InlineKeyboardButton(L["back"], callback_data="grammar|back|1|none")]]
        await query.edit_message_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(kb))
        return

    if action == "back":
        # go to main menu
        kb = make_main_keyboard(lang)
        await query.edit_message_text(L["title"] + "\n\n" + L["usage"], reply_markup=kb)
        return

    # noop or unknown
    await query.answer()
