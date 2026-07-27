"""Factory for creating per-request provider clients.

Credentials are read from HTTP request headers:
  X-Provider          : gitlab | github | bitbucket | gitea
  X-Provider-Token    : access token / app password
  X-Provider-URL      : base URL (defaults to the public cloud URL)
  X-Provider-Username : org name (GitHub), workspace (Bitbucket), org (Gitea)
  X-Provider-Project-Ids   : comma-separated repo IDs / full_names (optional)
  X-Provider-Project-Limit : max repos to auto-discover (default: 20)

For WebSocket connections (browser cannot set headers), pass the same fields
as query parameters: provider, token, url, username, project_ids, limit.
"""
from fastapi import Header, HTTPException, Query
from typing import Optional, Annotated
from config import get_settings
from services.base_client import BaseProviderClient
from services.gitlab_client import GitLabClient
from services.github_client import GitHubClient
from services.bitbucket_client import BitbucketClient
from services.gitea_client import GiteaClient

_DEFAULT_URLS = {
    "gitlab":    "https://gitlab.com",
    "github":    "https://api.github.com",
    "bitbucket": "https://api.bitbucket.org",
    "gitea":     "https://gitea.com",
}

_CLASSES = {
    "gitlab":    GitLabClient,
    "github":    GitHubClient,
    "bitbucket": BitbucketClient,
    "gitea":     GiteaClient,
}


def build_client(
    provider: str,
    token: str,
    url: str,
    username: str,
    project_ids: str,
    project_limit: int,
) -> BaseProviderClient:
    provider = (provider or "gitlab").lower()
    if provider not in _CLASSES:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{provider}'. Supported: {', '.join(_CLASSES)}",
        )
    if not token:
        raise HTTPException(
            status_code=401,
            detail="No provider token supplied. Configure your credentials in Settings.",
        )
    cls = _CLASSES[provider]
    effective_url = url or _DEFAULT_URLS[provider]
    ttl = get_settings().cache_ttl
    return cls(
        token=token,
        base_url=effective_url,
        username=username,
        project_ids=project_ids,
        project_limit=project_limit,
        cache_ttl=ttl,
    )


# ── FastAPI dependency: credentials from request headers ─────────────────────

def get_client(
    x_provider:            Annotated[str, Header()] = "",
    x_provider_token:      Annotated[str, Header()] = "",
    x_provider_url:        Annotated[str, Header()] = "",
    x_provider_username:   Annotated[str, Header()] = "",
    x_provider_project_ids: Annotated[str, Header()] = "",
    x_provider_project_limit: Annotated[int, Header()] = 20,
) -> BaseProviderClient:
    return build_client(
        provider=x_provider,
        token=x_provider_token,
        url=x_provider_url,
        username=x_provider_username,
        project_ids=x_provider_project_ids,
        project_limit=x_provider_project_limit,
    )


# ── Factory: credentials from query parameters (WebSocket) ───────────────────

def get_client_from_params(
    provider:    str = "gitlab",
    token:       str = "",
    url:         str = "",
    username:    str = "",
    project_ids: str = "",
    limit:       int = 20,
) -> BaseProviderClient:
    return build_client(
        provider=provider,
        token=token,
        url=url,
        username=username,
        project_ids=project_ids,
        project_limit=limit,
    )
