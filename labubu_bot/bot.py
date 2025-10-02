import discord
from discord.ext import commands
import asyncio
from loguru import logger
from parser import parse_message, is_labubu
from verifier import verify_url
from config import load_config
from cache import cache
from urllib.parse import urlparse
import os
import sys


class LabubuBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        try:
            self.cfg = load_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)
        
        self.sem = asyncio.Semaphore(self.cfg['concurrency_limit'])
        logger.add("labubu_logs.json", serialize=True, rotation="1 MB")
        logger.info("Bot initialized successfully")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Monitoring {len(self.cfg["source_channels"])} source channels')
        logger.info(f'Posting to destination channel: {self.cfg["destination_channel_id"]}')
        print(f'✓ Bot ready! Logged in as {self.user}')

    async def on_message(self, message):
        # Ignore bot's own messages
        if message.author == self.user:
            return
        
        try:
            # Check if message is from a monitored channel
            if message.channel.id not in self.cfg['source_channels']:
                return
            
            # Parse the message
            try:
                parsed = parse_message(message)
            except Exception as e:
                logger.error(f"Failed to parse message {message.id}: {e}")
                return
            
            # Check if it's a Labubu product
            if not is_labubu(parsed, self.cfg['labubu_keywords']):
                logger.debug(f"Message {message.id} is not a Labubu alert")
                return
            
            # Get URL to verify (prefer ATC link over store link)
            url_to_verify = parsed.add_to_cart_url or parsed.store_url
            if not url_to_verify:
                logger.debug(f"Message {message.id} has no verifiable URL")
                return
            
            url_str = str(url_to_verify)
            
            # Check cache to avoid duplicate processing
            if url_str in cache:
                logger.debug(f"URL already processed (cached): {url_str}")
                return
            
            logger.info(f"Processing new alert for: {url_str}")
            
            # Verify URL with concurrency control
            async with self.sem:
                start = asyncio.get_event_loop().time()
                
                try:
                    result = await verify_url(
                        url_str,
                        self.cfg['allowed_domains'],
                        self.cfg['proxy'],
                        self.cfg['verification_timeout_seconds'],
                        self.cfg['user_agent'],
                        self.cfg['retry']['attempts'],
                        self.cfg['retry']['backoff_seconds']
                    )
                except Exception as e:
                    logger.error(f"Verification failed for {url_str}: {e}")
                    return
                
                duration = asyncio.get_event_loop().time() - start
                
                # Log verification result
                log_data = {
                    "event": "verification",
                    "url": url_str,
                    "status": result.status,
                    "reason": result.reason,
                    "domain": urlparse(url_str).hostname,
                    "in_stock": result.in_stock,
                    "duration": round(duration, 2),
                    "source_message_id": message.id
                }
                logger.info(log_data)
                
                # Skip rejected URLs
                if result.status == "rejected":
                    logger.info(f"Rejected URL: {url_str} - {result.reason}")
                    cache[url_str] = True  # Cache rejections to avoid re-checking
                    return
                
                # Cache the URL to prevent duplicate processing
                cache[url_str] = True
                
                # Get destination channel
                dest_channel = self.get_channel(self.cfg['destination_channel_id'])
                if not dest_channel:
                    logger.error(f"Destination channel {self.cfg['destination_channel_id']} not found")
                    return
                
                # Build and send embed
                try:
                    embed = discord.Embed(
                        title=parsed.product_title or "🐰 Labubu Restock Alert",
                        description=f"**Price:** {parsed.price_text or 'N/A'}\n**SKU:** {parsed.sku_id or 'N/A'}",
                        color=self.cfg['embed_colors'][result.status]
                    )
                    
                    if parsed.image_url:
                        embed.set_thumbnail(url=str(parsed.image_url))
                    
                    if parsed.store_url:
                        embed.add_field(name="🏪 Store", value=str(parsed.store_url), inline=False)
                    
                    atc = str(parsed.add_to_cart_url) if parsed.add_to_cart_url else "N/A"
                    embed.add_field(name="🛒 Add to Cart", value=atc, inline=False)
                    
                    # Add verification details
                    if result.in_stock is not None:
                        stock_emoji = "✅" if result.in_stock else "❌"
                        stock_text = "In Stock" if result.in_stock else "Out of Stock"
                        embed.add_field(name="📦 Stock Status", value=f"{stock_emoji} {stock_text}", inline=True)
                    
                    status_text = result.status.replace('_', ' ').title()
                    proxy_indicator = "✓" if self.cfg['proxy'] else "✗"
                    footer = f"Status: {status_text} | Proxy: {proxy_indicator} | ⏱️ {duration:.1f}s"
                    embed.set_footer(text=footer)
                    
                    embed.timestamp = message.created_at
                    
                    # Add source link as button-style field
                    embed.add_field(name="📍 Source", value=f"[Jump to original message]({message.jump_url})", inline=False)
                    
                    await dest_channel.send(embed=embed)
                    logger.info(f"✓ Successfully posted alert for {url_str}")
                    
                except discord.HTTPException as e:
                    logger.error(f"Discord API error sending embed: {e}")
                except discord.Forbidden:
                    logger.error(f"Missing permissions to send messages in channel {dest_channel.id}")
                except Exception as e:
                    logger.error(f"Unexpected error sending message: {e}")
                    
        except Exception as e:
            logger.error(f"Error in on_message handler: {e}", exc_info=True)

    async def on_error(self, event, *args, **kwargs):
        logger.error(f"Unhandled error in event {event}", exc_info=True)


if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables")
        sys.exit(1)
    
    bot = LabubuBot()
    
    try:
        bot.run(token)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
