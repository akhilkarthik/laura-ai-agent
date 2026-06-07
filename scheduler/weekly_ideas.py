import os
import sys
import json
import asyncio
import urllib.request
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dotenv import load_dotenv
load_dotenv()

from groq import AsyncGroq

IST = timezone(timedelta(hours=5, minutes=30))


async def generate_ideas() -> str:
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    now = datetime.now(IST).strftime("%Y-%m-%d (%A)")

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""You are a LinkedIn content strategist for an AI/ML researcher and data scientist.
Today is {now}.

Generate exactly 5 specific, high-value LinkedIn post ideas for this week.
Each idea must have a sharp, non-generic angle — something a practitioner would actually find useful.
Topics: AI agents, LLMs, RAG, MLOps, data science, research papers, career insights, tools.

Format (plain text, no markdown symbols):
1. [Title] — [One sentence on the angle/hook]
2. ...
(5 total, nothing else)"""
            },
            {"role": "user", "content": "Give me this week's post ideas."}
        ],
        temperature=0.9,
        max_tokens=400
    )
    return response.choices[0].message.content.strip()


def send_telegram(chat_id: str, text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req):
        pass


async def main():
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not chat_id:
        print("TELEGRAM_CHAT_ID not set — skipping.")
        return

    print("Generating weekly ideas...")
    ideas = await generate_ideas()

    message = (
        "Good morning! Here are 5 LinkedIn post ideas for this week:\n\n"
        f"{ideas}\n\n"
        "Reply with a number to write any of these, or just paste a URL or topic."
    )
    send_telegram(chat_id, message)
    print("Sent.")


if __name__ == "__main__":
    asyncio.run(main())
