# Labubu Monitor & Reposter

A fully automated Discord bot that monitors source servers for Popmart/Labubu restock alerts, verifies them via proxy and whitelisted domains, and reposts color-coded embeds to a destination server.

## Setup

1. Copy `config.yaml.example` to `config.yaml` and configure channels, domains, etc.
2. Copy `.env.example` to `.env` and add your Discord token and optional proxy.
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python bot.py`

## Docker

Build: `docker build -t labubu-monitor .`
Run: `docker run -v $(pwd)/config.yaml:/app/config.yaml -v $(pwd)/.env:/app/.env labubu-monitor`

## Tests

Run: `pytest`
