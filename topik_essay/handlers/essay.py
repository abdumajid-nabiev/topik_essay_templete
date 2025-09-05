# handlers/essay.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.grid import create_grid_image
from handlers.common import count_squares   # keep this if common exists
import io
import os
import re
import json
import bot_admin

import os
from PIL import ImageFont   # only if using Pillow
import matplotlib.font_manager as fm   # only if using matplotlib

# Always build absolute path to the font file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(BASE_DIR, "..", "utils", "NotoSans.ttf")

# ----------------- CONFIG -----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
USE_DUMMY_AI = os.getenv("USE_DUMMY_AI", "0") == "1"

try:
    if not USE_DUMMY_AI and not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY environment variable not set. export OPENAI_API_KEY='sk-...'")
except RuntimeError as e:
    print(e)

# ----------------- ESSAY STATE -----------------
ESSAY_INPUT = 1
ROWS, COLS = 28, 25

# ----------------- AI ANALYSIS (kept as-is or fallback) -----------------
def ai_analyze_essay(text):
    """
    Returns:
    {
        'score': int 0-50,
        'mistakes': list of substrings,
        'corrected_essay': str,
        'feedback': str
    }
    """
    # Try real AI if configured
    if not USE_DUMMY_AI and OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            prompt = f"""
You are a TOPIK 54 writing examiner. Analyze this Korean essay for grammar, coherence, vocabulary, and logical structure.
Score essay out of 50 points with the following weights:
- Grammar accuracy: 15 points
- Vocabulary / expression: 10 points
- Sentence variety & structure: 15 points
- Coherence & logical flow: 10 points

Return a JSON object ONLY with keys:
{{"score": int, "mistakes": ["substring1","substring2"], "corrected_essay": "full corrected essay", "feedback": "short feedback in Korean"}}

Essay:
{text}
"""
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=1500
            )
            content = response.choices[0].message["content"]
            m = re.search(r"\{.*\}", content, re.DOTALL)
            content_str = m.group() if m else content.strip()
            parsed = json.loads(content_str)
            return {
                "score": int(parsed.get("score", 0)),
                "mistakes": parsed.get("mistakes", []) or [],
                "corrected_essay": parsed.get("corrected_essay", text),
                "feedback": parsed.get("feedback", "") or ""
            }
        except Exception as e:
            print("AI analysis failed:", repr(e))

    # Fallback heuristic
    txt = text.strip()
    length = len(txt)
    length_score = max(0, min(int(length / 700 * 20), 20))
    sentences = [s for s in re.split(r'[.!?]\s*', txt) if s]
    sentence_score = min(15, len(sentences) * 2)
    vocab_score = 10 if len(set(txt.split())) > 100 else 5
    coherence_score = 5 if len(sentences) >= 3 else 2
    total = max(0, min(50, length_score + sentence_score + vocab_score + coherence_score))
    mistakes = []
    if re.search(r'[A-Za-z]', txt):
        mistakes.append("영문자/영단어 사용 감지")
    feedback = f"샘플 분석 (대체): 길이={length}자, 문장수={len(sentences)}, 예상점수={total}/50."
    return {
        "score": total,
        "mistakes": mistakes,
        "corrected_essay": text,
        "feedback": feedback
    }

# ----------------- TEXT NORMALIZATION -----------------
PUNCTUATION_REGEX_BEFORE = re.compile(r'\s+([,\.!?;:，。、…])')
PUNCTUATION_REGEX_AFTER = re.compile(r'([,\.!?;:，。、…])\s+')
MULTI_SPACE_RE = re.compile(r' {2,}')

def normalize_text_for_grid(text: str) -> str:
    if not text:
        return ""
    s = text.strip()
    s = PUNCTUATION_REGEX_BEFORE.sub(r'\1', s)
    s = PUNCTUATION_REGEX_AFTER.sub(r'\1', s)
    s = MULTI_SPACE_RE.sub(' ', s)
    return s

# ----------------- MAP MISTAKES -----------------
def map_mistakes_positions(text: str, mistake_substrings: list, cols: int = COLS, rows: int = ROWS):
    positions = set()
    search_text = text or ""
    for sub in (mistake_substrings or []):
        if not sub:
            continue
        for needle in [sub, sub.strip()]:
            start = 0
            while True:
                idx = search_text.find(needle, start)
                if idx == -1:
                    break
                for pos in range(idx, idx + len(needle)):
                    row = pos // cols
                    col = pos % cols
                    if row < rows:
                        positions.add((row, col))
                start = idx + max(1, len(needle))
    return sorted(positions)

# ----------------- BOT HANDLERS -----------------
async def essay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    # initialize module-level buffer in bot_admin
    bot_admin.user_essays[user_id] = ""
    await update.message.reply_text(
        "📝 54번 에세이 작성 시작\n"
        "600~700자 이내로 작문하십시오.\n"
        "입력 후 `/done` 을 입력하세요."
    )
    return ESSAY_INPUT

async def essay_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    # Auto-save user profile + audit with each message
    await bot_admin.save_user_info(update, context)

    # Append to the per-user in-memory buffer (string)
    bot_admin.user_essays.setdefault(user_id, "")
    bot_admin.user_essays[user_id] += (update.message.text or "")

    # Also keep a session buffer (optional)
    context.user_data.setdefault("essay_buffer", [])
    context.user_data["essay_buffer"].append(update.message.text or "")

    await update.message.reply_text("✍️ 저장했습니다. 계속 입력하거나 `/done` 을 입력하세요.")
    return ESSAY_INPUT

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    essay_text = bot_admin.user_essays.get(user_id, "")
    if not essay_text:
        await update.message.reply_text("❌ 작성된 에세이가 없습니다.")
        return ConversationHandler.END

    # AI analysis
    ai_result = ai_analyze_essay(essay_text)
    score = ai_result.get("score", 0)
    corrected_text = ai_result.get("corrected_essay", essay_text)
    feedback = ai_result.get("feedback", "")

    # Normalize for grid
    corrected_text_normalized = normalize_text_for_grid(corrected_text)

    # Save finalized essay in persistent storage via bot_admin
    bot_admin.save_essay(user_id, corrected_text_normalized, score)

    # Map mistakes -> cell positions
    mistakes_positions = map_mistakes_positions(corrected_text_normalized, ai_result.get("mistakes", []))

    # Generate grid image and send
    img = create_grid_image(corrected_text_normalized, highlight_positions=mistakes_positions)
    bio = io.BytesIO()
    bio.name = "essay.png"
    img.save(bio, "PNG")
    bio.seek(0)

    await update.message.reply_photo(
        photo=bio,
        caption=(
            f"📄 작성 완료!\n"
            f"총 칸: {count_squares(corrected_text_normalized)}\n"
            f"예상 점수: {score}/50\n\n"
            f"💡 Feedback:\n{feedback}"
        )
    )

    # reset the in-memory buffer
    bot_admin.user_essays[user_id] = ""
    context.user_data.pop("essay_buffer", None)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    bot_admin.user_essays[user_id] = ""
    context.user_data.pop("essay_buffer", None)
    await update.message.reply_text("🚫 에세이 작성을 취소했습니다.")
    return ConversationHandler.END
