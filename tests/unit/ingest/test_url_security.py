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
