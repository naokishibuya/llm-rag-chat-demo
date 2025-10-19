"""
Helpers for routing finance quote requests through the toy MCP server.
"""

import re
import sys
from pathlib import Path
from typing import Final
from logger import get_logger


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from services.toy_finance import client as finance_client


LOGGER = get_logger("finance")


_SYMBOL_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"\b(?:price|quote)\s+(?:for|of)\s+([A-Za-z]{1,5})\b", re.IGNORECASE),
    re.compile(r"\b([A-Za-z]{1,5})\s+(?:stock|share)s?\s+(?:price|quote)\b", re.IGNORECASE),
    re.compile(r"\bticker\s+([A-Za-z]{1,5})\b", re.IGNORECASE),
)


def extract_symbol(user_text: str) -> str | None:
    """Return a likely ticker symbol mentioned in the user text."""
    for pattern in _SYMBOL_PATTERNS:
        match = pattern.search(user_text)
        if match:
            return match.group(1).upper()
    return None


async def fetch_quote(symbol: str) -> dict[str, str | float] | None:
    """
    Call the MCP server and return the price payload.
    """
    try:
        return await finance_client.get_stock_price(symbol)
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.warning("Failed to retrieve quote for %s: %s", symbol, exc)
        return None


async def render_quote_response(user_text: str) -> str:
    """
    Turn a user utterance into a natural language response.
    """
    symbol = extract_symbol(user_text)
    if not symbol:
        return "I couldn't spot a ticker symbol in that request."

    payload = await fetch_quote(symbol)
    if not payload:
        return "Sorry, I couldn't reach the finance quote service right now."

    LOGGER.info(payload)
    price = payload.get("price")
    if price is None:
        return f"I couldn't find a price for {symbol}."

    return f"Mock quote for {symbol}: ${float(price):.2f}."
