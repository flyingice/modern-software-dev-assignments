# Add OAuth 2.0 Authorization Server to MCP Server

## Context

The MCP server currently runs on streamable HTTP with no authentication — anyone
who can reach localhost:8000 can call the tools.  Adding OAuth 2.0 protects the
`/mcp` endpoint with bearer tokens, preparing the server for eventual cloud
deployment.  We use FastMCP's built-in auth integration (Option A: full
authorization server) with an in-memory provider suitable for local development.

## Files to Change

| File | Action |
|------|--------|
| `server/auth.py` | **Create** — `InMemoryOAuthProvider` implementing `OAuthAuthorizationServerProvider` |
| `server/config.py` | **Modify** — add `oauth_issuer_url`, `oauth_required_scopes`, `oauth_enabled` |
| `server/main.py` | **Modify** — wire provider + `AuthSettings` into `FastMCP()` when enabled |

## Implementation

### 1. `server/config.py` — add OAuth settings

```python
self.oauth_issuer_url: str = os.environ.get("OAUTH_ISSUER_URL", "http://localhost:8000")
self.oauth_required_scopes: list[str] = [
    s.strip() for s in os.environ.get("OAUTH_REQUIRED_SCOPES", "").split(",") if s.strip()
]
self.oauth_enabled: bool = os.environ.get("OAUTH_ENABLED", "false").lower() in ("true", "1", "yes")
```

`oauth_enabled` defaults to `false` so this is a non-breaking change.

### 2. `server/auth.py` — in-memory OAuth provider

Implement `OAuthAuthorizationServerProvider` with four in-memory dicts:

- `_clients: dict[str, OAuthClientInformationFull]`
- `_auth_codes: dict[str, AuthorizationCode]`
- `_access_tokens: dict[str, AccessToken]`
- `_refresh_tokens: dict[str, RefreshToken]`

Key method behaviors:
- **`authorize()`** — auto-approve flow for dev: generate code, store it, return redirect URL with `?code=...&state=...`
- **`exchange_authorization_code()`** — delete code (one-time use), generate access token (1h) + refresh token, return `OAuthToken`
- **`exchange_refresh_token()`** — rotate: delete old, generate new pair
- **`load_access_token()`** — lazy expiry check, return `None` if expired
- **`revoke_token()`** — `isinstance` check to delete from correct dict

PKCE verification is handled by the SDK's `/token` handler — provider just stores `code_challenge`.

### 3. `server/main.py` — conditional wiring

When `settings.oauth_enabled`:
- Create `InMemoryOAuthProvider()`
- Create `AuthSettings(issuer_url=..., resource_server_url=..., required_scopes=..., client_registration_options=ClientRegistrationOptions(enabled=True, valid_scopes=["read", "write"], default_scopes=["read"]), revocation_options=RevocationOptions(enabled=True))`
- Pass `auth_server_provider=` and `auth=` to `FastMCP()`

When disabled, pass `None` — server behaves exactly as before.

## Verification

1. Start server with `OAUTH_ENABLED=true python -m server.main`
2. Confirm OAuth metadata at `GET http://localhost:8000/.well-known/oauth-authorization-server`
3. Register a client via `POST http://localhost:8000/register`
4. Confirm unauthenticated `POST /mcp` returns 401
5. Complete auth code + token exchange flow, then call `/mcp` with `Authorization: Bearer <token>`
