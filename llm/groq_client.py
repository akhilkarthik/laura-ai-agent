import os
from groq import AsyncGroq

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an expert LinkedIn content creator specializing in AI, ML, and data science topics.

Create engaging, professional LinkedIn posts that:
- Start with a powerful hook — the first line must stop the scroll
- Are 150-300 words
- Include a personal insight, lesson, or story angle
- End with a thought-provoking question to drive comments
- Include 3-5 relevant hashtags at the end
- Use short paragraphs and line breaks for readability
- Sound authentic and human, not corporate or generic

Return ONLY the post text. No intros, no explanations, no quotes around the post."""


async def generate_linkedin_post(topic: str) -> str:
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Create a LinkedIn post about: {topic}"}
        ],
        temperature=0.8,
        max_tokens=600
    )
    return response.choices[0].message.content
