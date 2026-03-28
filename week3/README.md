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
| `FASTMCP_HOST` | `0.0.0.0` | Server bind address |
| `FASTMCP_PORT` | `8000` | Server port |
| `OAUTH_ENABLED` | `false` | Enable OAuth 2.0 authentication |
| `OAUTH_ISSUER_URL` | `http://localhost:8000` | OAuth issuer URL |
| `OAUTH_REQUIRED_SCOPES` | *(empty)* | Comma-separated scopes required to access tools |

## Running the server

```bash
python -m server.main
```

The server starts on `http://0.0.0.0:8000` using the Streamable HTTP transport. The MCP endpoint is at `/mcp`.

### With OAuth 2.0 authentication

```bash
OAUTH_ENABLED=true python -m server.main
```

This activates the built-in OAuth 2.0 authorization server. Unauthenticated requests to `/mcp` will receive a `401` response.

## OAuth 2.0 authentication flow

When `OAUTH_ENABLED=true`, the server exposes standard OAuth 2.0 endpoints. Clients must complete the following flow to obtain a bearer token.

### 1. Discover endpoints

```bash
curl http://localhost:8000/.well-known/oauth-authorization-server
```

Returns the authorization, token, and registration endpoint URLs.

### 2. Register a client (dynamic client registration)

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "redirect_uris": ["http://localhost:3000/callback"],
    "grant_types": ["authorization_code", "refresh_token"],
    "response_types": ["code"],
    "token_endpoint_auth_method": "client_secret_post"
  }'
```

Save the returned `client_id` and `client_secret`.

### 3. Authorize (with PKCE)

Generate a PKCE code verifier and challenge:

```bash
CODE_VERIFIER=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
CODE_CHALLENGE=$(python3 -c "
import hashlib, base64
v = '$CODE_VERIFIER'
digest = hashlib.sha256(v.encode()).digest()
print(base64.urlsafe_b64encode(digest).rstrip(b'=').decode())
")
```

Open the authorization URL in a browser or follow the redirect:

```
http://localhost:8000/authorize?response_type=code&client_id=CLIENT_ID&redirect_uri=http://localhost:3000/callback&code_challenge=CODE_CHALLENGE&code_challenge_method=S256&state=random_state
```

The dev server auto-approves and redirects to your `redirect_uri` with a `code` parameter.

### 4. Exchange authorization code for tokens

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&redirect_uri=http://localhost:3000/callback&client_id=CLIENT_ID&client_secret=CLIENT_SECRET&code_verifier=CODE_VERIFIER"
```

Returns an `access_token` (valid 1 hour) and `refresh_token`.

### 5. Call the MCP endpoint

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '...'
```

### 6. Refresh an expired token

```bash
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=REFRESH_TOKEN&client_id=CLIENT_ID&client_secret=CLIENT_SECRET"
```

## Claude Desktop configuration (macOS)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "weather-finance": {
            "command": "npx",
            "args": ["-y", "mcp-remote", "http://localhost:8000/mcp"],
            "env": {
                "PATH": "/path/to/node/bin:/usr/local/bin:/usr/bin:/bin"
            }
        }
    }
}
```

`mcp-remote` acts as a stdio-to-HTTP bridge since Claude Desktop only supports stdio in config files. Update the `PATH` to include your Node.js `bin` directory. Start the MCP server before launching Claude Desktop.

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
├── auth.py              # In-memory OAuth 2.0 authorization server provider
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
- **Auth** — optional OAuth 2.0 provider with in-memory storage for dev; swap for a real provider in production
- **Clients** — HTTP logic with retries and rate-limit back-off; each API gets its own module
- **Tools** — thin MCP wrappers that delegate to clients and format results
- **Transport** — a single `mcp.run()` call in `main.py`, swappable without touching any other layer

Adding a new API integration means creating one client module and one tool module, then calling `register(mcp)` in `main.py`.
