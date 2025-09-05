import os
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "7596936019:AAHi-MNYN0ojqRWNJqiGRp6Q5DDai4V_Tqw")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
FONT_PATH = "assets/fonts/NotoSansKR-Regular.ttf"
A4_DPI = 300
