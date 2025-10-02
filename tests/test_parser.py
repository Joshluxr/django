import pytest
import json
import discord
from unittest.mock import MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parser import parse_message, is_labubu


@pytest.fixture
def example_text():
    with open('tests/fixtures/example_text.txt', 'r') as f:
        return f.read()


@pytest.fixture
def example_embed():
    with open('tests/fixtures/example_embed.json', 'r') as f:
        return json.load(f)


def test_parse_text(example_text):
    """Test parsing text-based Discord message."""
    message = MagicMock()
    message.content = example_text
    message.embeds = []
    message.id = 123
    message.channel.id = 456
    
    parsed = parse_message(message)
    
    assert str(parsed.store_url) == 'https://www.popmart.com/us/products/labubu'
    # Updated: price_text now keeps currency symbol
    assert parsed.price_text == '$29.99'
    assert parsed.sku_id == 'sku002'
    assert str(parsed.add_to_cart_url) == 'https://www.popmart.com/atc'


def test_parse_embed(example_embed):
    """Test parsing embed-based Discord message."""
    message = MagicMock()
    message.content = ''
    message.embeds = [discord.Embed.from_dict(example_embed)]
    message.id = 123
    message.channel.id = 456
    
    parsed = parse_message(message)
    
    assert parsed.product_title == 'Labubu Figure'
    assert str(parsed.store_url) == 'https://www.popmart.com/' or str(parsed.store_url) == 'https://www.popmart.com'
    # Updated: price_text now keeps currency symbol
    assert parsed.price_text == '$29.99'
    assert parsed.sku_id == 'sku002'
    assert str(parsed.add_to_cart_url) == 'https://www.popmart.com/atc'
    assert str(parsed.image_url) == 'https://image.url/' or str(parsed.image_url) == 'https://image.url'


def test_parse_mixed_content():
    """Test parsing message with both text and embed."""
    message = MagicMock()
    message.content = 'Check out this restock!\nPrice: €19.99'
    message.id = 789
    message.channel.id = 456
    
    embed_dict = {
        "title": "Labubu Mini Figure",
        "fields": [
            {"name": "Store", "value": "https://www.popmart-uk.com/product"},
            {"name": "SKU", "value": "sku123"}
        ]
    }
    message.embeds = [discord.Embed.from_dict(embed_dict)]
    
    parsed = parse_message(message)
    
    assert parsed.product_title == 'Labubu Mini Figure'
    assert str(parsed.store_url) == 'https://www.popmart-uk.com/product'
    # Embed fields take precedence, but if only in text, keeps format
    assert parsed.sku_id == 'sku123'


def test_is_labubu_positive():
    """Test Labubu keyword detection - positive case."""
    parsed = MagicMock()
    parsed.product_title = 'Labubu Figure'
    parsed.raw_text = 'the monsters collection restock'
    
    keywords = ['labubu', 'the monsters']
    
    assert is_labubu(parsed, keywords) is True


def test_is_labubu_negative():
    """Test Labubu keyword detection - negative case."""
    parsed = MagicMock()
    parsed.product_title = 'Molly Figure'
    parsed.raw_text = 'popmart collection restock'
    
    keywords = ['labubu', 'the monsters']
    
    assert is_labubu(parsed, keywords) is False


def test_is_labubu_case_insensitive():
    """Test that keyword matching is case-insensitive."""
    parsed = MagicMock()
    parsed.product_title = 'LABUBU Figure'
    parsed.raw_text = 'THE MONSTERS collection'
    
    keywords = ['labubu', 'the monsters']
    
    assert is_labubu(parsed, keywords) is True


def test_is_labubu_partial_match():
    """Test that partial keyword matches work."""
    parsed = MagicMock()
    parsed.product_title = 'Labububu Plush'
    parsed.raw_text = ''
    
    keywords = ['labubu']
    
    assert is_labubu(parsed, keywords) is True


def test_parse_message_missing_fields():
    """Test parsing message with missing optional fields."""
    message = MagicMock()
    message.content = 'Simple alert'
    message.embeds = []
    message.id = 999
    message.channel.id = 456
    
    parsed = parse_message(message)
    
    assert parsed.source_message_id == 999
    assert parsed.source_channel_id == 456
    assert parsed.store_url is None
    assert parsed.product_title is None
    assert parsed.price_text is None
    assert parsed.sku_id is None
    assert parsed.image_url is None
    assert parsed.add_to_cart_url is None
    assert parsed.raw_text == 'simple alert'


def test_parse_price_with_various_currencies():
    """Test that various currency formats are preserved."""
    test_cases = [
        ('Price: $29.99', '$29.99'),
        ('Price: €19.99', '€19.99'),
        ('Price: £24.99', '£24.99'),
        ('Price: ¥2999', '¥2999'),
        ('Price: 29.99 USD', '29.99 USD'),
    ]
    
    for price_line, expected in test_cases:
        message = MagicMock()
        message.content = f'Store: https://example.com\n{price_line}'
        message.embeds = []
        message.id = 123
        message.channel.id = 456
        
        parsed = parse_message(message)
        assert parsed.price_text == expected, f"Failed for input: {price_line}"


def test_parse_embed_with_image():
    """Test parsing embed with image field."""
    message = MagicMock()
    message.content = ''
    message.id = 123
    message.channel.id = 456
    
    embed_dict = {
        "title": "Labubu",
        "image": {"url": "https://cdn.example.com/image.jpg"}
    }
    message.embeds = [discord.Embed.from_dict(embed_dict)]
    
    parsed = parse_message(message)
    
    assert str(parsed.image_url) == 'https://cdn.example.com/image.jpg'
    assert parsed.product_title == 'Labubu'


def test_parse_embed_with_thumbnail():
    """Test parsing embed with thumbnail (fallback for image)."""
    message = MagicMock()
    message.content = ''
    message.id = 123
    message.channel.id = 456
    
    embed_dict = {
        "title": "Labubu",
        "thumbnail": {"url": "https://cdn.example.com/thumb.jpg"}
    }
    message.embeds = [discord.Embed.from_dict(embed_dict)]
    
    parsed = parse_message(message)
    
    assert str(parsed.image_url) == 'https://cdn.example.com/thumb.jpg'
