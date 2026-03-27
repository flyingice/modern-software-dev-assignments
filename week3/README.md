# Week 3 — Weather & Finance MCP Server

An MCP server built with [FastMCP](https://github.com/modelcontextprotocol/python-sdk) that exposes two tools:

| Tool | Source API | Description |
|------|-----------|-------------|
| `get_stock_quote` | Yahoo Finance (RapidAPI) | Real-time stock price, change, and market state for a ticker symbol |
| `get_weather` | WeatherAPI.com (RapidAPI) | Current weather conditions for a given city |

## Prerequisites

- Python 3.11+
- A [RapidAPI](https://rapidapi.com/) account with subscriptions to:
  - [Yahoo Finance](https://rapidapi.com/sparior/api/yahoo-finance15) (free tier available)
  - [WeatherAPI.com](https://rapidapi.com/weatherapi/api/weatherapi-com) (free tier available)

## Setup

```bash
cd week3

# Create a virtual environment and install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set the required environment variable
export RAPIDAPI_KEY="your-rapidapi-key-here"
```

### Optional environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `YAHOO_FINANCE_HOST` | `yahoo-finance15.p.rapidapi.com` | RapidAPI host for Yahoo Finance |
| `WEATHERAPI_HOST` | `weatherapi-com.p.rapidapi.com` | RapidAPI host for WeatherAPI.com |
| `REQUEST_TIMEOUT` | `10` | HTTP request timeout in seconds |

## Running the server

### STDIO (default — for Claude Desktop / Cursor)

```bash
python -m server.main
```

The server communicates over stdin/stdout using the MCP protocol. All logs go to stderr.

### Switching to SSE or Streamable HTTP (future)

The transport is a single argument in `server/main.py`:

```python
mcp.run(transport="sse")             # SSE on port 8000
mcp.run(transport="streamable-http") # Streamable HTTP
```

No tool or client code changes are needed.

## Claude Desktop configuration (macOS)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "weather-finance": {
            "command": "/bin/bash",
            "args": ["-c", "cd /path/to/week3 && .venv/bin/python -m server.main"],
            "env": {
                "RAPIDAPI_KEY": "your-rapidapi-key-here"
            }
        }
    }
}
```

Replace `/path/to/week3` with the absolute path to the `week3/` directory. Restart Claude Desktop after saving.

## Example invocation flow

Once configured, open Claude Desktop and use natural language:

### Stock quote

> **You:** What's the current price of AAPL?

Claude calls `get_stock_quote` with `symbol="AAPL"` and returns something like:

```json
{
    "symbol": "AAPL",
    "name": "NMS",
    "price": 227.48,
    "change": 1.23,
    "change_percent": 0.54,
    "currency": "USD",
    "market_state": "REGULAR",
    "exchange": "NMS"
}
```

### Weather

> **You:** What's the weather in Tokyo?

Claude calls `get_weather` with `city="Tokyo"` and returns something like:

```json
{
    "city": "Tokyo",
    "region": "Tokyo",
    "country": "Japan",
    "localtime": "2026-03-24 15:30",
    "temperature_c": 18.0,
    "temperature_f": 64.4,
    "feels_like_c": 17.2,
    "feels_like_f": 63.0,
    "condition": "Partly cloudy",
    "humidity": 55,
    "wind_kph": 12.0,
    "wind_mph": 7.5,
    "wind_direction": "NE",
    "pressure_mb": 1015.0,
    "uv_index": 4.0
}
```

## Tool reference

### `get_stock_quote`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `symbol` | string | yes | Ticker symbol (e.g. `AAPL`, `MSFT`, `TSLA`) |

### `get_weather`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `city` | string | yes | City name (e.g. `London`, `New York`), postal code, or lat/lon pair (`48.8567,2.3508`) |

## Architecture

```
server/
├── main.py              # FastMCP server setup and entrypoint
├── config.py            # Environment-based settings (single source of truth)
├── clients/
│   ├── base.py          # Shared HTTP client with retry, timeout, rate-limit
│   ├── yahoo_finance.py # Yahoo Finance integration
│   └── weatherapi.py    # WeatherAPI.com integration
└── tools/
    ├── stocks.py        # MCP tool: get_stock_quote
    └── weather.py       # MCP tool: get_weather
```

**Layered design:**
- **Config** — all secrets and tunables live in `config.py`, read from env vars
- **Clients** — HTTP logic with retries and rate-limit back-off; each API gets its own module
- **Tools** — thin MCP wrappers that delegate to clients and format results
- **Transport** — a single `mcp.run()` call in `main.py`, swappable without touching any other layer

Adding a new API integration means creating one client module and one tool module, then calling `register(mcp)` in `main.py`.
