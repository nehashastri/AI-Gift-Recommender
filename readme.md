AI-powered gift discovery platform that understands who you're shopping for.

## Features

- **Smart Recommendations**: Get 3 distinct picks - Best Match, Safe Bet, and Something Unique
- **Dual-Path Intelligence**: Matches explicit preferences AND creative lifestyle-based suggestions
- **Safety First**: AI validates every recommendation against allergies and dislikes
- **Persona Management**: Save recipients and get instant recommendations next time
- **Email Reminders**: Schedule and send reminder emails for upcoming gift occasions

## Tech Stack

- **Environment**: Pixi (reproducible builds)
- **Backend**: Python 3.11, FastAPI
- **AI**: OpenAI API (gpt-4o-mini, text-embedding-3-small)
- **Database**: SQLite
- **Frontend**: Static HTML/CSS/JS

## Project Structure
```
gift-genius/
├── app.py                    # App entrypoint
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI app
├── lib/
│   ├── types.py             # Type definitions
│   ├── edible_api.py        # Edible API client
│   ├── ai_client.py         # OpenAI wrapper
│   ├── recommender.py       # Core recommendation engine
│   ├── scorer.py            # Scoring algorithms
│   ├── reminder_service.py  # Email reminders
│   └── database.py          # Persona management
├── static/                  # Web frontend assets
├── tests/                   # Test suite
├── data/                    # App data and defaults
├── logs/
├── start.ps1                # Local run helper
└── pixi.toml                # Environment definition
```

## Model Selection

- **Embeddings**: text-embedding-3-small ($0.02/1M tokens) - 99% cheaper than text-embedding-3-large, sufficient for semantic matching
- **Chat**: gpt-4o-mini ($0.15/1M input, $0.60/1M output) - 15x cheaper than gpt-4o, adequate for structured tasks
- **Rationale**: POC prioritizes speed and cost; production could A/B test premium models for quality lift
