import asyncio
from dotenv import load_dotenv
load_dotenv()

from bot.telegram_bot import run_bot

if __name__ == "__main__":
    asyncio.set_event_loop(asyncio.new_event_loop())
    run_bot()
