import aiohttp
import asyncio
import fnmatch
from urllib.parse import urlparse
import ipaddress
from bs4 import BeautifulSoup
from schemas import VerificationResult
from typing import Optional
from aiohttp import ClientSSLError, ClientTimeout
from loguru import logger


async def verify_url(url: str, allowed_domains: list[str], proxy: Optional[str], timeout: int, user_agent: str, retries: int, backoff: float) -> VerificationResult:
    domain = urlparse(url).hostname
    if not domain:
        return VerificationResult(ok=False, status="rejected", reason="Invalid URL", final_url=None, in_stock=None, domain_allowed=False, details={})
    
    domain_allowed = any(fnmatch.fnmatch(domain, pattern) for pattern in allowed_domains)
    if not domain_allowed:
        return VerificationResult(ok=False, status="rejected", reason="Domain not allowed", final_url=None, in_stock=None, domain_allowed=False, details={})
    
    headers = {'User-Agent': user_agent}
    
    # Fix: Properly configure connector with SSL for both proxy and non-proxy cases
    if proxy:
        connector = aiohttp.TCPConnector(ssl=True)
        session_kwargs = {
            'connector': connector,
            'timeout': aiohttp.ClientTimeout(total=timeout),
            'trust_env': True  # Use proxy from environment if set
        }
    else:
        connector = aiohttp.TCPConnector(ssl=True)
        session_kwargs = {
            'connector': connector,
            'timeout': aiohttp.ClientTimeout(total=timeout)
        }
    
    async with aiohttp.ClientSession(**session_kwargs) as session:
        for attempt in range(retries):
            try:
                # Use proxy parameter in get() call if provided
                get_kwargs = {'headers': headers, 'allow_redirects': True}
                if proxy:
                    get_kwargs['proxy'] = proxy
                
                async with session.get(url, **get_kwargs) as resp:
                    final_url = str(resp.url)
                    final_domain = urlparse(final_url).hostname
                    
                    if not final_domain:
                        return VerificationResult(ok=False, status="rejected", reason="Invalid redirect URL", final_url=final_url, in_stock=None, domain_allowed=False, details={})
                    
                    final_allowed = any(fnmatch.fnmatch(final_domain, p) for p in allowed_domains)
                    if not final_allowed:
                        return VerificationResult(ok=False, status="rejected", reason="Redirect to non-allowed domain", final_url=final_url, in_stock=None, domain_allowed=False, details={})
                    
                    # Check if URL leads to IP address
                    try:
                        ipaddress.ip_address(final_domain)
                        return VerificationResult(ok=False, status="rejected", reason="URL leads to IP address", final_url=final_url, in_stock=None, domain_allowed=True, details={})
                    except ValueError:
                        pass
                    
                    if resp.status != 200:
                        return VerificationResult(ok=False, status="suspicious", reason=f"HTTP status {resp.status}", final_url=final_url, in_stock=None, domain_allowed=True, details={})
                    
                    # Fix: Add error handling for HTML parsing
                    try:
                        text = await resp.text()
                        soup = BeautifulSoup(text, 'html.parser')
                        title = soup.title.string.lower() if soup.title and soup.title.string else ''
                    except Exception as e:
                        logger.warning(f"HTML parsing error for {final_url}: {e}")
                        return VerificationResult(ok=False, status="suspicious", reason=f"HTML parsing error: {str(e)[:50]}", final_url=final_url, in_stock=None, domain_allowed=True, details={})
                    
                    # Check for suspicious title content
                    if 'login' in title or 'phish' in title or 'error' in title:
                        return VerificationResult(ok=False, status="rejected", reason="Suspicious HTML title", final_url=final_url, in_stock=None, domain_allowed=True, details={})
                    
                    # Verify it's a legitimate store page
                    if not ('popmart' in title or 'labubu' in title or 'product' in title):
                        return VerificationResult(ok=False, status="suspicious", reason="Unexpected page title", final_url=final_url, in_stock=None, domain_allowed=True, details={})
                    
                    lower_text = text.lower()
                    in_stock = None
                    
                    # Check stock status
                    if 'in stock' in lower_text or 'available' in lower_text or '"stock": true' in lower_text or 'add to cart' in lower_text or 'add to bag' in lower_text:
                        in_stock = True
                    elif 'sold out' in lower_text or 'out of stock' in lower_text or 'unavailable' in lower_text or '"stock": false' in lower_text or 'notify me' in lower_text:
                        in_stock = False
                    
                    if in_stock is True:
                        return VerificationResult(ok=True, status="verified_safe", reason="In stock and verified", final_url=final_url, in_stock=True, domain_allowed=True, details={})
                    elif in_stock is False:
                        return VerificationResult(ok=False, status="rejected", reason="Out of stock", final_url=final_url, in_stock=False, domain_allowed=True, details={})
                    else:
                        return VerificationResult(ok=False, status="suspicious", reason="Stock status uncertain", final_url=final_url, in_stock=None, domain_allowed=True, details={})
                        
            except ClientSSLError as e:
                logger.error(f"SSL error for {url}: {e}")
                return VerificationResult(ok=False, status="rejected", reason="SSL/TLS validation failed", final_url=None, in_stock=None, domain_allowed=domain_allowed, details={})
            except ClientTimeout as e:
                if attempt == retries - 1:
                    logger.warning(f"Timeout for {url} after {retries} attempts")
                    return VerificationResult(ok=False, status="suspicious", reason="Timeout", final_url=None, in_stock=None, domain_allowed=domain_allowed, details={})
                await asyncio.sleep(backoff * (2 ** attempt))
            except aiohttp.ClientError as e:
                if attempt == retries - 1:
                    logger.error(f"Client error for {url}: {e}")
                    return VerificationResult(ok=False, status="suspicious", reason=str(e)[:100], final_url=None, in_stock=None, domain_allowed=domain_allowed, details={})
                await asyncio.sleep(backoff * (2 ** attempt))
            except Exception as e:
                logger.error(f"Unexpected error verifying {url}: {e}")
                return VerificationResult(ok=False, status="suspicious", reason=f"Unexpected error: {str(e)[:50]}", final_url=None, in_stock=None, domain_allowed=domain_allowed, details={})
    
    # Should never reach here, but just in case
    return VerificationResult(ok=False, status="suspicious", reason="Verification failed", final_url=None, in_stock=None, domain_allowed=domain_allowed, details={})
