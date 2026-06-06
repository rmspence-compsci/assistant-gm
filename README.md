# Assistant GM

An AI-powered fantasy football advisor that connects to your Sleeper league and answers natural language questions about lineups, trades, waivers, and standings.

## Setup

1. Clone the repo and enter the directory
2. Create and activate the conda environment:
   ```bash
   conda create -n assistant-gm python=3.11 -y
   conda activate assistant-gm
   pip install -r requirements.txt
   ```
3. Copy the env template and add your Anthropic API key:
   ```bash
   cp .env.example .env
   # Edit .env and set ANTHROPIC_API_KEY=your_key_here
   ```

## Running

```bash
streamlit run app.py
```

The app opens at http://localhost:8501.

## Usage

1. Enter your Sleeper username in the sidebar
2. Click **Load Leagues** to see your leagues
3. Select a league from the dropdown
4. Ask questions about your team in the chat

## Data

League data is cached locally in `data/league_cache.db` with a 1-hour TTL. Click **Refresh League Data** in the sidebar to force a refresh. Q&A pairs are logged to `data/finetune/qa_log.jsonl` for future fine-tuning.

## Tech Stack

- **Claude** (claude-sonnet-4-6) via Anthropic SDK — AI reasoning
- **Sleeper API** — public fantasy football data (no API key required)
- **SQLite** — local cache with TTL-based refresh
- **Streamlit** — lightweight web UI
