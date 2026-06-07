# Laura — AI Agent

A conversational AI agent that acts as your personal assistant for LinkedIn content, emails, Notion notes, and analytics. Hosted for free on GitHub Actions — no server or credit card required.

---

## What Laura can do

- **LinkedIn posts** — write, edit, regenerate, post immediately or schedule for a specific time
- **Convert any URL to a post** — paste an article link and Laura turns it into a LinkedIn post
- **Weekly content ideas** — every Monday 9am IST, Laura sends 5 AI/ML post ideas
- **Analytics dashboard** — track post engagement over time, generate a visual chart on demand
- **Email** — draft and send emails via natural language
- **Notion notes** — save ideas, notes, and posts directly to Notion
- **Persistent memory** — remembers every post, email, and note across sessions and agent restarts

---

## Architecture

```
Telegram (user) ──► Agent (python-telegram-bot polling)
                         │
                    Groq LLaMA 3.3 70B  ←── context injection from workspace
                         │
          ┌──────────────┼──────────────────┐
          ▼              ▼                  ▼
    LinkedIn API    Mailjet API        Notion API
    (ugcPosts)      (email send)       (pages)
          │
    GitHub API (free database)
    ├── data/workspace_{user_id}.json   ← persistent history + saved items
    └── data/scheduled_posts.json       ← scheduled post queue
```

**Hosting:** GitHub Actions public repo — 6-hour polling cycles with cron auto-restart. Zero cost, no credit card needed.

---

## Setup

### 1. Fork or clone this repo

```bash
git clone https://github.com/your-username/laura-ai-agent
cd laura-ai-agent
```

### 2. Get your API keys

| Secret | Where to get it |
|--------|----------------|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) → `/newbot` |
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `LINKEDIN_ACCESS_TOKEN` | Run `python linkedin/setup.py` — opens OAuth flow |
| `LINKEDIN_PERSON_URN` | Printed by the setup script (format: `urn:li:person:xxxxx`) |
| `LINKEDIN_CLIENT_ID` | [LinkedIn Developer Apps](https://www.linkedin.com/developers/apps) |
| `LINKEDIN_CLIENT_SECRET` | Same app page |
| `MAILJET_API_KEY` | [app.mailjet.com](https://app.mailjet.com) — free tier |
| `MAILJET_SECRET_KEY` | Same dashboard |
| `NOTION_API_KEY` | [notion.so/my-integrations](https://notion.so/my-integrations) → create integration |
| `NOTION_PAGE_ID` | ID from the URL of your Notion parent page |
| `TELEGRAM_CHAT_ID` | Send `/myid` to your agent after it starts |

### 3. Add secrets to GitHub

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret** — add each key above.

### 4. Enable GitHub Actions

The workflows are already configured in `.github/workflows/`. Push to `master` and then manually trigger **Run Telegram Bot** from the Actions tab.

---

## Usage

Talk to Laura naturally — no commands needed for most things.

```
You:   Write a LinkedIn post about how RAG is being misused in production
Laura: [generates post with hook, body, CTA]
       [Post Now] [Schedule] [Regenerate] [Edit] [Save to Notion]

You:   Make it more conversational
Laura: [rewrites post]

You:   Schedule it for tonight 10pm
Laura: Scheduled for 07 Jun 2026 at 10:00 PM IST. I'll post it and notify you.

You:   https://arxiv.org/abs/2405.xxxxx  turn this into a post
Laura: [fetches article, generates LinkedIn post]
```

### Analytics tracking

LinkedIn's API doesn't expose engagement data for personal profiles. Laura tracks it from what you tell her:

```
You:   that post got 52 reactions 11 comments 340 views
Laura: Tracked. Say 'show me analytics' anytime.

You:   show me my analytics
Laura: [sends a chart image + written analysis]
```

### Commands

| Command | What it does |
|---------|-------------|
| `/analytics` | Visual engagement dashboard for all tracked posts |
| `/memory` | List all saved posts, emails, and notes |
| `/scheduled` | Pending scheduled posts |
| `/clear` | Reset conversation (keeps saved items) |
| `/myid` | Get your Telegram chat ID |
| `/help` | Full command reference |

---

## Project structure

```
bot/
  telegram_bot.py       main bot logic, message + callback handlers
llm/
  groq_client.py        Groq LLaMA wrapper, Laura's system prompt
linkedin/
  poster.py             post to LinkedIn via ugcPosts API
  setup.py              OAuth flow to get access token
db/
  workspace.py          per-user persistent storage via GitHub API
  schedule_store.py     scheduled post queue via GitHub API
scheduler/
  run.py                checks and fires due scheduled posts (every 5 min)
  weekly_ideas.py       Monday 9am IST content ideas
utils/
  url_fetcher.py        extract article text from URLs (trafilatura)
  gmail_sender.py       send email via Mailjet REST API
  notion_client.py      create Notion pages
  chart_generator.py    matplotlib analytics chart generator
.github/workflows/
  run-bot.yml           6-hour polling bot (auto-restarts via cron)
  scheduler.yml         every-5-min scheduled post checker
  weekly-ideas.yml      Monday 9am IST weekly ideas sender
```

---

## Tech stack

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21.6
- [Groq](https://groq.com) — LLaMA 3.3 70B inference
- [LinkedIn ugcPosts API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)
- [Mailjet](https://www.mailjet.com) — transactional email
- [Notion API](https://developers.notion.com)
- [trafilatura](https://trafilatura.readthedocs.io) — web article extraction
- [matplotlib](https://matplotlib.org) — analytics charts
- GitHub Actions + GitHub Contents API — free hosting and database

---

## License

MIT
