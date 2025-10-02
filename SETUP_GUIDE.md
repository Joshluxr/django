# Labubu Monitor Bot - Setup Guide

## Prerequisites

- Python 3.12+ installed
- A Discord bot token
- Discord server with channels to monitor
- (Optional) HTTP proxy for verification requests

## Step-by-Step Configuration

### 1. Clone the Repository

```bash
git clone -b lou https://github.com/Joshluxr/django.git labubu-bot
cd labubu-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name (e.g., "Labubu Monitor")
4. Go to the "Bot" tab
5. Click "Add Bot"
6. Under "Privileged Gateway Intents", enable:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT (optional)
7. Click "Reset Token" and copy your bot token (save it securely!)

### 4. Invite Bot to Your Server

1. Go to OAuth2 → URL Generator
2. Select scopes:
   - ✅ `bot`
3. Select bot permissions:
   - ✅ Read Messages/View Channels
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

### 5. Get Channel IDs

**Enable Developer Mode in Discord:**
1. User Settings → Advanced → Developer Mode (ON)

**Get Channel IDs:**
1. Right-click on the channel you want to monitor → Copy Channel ID
2. Right-click on the destination channel → Copy Channel ID

### 6. Configure Environment Variables

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your Discord token:

```env
DISCORD_TOKEN=your_bot_token_here
HTTP_PROXY=http://your-proxy:port  # Optional, leave empty if not using proxy
```

**Security Note:** Never commit your `.env` file to git!

### 7. Configure Bot Settings

Create `config.yaml` from the example:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` with your settings:

```yaml
# Channels to monitor for alerts
source_channels:
  - 1234567890123456789  # Replace with actual channel IDs
  - 9876543210987654321

# Channel where verified alerts will be posted
destination_channel_id: 1111111111111111111  # Replace with actual channel ID

# Allowed domains for URL verification (wildcards supported)
allowed_domains:
  - "*.popmart.com"
  - "*.popmartglobal.com"
  - "*.popmart-uk.com"
  - "*.popmartinternational.com"
  - "*.popmartstore.com"
  - "*.popmartofficial.com"

# Keywords to detect Labubu products (case-insensitive)
labubu_keywords:
  - labubu
  - labububu
  - the monsters

# Concurrent URL verification limit
concurrency_limit: 5

# Timeout for URL verification (seconds)
verification_timeout_seconds: 8

# User agent for HTTP requests
user_agent: "Mozilla/5.0 (LabubuMonitorBot)"

# Retry configuration
retry:
  attempts: 3
  backoff_seconds: 1.5

# Embed colors (hex format)
embed_colors:
  verified_safe: 0x00FF00    # Green - In stock and verified
  suspicious: 0xFFFF00       # Yellow - Uncertain status
  rejected: 0xFF0000         # Red - Out of stock or invalid
```

### 8. Test Configuration

Run the configuration test:

```bash
python -c "from config import load_config; print('✓ Config loaded successfully'); print(load_config())"
```

### 9. Run the Bot

```bash
python bot.py
```

You should see:
```
✓ Bot ready! Logged in as YourBotName#1234
```

## Configuration Examples

### Example 1: Single Source Channel

```yaml
source_channels:
  - 123456789012345678

destination_channel_id: 987654321098765432
```

### Example 2: Multiple Source Channels

```yaml
source_channels:
  - 123456789012345678  # alerts-channel-1
  - 234567890123456789  # alerts-channel-2
  - 345678901234567890  # restock-alerts

destination_channel_id: 987654321098765432
```

### Example 3: With Proxy

`.env`:
```env
DISCORD_TOKEN=your_token_here
HTTP_PROXY=http://proxy.example.com:8080
```

### Example 4: Custom Keywords

```yaml
labubu_keywords:
  - labubu
  - labububu
  - the monsters
  - labubu plush
  - crybaby labubu
```

## Docker Deployment (Optional)

### Build the Docker Image

```bash
docker build -t labubu-monitor .
```

### Run with Docker

```bash
docker run -d \
  --name labubu-bot \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/.env:/app/.env \
  --restart unless-stopped \
  labubu-monitor
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  labubu-bot:
    build: .
    container_name: labubu-monitor
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./.env:/app/.env
      - ./logs:/app/logs
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

## Troubleshooting

### Bot doesn't respond to messages

**Check:**
- ✅ MESSAGE CONTENT INTENT is enabled in Discord Developer Portal
- ✅ Bot has permission to read messages in source channels
- ✅ Channel IDs are correct (18-19 digit numbers)
- ✅ Bot is actually in the server

### "DISCORD_TOKEN not found" error

**Fix:**
- Make sure `.env` file exists in the same directory as `bot.py`
- Check that `DISCORD_TOKEN=` has no spaces around the `=`
- Verify the token is correct (reset it in Discord Developer Portal if needed)

### URL verification fails

**Check:**
- Network connectivity
- Proxy configuration (if using)
- Domain is in `allowed_domains` list
- URLs are properly formatted

### Bot crashes on startup

**Common issues:**
- Missing dependencies: Run `pip install -r requirements.txt`
- Invalid YAML syntax in `config.yaml`
- Python version < 3.12

### Messages aren't being filtered

**Verify:**
- Keywords in `labubu_keywords` match the content
- Messages contain URLs (bot only processes messages with URLs)
- Check logs in `labubu_logs.json`

## Testing the Bot

### 1. Send a Test Message

In one of your source channels, send:

```
🐰 Labubu Restock Alert!
Store: https://www.popmart.com/us/products/labubu-figure
Price: $29.99
SKU: LAB-001
ATC Link: https://www.popmart.com/cart/add
```

### 2. Check Destination Channel

The bot should post a formatted embed with:
- Product title
- Price and SKU
- Store and ATC links
- Stock status (if detectable)
- Verification status (color-coded)

## Monitoring & Logs

### View Logs

```bash
tail -f labubu_logs.json
```

Or pretty-print:
```bash
tail -f labubu_logs.json | python -m json.tool
```

### Log Levels

- `INFO`: Normal operations
- `WARNING`: Non-critical issues
- `ERROR`: Failures that need attention
- `DEBUG`: Detailed debugging info

## Performance Tuning

### Adjust Concurrency

Higher values = faster processing, more resource usage:
```yaml
concurrency_limit: 10  # Process 10 URLs simultaneously
```

### Adjust Timeout

For slow networks:
```yaml
verification_timeout_seconds: 15  # Wait longer for responses
```

### Cache Duration

Edit `cache.py` to change cache TTL:
```python
cache = TTLCache(maxsize=1000, ttl=7200)  # 2 hours instead of 1
```

## Security Best Practices

1. ✅ Never commit `.env` or `config.yaml` with real credentials
2. ✅ Use environment-specific configs (dev/staging/prod)
3. ✅ Rotate Discord bot token periodically
4. ✅ Restrict bot permissions to minimum required
5. ✅ Use HTTPS proxy if handling sensitive data
6. ✅ Monitor logs for suspicious activity

## Support

For issues or questions:
- Check `labubu_logs.json` for error details
- Run tests: `pytest tests/ -v`
- Review this guide carefully

## Quick Start Checklist

- [ ] Python 3.12+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Discord bot created and invited to server
- [ ] `.env` file created with `DISCORD_TOKEN`
- [ ] `config.yaml` created with correct channel IDs
- [ ] Bot has proper permissions in Discord
- [ ] MESSAGE CONTENT INTENT enabled
- [ ] Test message sent and bot responds

Ready to go! 🚀
