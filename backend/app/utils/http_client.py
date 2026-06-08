"""
Async HTTP client with retry and rate-limit handling.
"""

import asyncio
import logging
import httpx
from typing import Optional, Dict, Any

from app.config.settings import settings

logger = logging.getLogger(__name__)


async def make_request(
    method: str,
    url: str,
    headers: Optional[Dict] = None,
    json: Optional[Dict] = None,
    params: Optional[Dict] = None,
    retries: int = None,
) -> Optional[Dict[str, Any]]:
    """
    Make an HTTP request with retry logic and error handling.
    Returns parsed JSON or None on failure.
    """
    max_retries = retries if retries is not None else settings.MAX_RETRIES
    delay = settings.RETRY_DELAY

    for attempt in range(max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    json=json,
                    params=params,
                )

                if response.status_code == 429:
                    wait = float(response.headers.get("Retry-After", delay * (2 ** attempt)))
                    logger.warning(f"Rate limited on {url}. Waiting {wait}s...")
                    await asyncio.sleep(wait)
                    continue

                if response.status_code >= 500:
                    logger.warning(f"Server error {response.status_code} on attempt {attempt + 1}")
                    if attempt < max_retries:
                        await asyncio.sleep(delay * (2 ** attempt))
                        continue
                    return None

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
            if attempt < max_retries:
                await asyncio.sleep(delay * (2 ** attempt))
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            if attempt < max_retries:
                await asyncio.sleep(delay)
            else:
                return None

    logger.error(f"All {max_retries + 1} attempts failed for {url}")
    return None
