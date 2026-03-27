## Task

Build an MCP server using the FastMCP Python library with two core capabilities:

1. Real-time stock quotes fetched from Yahoo Finance via RapidAPI

2. Current weather information (temperature, conditions, humidity, wind, etc.) for a given city, fetched from WeatherAPI.com via RapidAPI

## Non-Functional Requirements

- Gracefully handle errors such as HTTP failures, timeouts, and empty responses to provide basic resilience
- Respect the rate limits imposed by third-party APIs
- Structure modules cleanly so that new API integrations can be added with minimal friction
- Follow logging and transport best practices for production-grade observability

## Implementation Notes

- Use Python throughout
- Validate all incoming MCP tool inputs using Pydantic models before passing them to API clients
- Accept API keys through environment variables rather than hard-coded values
- Adopt a layered architecture that accommodates OAuth 2.0-based authentication as a future enhancement without requiring structural rework
- Expose a local STDIO server as the default transport; keep the transport layer loosely coupled so the server can later be redeployed as a network-accessible remote endpoint callable by any MCP-aware agent
- Provide setup instructions covering required environment variables and run commands
- Include an example invocation flow showing exactly what a user would type or click in Claude Desktop on macOS to trigger each tool
