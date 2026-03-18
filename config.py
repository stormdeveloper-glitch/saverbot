import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
ADMIN_ID = [int(x) for x in os.getenv("ADMIN_ID", "0").split(",")]
# Kanallarni vergul bilan ajratib yozing: "@kanal1,@kanal2"
CHANNELS = [ch.strip() for ch in os.getenv("CHANNELS", "").split(",")]
