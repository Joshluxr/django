import re
from schemas import ParsedAlert


def parse_message(message):
    """Parse a Discord message to extract product information."""
    text = message.content
    store_url = None
    product_title = None
    price_text = None
    sku_id = None
    image_url = None
    add_to_cart_url = None
    
    # Regex patterns for parsing message content
    patterns = {
        'store_url': r'^Store:\s*(\S+)',
        'price': r'^Price:\s*(.+)',
        'sku': r'^SPU_ID\s*\|\s*SKU_ID:\s*\S+\s*\|\s*(\S+)',
        'add_to_cart_url': r'^ATC Link:\s*(\S+)',
    }
    
    # Parse text content line by line
    lines = text.split('\n')
    for line in lines:
        for key, pat in patterns.items():
            match = re.match(pat, line)
            if match:
                if key == 'store_url':
                    store_url = match.group(1)
                elif key == 'price':
                    # Fix: Keep original price text with currency symbols
                    price_text = match.group(1).strip()
                elif key == 'sku':
                    sku_id = match.group(1)
                elif key == 'add_to_cart_url':
                    add_to_cart_url = match.group(1)
    
    # Parse embed if present
    if message.embeds:
        embed = message.embeds[0]
        
        # Get title from embed
        if embed.title:
            product_title = embed.title
        
        # Append description to raw text for keyword matching
        if embed.description:
            text += '\n' + embed.description
        
        # Parse embed fields
        for field in embed.fields:
            if 'Store' in field.name:
                store_url = field.value
            elif 'Price' in field.name:
                # Fix: Keep original price text with currency symbols
                price_text = field.value.strip()
            elif 'SKU' in field.name:
                sku_id = field.value
            elif 'Add to Cart' in field.name or 'ATC' in field.name:
                add_to_cart_url = field.value
        
        # Get image from embed
        if embed.image:
            image_url = embed.image.url
        elif embed.thumbnail:
            image_url = embed.thumbnail.url
    
    # Create lowercase version for keyword matching
    raw_text = text.lower()
    
    return ParsedAlert(
        source_message_id=message.id,
        source_channel_id=message.channel.id,
        store_url=store_url,
        product_title=product_title,
        price_text=price_text,
        sku_id=sku_id,
        image_url=image_url,
        add_to_cart_url=add_to_cart_url,
        raw_text=raw_text
    )


def is_labubu(parsed: ParsedAlert, keywords: list[str]) -> bool:
    """Check if the parsed alert contains Labubu-related keywords."""
    check_text = (parsed.product_title or '') + ' ' + parsed.raw_text
    check_text = check_text.lower()
    
    for kw in keywords:
        if kw.lower() in check_text:
            return True
    
    return False
