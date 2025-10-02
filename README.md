# Labubu Monitor & Reposter 🐰

A fully automated Discord bot that monitors source servers for Popmart/Labubu restock alerts, verifies them via proxy and whitelisted domains, and reposts color-coded embeds to a destination server.

## ✨ Features

- 🔍 **Smart Monitoring** - Monitors multiple Discord channels for Labubu restock alerts
- 🔐 **URL Verification** - Validates URLs against whitelisted domains with SSL/TLS checks
- 📦 **Stock Detection** - Automatically detects in-stock vs out-of-stock items
- 🎨 **Color-coded Embeds** - Visual status indicators (green/yellow/red)
- 🚀 **High Performance** - Concurrent URL verification with configurable limits
- 💾 **Smart Caching** - Prevents duplicate alerts with TTL cache
- 🔒 **Security First** - Domain whitelisting, IP address blocking, phishing detection
- 📊 **Comprehensive Logging** - JSON logs for monitoring and debugging

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone -b lou https://github.com/Joshluxr/django.git labubu-bot
cd labubu-bot

# Run the setup script
./setup.sh
```

### Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

3. **Configure Bot Settings**
   ```bash
   cp config.yaml.example config.yaml
   # Edit config.yaml and add your channel IDs
   ```

4. **Validate Configuration**
   ```bash
   python validate_config.py
   ```

5. **Run the Bot**
   ```bash
   python bot.py
   ```

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and configuration guide
- **[Discord Bot Setup](SETUP_GUIDE.md#3-create-discord-bot)** - How to create and configure your Discord bot
- **[Configuration Reference](SETUP_GUIDE.md#7-configure-bot-settings)** - All configuration options explained
- **[Troubleshooting](SETUP_GUIDE.md#troubleshooting)** - Common issues and solutions

## 🐳 Docker Deployment

### Using Docker

```bash
docker build -t labubu-monitor .
docker run -d \
  --name labubu-bot \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v $(pwd)/.env:/app/.env \
  --restart unless-stopped \
  labubu-monitor
```

### Using Docker Compose

```bash
docker-compose up -d
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=. --cov-report=html
```

## 📁 Project Structure

```
.
├── bot.py                   # Main Discord bot application
├── parser.py                # Message parsing and keyword detection
├── verifier.py              # URL verification with safety checks
├── schemas.py               # Pydantic data models
├── config.py                # Configuration management
├── cache.py                 # TTL cache for deduplication
├── setup.sh                 # Automated setup script
├── validate_config.py       # Configuration validation tool
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── config.yaml.example      # Configuration template
├── Dockerfile               # Docker image definition
├── SETUP_GUIDE.md          # Comprehensive setup guide
└── tests/
    ├── test_parser.py       # Parser tests
    ├── test_verifier.py     # Verifier tests
    └── fixtures/            # Test data
```

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
DISCORD_TOKEN=your_bot_token_here
HTTP_PROXY=http://proxy:port  # Optional
```

### Bot Settings (`config.yaml`)

```yaml
source_channels:            # Channels to monitor
  - 123456789012345678
destination_channel_id: 987654321098765432  # Where to post alerts
allowed_domains:            # Whitelisted domains
  - "*.popmart.com"
labubu_keywords:            # Product keywords
  - labubu
concurrency_limit: 5        # Concurrent verifications
verification_timeout_seconds: 8
```

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete configuration reference.

## 🛠️ Utilities

- **`setup.sh`** - Automated setup script with dependency installation
- **`validate_config.py`** - Validates your configuration before running
- **`pytest tests/`** - Run test suite to verify functionality

## 🔒 Security Features

- ✅ Domain whitelisting with wildcard support
- ✅ SSL/TLS certificate validation
- ✅ IP address blocking
- ✅ Redirect verification
- ✅ Phishing detection (suspicious title checks)
- ✅ HTTP status validation

## 📊 How It Works

1. **Monitor** - Bot watches configured source channels for new messages
2. **Parse** - Extracts product information (title, price, URLs, etc.)
3. **Filter** - Checks if message contains Labubu-related keywords
4. **Verify** - Validates URLs against whitelisted domains and checks stock
5. **Post** - Sends color-coded embed to destination channel with verification status

## 🎨 Status Colors

- 🟢 **Green (Verified Safe)** - In stock and verified on allowed domain
- 🟡 **Yellow (Suspicious)** - Uncertain status, requires manual review
- 🔴 **Red (Rejected)** - Out of stock, invalid domain, or failed checks

## 📝 Logging

Logs are written to `labubu_logs.json` in JSON format:

```bash
# View logs in real-time
tail -f labubu_logs.json | python -m json.tool
```

## 🤝 Contributing

Contributions are welcome! Please ensure:
- All tests pass: `pytest tests/`
- Code follows existing style
- Add tests for new features

## 📄 License

This project is provided as-is for monitoring Labubu restocks.

## 🆘 Support

- Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed instructions
- Run `python validate_config.py` to diagnose configuration issues
- Review logs in `labubu_logs.json` for error details

---

Made with 💜 for Labubu collectors
