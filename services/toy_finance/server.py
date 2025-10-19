"""FastMCP server exposing a toy stock price lookup tool."""

from pathlib import Path
from fastmcp import FastMCP


APP_NAME = "toy-finance-server"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8030
DEFAULT_PATH = "/mcp"


with Path(__file__).with_name("manifest.json").open(encoding="utf-8") as f:
    INSTRUCTIONS = f.read()
mcp = FastMCP(APP_NAME, instructions=INSTRUCTIONS)


@mcp.tool
def get_stock_price(symbol: str) -> dict[str, float | str]:
    """Return a mock stock price for a given ticker symbol."""
    mock_data = {
        "AAPL": 224.52,
        "GOOG": 182.67,
        "TSLA": 207.31,
        "MSFT": 411.15,
    }
    ticker = symbol.upper()
    price = mock_data.get(ticker, 100.00)
    return {"symbol": ticker, "price": price}


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        path=DEFAULT_PATH,
    )
