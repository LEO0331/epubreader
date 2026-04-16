from __future__ import annotations

import pytest

from packages.ingest.adapters.url_security import validate_public_http_url


@pytest.mark.parametrize(
    "url",
    [
        "https://8.8.8.8/book.epub",
    ],
)
def test_validate_public_http_url_allows_public_hosts(url: str):
    validate_public_http_url(url)


def test_validate_public_http_url_rejects_hostname_with_private_dns(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [(None, None, None, None, ("10.0.0.5", 0))]

    monkeypatch.setattr(
        "packages.ingest.adapters.url_security.socket.getaddrinfo",
        fake_getaddrinfo,
    )
    with pytest.raises(ValueError):
        validate_public_http_url("https://example.com/book.epub")


def test_validate_public_http_url_allowlist_allows_subdomain(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [(None, None, None, None, ("8.8.8.8", 0))]

    monkeypatch.setattr(
        "packages.ingest.adapters.url_security.socket.getaddrinfo",
        fake_getaddrinfo,
    )
    validate_public_http_url(
        "https://cdn.example.com/book.epub",
        allowlist_enabled=True,
        allowlist_hosts=["example.com"],
    )


def test_validate_public_http_url_allowlist_rejects_non_member(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [(None, None, None, None, ("8.8.8.8", 0))]

    monkeypatch.setattr(
        "packages.ingest.adapters.url_security.socket.getaddrinfo",
        fake_getaddrinfo,
    )
    with pytest.raises(ValueError):
        validate_public_http_url(
            "https://cdn.example.com/book.epub",
            allowlist_enabled=True,
            allowlist_hosts=["other.com"],
        )


def test_validate_public_http_url_allowlist_requires_hosts(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        return [(None, None, None, None, ("8.8.8.8", 0))]

    monkeypatch.setattr(
        "packages.ingest.adapters.url_security.socket.getaddrinfo",
        fake_getaddrinfo,
    )
    with pytest.raises(ValueError):
        validate_public_http_url(
            "https://example.com/book.epub",
            allowlist_enabled=True,
            allowlist_hosts=[],
        )


@pytest.mark.parametrize(
    "url",
    [
        "file:///tmp/a.epub",
        "https://localhost/a.epub",
        "https://127.0.0.1/a.epub",
        "https://[::1]/a.epub",
        "https://10.1.2.3/a.epub",
        "https://172.16.0.5/a.epub",
        "https://192.168.1.8/a.epub",
        "https://169.254.1.1/a.epub",
        "https://user:pass@example.com/a.epub",
    ],
)
def test_validate_public_http_url_rejects_unsafe_hosts(url: str):
    with pytest.raises(ValueError):
        validate_public_http_url(url)
