"""Common OAuth 2.1 request handlers used by both legacy and modern auth providers."""

import logging
import os
import time
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs

import aiohttp
import jwt
from jwt import PyJWKClient
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from google.oauth2.credentials import Credentials

from auth.oauth21_session_store import store_token_session
from auth.google_auth import save_credentials_to_file
from auth.scopes import get_current_scopes
from core.config import WORKSPACE_MCP_BASE_URI, WORKSPACE_MCP_PORT

logger = logging.getLogger(__name__)


async def handle_oauth_authorize(request: Request):
    """Common handler for OAuth authorization proxy."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    # Get query parameters
    params = dict(request.query_params)

    # Add our client ID if not provided
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    if "client_id" not in params and client_id:
        params["client_id"] = client_id

    # Ensure response_type is code
    params["response_type"] = "code"

    # Merge client scopes with scopes for enabled tools only
    client_scopes = params.get("scope", "").split() if params.get("scope") else []
    # Include scopes for enabled tools only (not all tools)
    enabled_tool_scopes = get_current_scopes()
    all_scopes = set(client_scopes) | set(enabled_tool_scopes)
    params["scope"] = " ".join(sorted(all_scopes))
    logger.info(f"OAuth 2.1 authorization: Requesting scopes: {params['scope']}")

    # Build Google authorization URL
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)

    # Return redirect
    return RedirectResponse(
        url=google_auth_url,
        status_code=302,
        headers={
            "Access-Control-Allow-Origin": "*"
        }
    )


async def handle_proxy_token_exchange(request: Request):
    """Common handler for OAuth token exchange proxy."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
    try:
        # Get form data
        body = await request.body()
        content_type = request.headers.get("content-type", "application/x-www-form-urlencoded")
        
        # Parse form data to add missing client credentials
        if content_type and "application/x-www-form-urlencoded" in content_type:
            form_data = parse_qs(body.decode('utf-8'))
            
            # Check if client_id is missing (public client)
            if 'client_id' not in form_data or not form_data['client_id'][0]:
                client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
                if client_id:
                    form_data['client_id'] = [client_id]
                    logger.debug("Added missing client_id to token request")
            
            # Check if client_secret is missing (public client using PKCE)
            if 'client_secret' not in form_data:
                client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
                if client_secret:
                    form_data['client_secret'] = [client_secret]
                    logger.debug("Added missing client_secret to token request")
            
            # Reconstruct body with added credentials
            body = urlencode(form_data, doseq=True).encode('utf-8')

        # Forward request to Google
        async with aiohttp.ClientSession() as session:
            headers = {"Content-Type": content_type}

            async with session.post("https://oauth2.googleapis.com/token", data=body, headers=headers) as response:
                response_data = await response.json()

                # Log for debugging
                if response.status != 200:
                    logger.error(f"Token exchange failed: {response.status} - {response_data}")
                else:
                    logger.info("Token exchange successful")

                    # Store the token session for credential bridging
                    if "access_token" in response_data:
                        try:
                            # Extract user email from ID token if present
                            if "id_token" in response_data:
                                # Verify ID token using Google's public keys for security
                                try:
                                    # Get Google's public keys for verification
                                    jwks_client = PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")

                                    # Get signing key from JWT header
                                    signing_key = jwks_client.get_signing_key_from_jwt(response_data["id_token"])

                                    # Verify and decode the ID token
                                    id_token_claims = jwt.decode(
                                        response_data["id_token"],
                                        signing_key.key,
                                        algorithms=["RS256"],
                                        audience=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
                                        issuer="https://accounts.google.com"
                                    )
                                    user_email = id_token_claims.get("email")
                                    email_verified = id_token_claims.get("email_verified")
                                    
                                    if not email_verified:
                                        logger.error(f"Email address for user {user_email} is not verified by Google. Aborting session creation.")
                                        return JSONResponse(content={"error": "Email address not verified"}, status_code=403)
                                    elif user_email:
                                        # Try to get FastMCP session ID from request context for binding
                                        mcp_session_id = None
                                        try:
                                            # Check if this is a streamable HTTP request with session
                                            if hasattr(request, 'state') and hasattr(request.state, 'session_id'):
                                                mcp_session_id = request.state.session_id
                                                logger.info(f"Found MCP session ID for binding: {mcp_session_id}")
                                        except Exception as e:
                                            logger.debug(f"Could not get MCP session ID: {e}")
                                        
                                        # Store the token session with MCP session binding
                                        session_id = store_token_session(response_data, user_email, mcp_session_id)
                                        logger.info(f"Stored OAuth session for {user_email} (session: {session_id}, mcp: {mcp_session_id})")

                                        # Also create and store Google credentials
                                        expiry = None
                                        if "expires_in" in response_data:
                                            # Google auth library expects timezone-naive datetime
                                            expiry = datetime.utcnow() + timedelta(seconds=response_data["expires_in"])

                                        credentials = Credentials(
                                            token=response_data["access_token"],
                                            refresh_token=response_data.get("refresh_token"),
                                            token_uri="https://oauth2.googleapis.com/token",
                                            client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
                                            client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
                                            scopes=response_data.get("scope", "").split() if response_data.get("scope") else None,
                                            expiry=expiry
                                        )

                                        # Save credentials to file for legacy auth
                                        save_credentials_to_file(user_email, credentials)
                                        logger.info(f"Saved Google credentials for {user_email}")
                                except jwt.ExpiredSignatureError:
                                    logger.error("ID token has expired - cannot extract user email")
                                except jwt.InvalidTokenError as e:
                                    logger.error(f"Invalid ID token - cannot extract user email: {e}")
                                except Exception as e:
                                    logger.error(f"Failed to verify ID token - cannot extract user email: {e}")

                        except Exception as e:
                            logger.error(f"Failed to store OAuth session: {e}")

                return JSONResponse(
                    status_code=response.status,
                    content=response_data,
                    headers={
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "no-store"
                    }
                )

    except Exception as e:
        logger.error(f"Error in token proxy: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "server_error", "error_description": str(e)},
            headers={"Access-Control-Allow-Origin": "*"}
        )


async def handle_oauth_protected_resource(request: Request):
    """Common handler for OAuth protected resource metadata."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    metadata = {
        "resource": f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}",
        "authorization_servers": [
            f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}"
        ],
        "bearer_methods_supported": ["header"],
        "scopes_supported": get_current_scopes(),
        "resource_documentation": "https://developers.google.com/workspace",
        "client_registration_required": True,
        "client_configuration_endpoint": f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/.well-known/oauth-client",
    }

    return JSONResponse(
        content=metadata,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )


async def handle_oauth_authorization_server(request: Request):
    """Common handler for OAuth authorization server metadata."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    try:
        # Fetch metadata from Google
        async with aiohttp.ClientSession() as session:
            url = "https://accounts.google.com/.well-known/openid-configuration"
            async with session.get(url) as response:
                if response.status == 200:
                    metadata = await response.json()

                    # Add OAuth 2.1 required fields
                    metadata.setdefault("code_challenge_methods_supported", ["S256"])
                    metadata.setdefault("pkce_required", True)

                    # Override endpoints to use our proxies
                    metadata["token_endpoint"] = f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2/token"
                    metadata["authorization_endpoint"] = f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2/authorize"
                    metadata["enable_dynamic_registration"] = True
                    metadata["registration_endpoint"] = f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2/register"
                    return JSONResponse(
                        content=metadata,
                        headers={
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*"
                        }
                    )

        # Fallback metadata
        return JSONResponse(
            content={
                "issuer": "https://accounts.google.com",
                "authorization_endpoint": f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2/authorize",
                "token_endpoint": f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2/token",
                "userinfo_endpoint": "https://www.googleapis.com/oauth2/v2/userinfo",
                "revocation_endpoint": "https://oauth2.googleapis.com/revoke",
                "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
                "response_types_supported": ["code"],
                "code_challenge_methods_supported": ["S256"],
                "pkce_required": True,
                "grant_types_supported": ["authorization_code", "refresh_token"],
                "scopes_supported": get_current_scopes(),
                "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post"]
            },
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        )

    except Exception as e:
        logger.error(f"Error fetching auth server metadata: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Failed to fetch authorization server metadata"},
            headers={"Access-Control-Allow-Origin": "*"}
        )


async def handle_oauth_client_config(request: Request):
    """Common handler for OAuth client configuration."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )

    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    if not client_id:
        return JSONResponse(
            status_code=404,
            content={"error": "OAuth not configured"},
            headers={"Access-Control-Allow-Origin": "*"}
        )

    return JSONResponse(
        content={
            "client_id": client_id,
            "client_name": "Google Workspace MCP Server",
            "client_uri": f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}",
            "redirect_uris": [
                f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2callback",
                "http://localhost:5173/auth/callback"
            ],
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
            "scope": " ".join(get_current_scopes()),
            "token_endpoint_auth_method": "client_secret_basic",
            "code_challenge_methods": ["S256"]
        },
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    )


async def handle_oauth_register(request: Request):
    """Common handler for OAuth dynamic client registration."""
    if request.method == "OPTIONS":
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )

    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")

    if not client_id or not client_secret:
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": "OAuth not configured"},
            headers={"Access-Control-Allow-Origin": "*"}
        )

    try:
        # Parse the registration request
        body = await request.json()
        logger.info(f"Dynamic client registration request received: {body}")

        # Extract redirect URIs from the request or use defaults
        redirect_uris = body.get("redirect_uris", [])
        if not redirect_uris:
            redirect_uris = [
                f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2callback",
                "http://localhost:5173/auth/callback"
            ]

        # Build the registration response with our pre-configured credentials
        response_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "client_name": body.get("client_name", "Google Workspace MCP Server"),
            "client_uri": body.get("client_uri", f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}"),
            "redirect_uris": redirect_uris,
            "grant_types": body.get("grant_types", ["authorization_code", "refresh_token"]),
            "response_types": body.get("response_types", ["code"]),
            "scope": body.get("scope", " ".join(get_current_scopes())),
            "token_endpoint_auth_method": body.get("token_endpoint_auth_method", "client_secret_basic"),
            "code_challenge_methods": ["S256"],
            # Additional OAuth 2.1 fields
            "client_id_issued_at": int(time.time()),
            "registration_access_token": "not-required",  # We don't implement client management
            "registration_client_uri": f"{WORKSPACE_MCP_BASE_URI}:{WORKSPACE_MCP_PORT}/oauth2/register/{client_id}"
        }

        logger.info("Dynamic client registration successful - returning pre-configured Google credentials")

        return JSONResponse(
            status_code=201,
            content=response_data,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "no-store"
            }
        )

    except Exception as e:
        logger.error(f"Error in dynamic client registration: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": "invalid_request", "error_description": str(e)},
            headers={"Access-Control-Allow-Origin": "*"}
        )