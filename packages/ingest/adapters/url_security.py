from __future__ import annotations

import socket
from collections.abc import Sequence
from ipaddress import ip_address
from urllib.parse import urlparse


def validate_public_http_url(
    source_ref: str,
    *,
    allowlist_enabled: bool = False,
    allowlist_hosts: Sequence[str] | None = None,
) -> None:
    parsed = urlparse(source_ref)

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are allowed")

    if parsed.username or parsed.password:
        raise ValueError("Credentials in URL are not allowed")

    host = parsed.hostname
    if not host:
        raise ValueError("URL host is required")

    blocked_hosts = {"localhost", "127.0.0.1", "::1"}
    if host.lower() in blocked_hosts:
        raise ValueError("Localhost URLs are not allowed")
    if allowlist_enabled:
        _enforce_allowlist(host=host, allowlist_hosts=allowlist_hosts)

    try:
        address = ip_address(host)
    except ValueError:
        try:
            infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError("Unable to resolve URL host") from exc

        resolved = {item[4][0] for item in infos if item[4]}
        for resolved_ip in resolved:
            if isinstance(resolved_ip, str):
                _reject_if_non_public(resolved_ip.split("%", maxsplit=1)[0])
        return

    _reject_if_non_public(str(address))


def _reject_if_non_public(value: str) -> None:
    address = ip_address(value)
    if (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        raise ValueError("Non-public IP URLs are not allowed")


def _enforce_allowlist(*, host: str, allowlist_hosts: Sequence[str] | None) -> None:
    normalized_allowlist = [
        item.strip().lower().rstrip(".")
        for item in (allowlist_hosts or [])
        if item.strip()
    ]
    if not normalized_allowlist:
        raise ValueError("Host allowlist mode is enabled but no allowlist hosts are configured")

    normalized_host = host.lower().rstrip(".")
    for allowed in normalized_allowlist:
        if normalized_host == allowed or normalized_host.endswith(f".{allowed}"):
            return
    raise ValueError("URL host is not in configured allowlist")
