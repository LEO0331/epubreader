from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class LimitedFetchResult:
    content: bytes
    headers: httpx.Headers


def fetch_limited_bytes(
    source_ref: str,
    *,
    max_bytes: int,
    resource_label: str,
    timeout: int = 30,
) -> LimitedFetchResult:
    with httpx.stream(
        "GET",
        source_ref,
        timeout=timeout,
        follow_redirects=False,
        trust_env=False,
    ) as response:
        if 300 <= response.status_code < 400:
            raise ValueError(f"Redirect responses are not allowed for {resource_label} ingest")
        response.raise_for_status()

        content_length = response.headers.get("content-length")
        if content_length:
            try:
                parsed_content_length = int(content_length)
            except ValueError:
                parsed_content_length = None
            if parsed_content_length is not None and parsed_content_length > max_bytes:
                raise ValueError(f"Remote {resource_label} exceeds maximum allowed size")

        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_bytes():
            total += len(chunk)
            if total > max_bytes:
                raise ValueError(f"Remote {resource_label} exceeds maximum allowed size")
            chunks.append(chunk)

        return LimitedFetchResult(content=b"".join(chunks), headers=response.headers)
