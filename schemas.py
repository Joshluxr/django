from pydantic import BaseModel, HttpUrl
from typing import Literal, Optional

class ParsedAlert(BaseModel):
    source_message_id: int
    source_channel_id: int
    store_url: Optional[HttpUrl]
    product_title: Optional[str]
    price_text: Optional[str]
    sku_id: Optional[str]
    image_url: Optional[HttpUrl]
    add_to_cart_url: Optional[HttpUrl]
    raw_text: str

class VerificationResult(BaseModel):
    ok: bool
    status: Literal["verified_safe", "suspicious", "rejected"]
    reason: str
    final_url: Optional[HttpUrl]
    in_stock: Optional[bool]
    domain_allowed: bool
    details: dict
