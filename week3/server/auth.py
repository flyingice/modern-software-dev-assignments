"""In-memory OAuth 2.0 authorization server provider.

Implements the OAuthAuthorizationServerProvider protocol using plain
dictionaries.  Suitable for local development — all state is lost when
the process restarts.

DEV-ONLY LIMITATIONS
--------------------
This provider auto-approves every authorization request and allows open
dynamic client registration.  In a production deployment you would:

1. **Restrict client registration** — disable dynamic registration
   (``ClientRegistrationOptions(enabled=False)``) and pre-register only
   trusted clients with known ``client_id`` / ``client_secret`` pairs,
   or gate registration behind admin authentication.

2. **Require real user authentication in authorize()** — redirect to a
   login page or a third-party identity provider (Google, GitHub, Okta,
   etc.) so only authenticated users can grant authorization codes.

3. **Use persistent storage** — replace the in-memory dicts with a
   database so tokens survive restarts and can be shared across
   replicas.
"""

from __future__ import annotations

import logging
import secrets
import time

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    RefreshToken,
    construct_redirect_uri,
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


logger = logging.getLogger(__name__)

# Token lifetimes (seconds).
_AUTH_CODE_TTL = 300       # 5 minutes
_ACCESS_TOKEN_TTL = 3600   # 1 hour


class InMemoryOAuthProvider:
    """OAuth authorization server backed by in-memory dicts."""

    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, AuthorizationCode] = {}
        self._access_tokens: dict[str, AccessToken] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}

    # ------------------------------------------------------------------
    # Client registration
    # ------------------------------------------------------------------

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self._clients.get(client_id)

    async def register_client(
        self, client_info: OAuthClientInformationFull
    ) -> None:
        # DEV: accepts any client.  In production, either disable dynamic
        # registration entirely or validate the caller (e.g. require an
        # admin bearer token, check an allow-list of redirect URIs, or
        # verify a signed software statement).
        self._clients[client_info.client_id] = client_info
        logger.info("registered client %s", client_info.client_id)

    # ------------------------------------------------------------------
    # Authorization
    # ------------------------------------------------------------------

    async def authorize(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams,
    ) -> str:
        # DEV: auto-approve — no login, no consent screen.
        #
        # In production this method is the security gate.  A real
        # implementation would:
        #
        #   1. Redirect the user's browser to a login / consent page
        #      (or to a third-party identity provider such as Google or
        #      GitHub for federated authentication).
        #   2. After the user authenticates and grants consent, generate
        #      the authorization code and redirect back to
        #      ``params.redirect_uri`` with the code.
        #
        # Only after that human step should the code below execute.
        # Without it, any client that can reach the server can obtain
        # tokens — which is acceptable for localhost development but
        # not for a public deployment.
        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            scopes=params.scopes or [],
            expires_at=time.time() + _AUTH_CODE_TTL,
            code_challenge=params.code_challenge,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            resource=params.resource,
        )
        logger.info("issued auth code for client %s", client.client_id)
        return construct_redirect_uri(
            str(params.redirect_uri), code=code, state=params.state
        )

    # ------------------------------------------------------------------
    # Authorization-code exchange
    # ------------------------------------------------------------------

    async def load_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: str,
    ) -> AuthorizationCode | None:
        ac = self._auth_codes.get(authorization_code)
        if ac is None or ac.client_id != client.client_id:
            return None
        if ac.expires_at < time.time():
            self._auth_codes.pop(authorization_code, None)
            return None
        return ac

    async def exchange_authorization_code(
        self,
        client: OAuthClientInformationFull,
        authorization_code: AuthorizationCode,
    ) -> OAuthToken:
        # One-time use.
        self._auth_codes.pop(authorization_code.code, None)
        return self._issue_tokens(
            client.client_id,
            authorization_code.scopes,
            authorization_code.resource,
        )

    # ------------------------------------------------------------------
    # Refresh-token exchange
    # ------------------------------------------------------------------

    async def load_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: str,
    ) -> RefreshToken | None:
        rt = self._refresh_tokens.get(refresh_token)
        if rt is None or rt.client_id != client.client_id:
            return None
        return rt

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        # Rotate: delete old refresh token.
        self._refresh_tokens.pop(refresh_token.token, None)
        return self._issue_tokens(
            client.client_id,
            scopes or refresh_token.scopes,
            resource=None,
        )

    # ------------------------------------------------------------------
    # Token verification & revocation
    # ------------------------------------------------------------------

    async def load_access_token(self, token: str) -> AccessToken | None:
        at = self._access_tokens.get(token)
        if at is None:
            return None
        if at.expires_at is not None and at.expires_at < time.time():
            self._access_tokens.pop(token, None)
            return None
        return at

    async def revoke_token(
        self, token: AccessToken | RefreshToken
    ) -> None:
        if isinstance(token, AccessToken):
            self._access_tokens.pop(token.token, None)
        elif isinstance(token, RefreshToken):
            self._refresh_tokens.pop(token.token, None)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _issue_tokens(
        self,
        client_id: str,
        scopes: list[str],
        resource: str | None,
    ) -> OAuthToken:
        access = secrets.token_urlsafe(32)
        refresh = secrets.token_urlsafe(32)
        now = int(time.time())

        self._access_tokens[access] = AccessToken(
            token=access,
            client_id=client_id,
            scopes=scopes,
            expires_at=now + _ACCESS_TOKEN_TTL,
            resource=resource,
        )
        self._refresh_tokens[refresh] = RefreshToken(
            token=refresh,
            client_id=client_id,
            scopes=scopes,
        )
        return OAuthToken(
            access_token=access,
            token_type="Bearer",
            expires_in=_ACCESS_TOKEN_TTL,
            scope=" ".join(scopes),
            refresh_token=refresh,
        )
