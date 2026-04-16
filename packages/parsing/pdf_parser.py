from __future__ import annotations

import multiprocessing as mp
from pathlib import Path
from queue import Empty
from time import monotonic
from typing import Any


def _load_pdf_reader(path: Path) -> Any:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("PDF parsing dependency missing: install pypdf") from exc
    return PdfReader(str(path))


def parse_pdf(
    path: Path,
    *,
    ocr_enabled: bool = True,
    ocr_langs: str = "chi_tra+eng",
    ocr_min_text_chars: int = 80,
    ocr_tesseract_cmd: str | None = None,
    ocr_max_pages: int = 0,
    ocr_page_timeout_seconds: int = 0,
    ocr_total_timeout_seconds: int = 0,
    ocr_isolate_worker: bool = False,
) -> dict[str, object]:
    reader = _load_pdf_reader(path)

    metadata_obj = reader.metadata
    title = _metadata_value(metadata_obj, "title", "/Title")
    author = _metadata_value(metadata_obj, "author", "/Author")

    sections: list[dict[str, object]] = []
    ordinal = 0
    ocr_attempted_pages = 0
    ocr_used_pages = 0
    ocr_skipped_due_to_limits = 0
    ocr_available = ocr_enabled
    ocr_started_at = monotonic()

    for page_number, page in enumerate(reader.pages, start=1):
        native_text = page.extract_text() or ""
        text = native_text.strip()

        if ocr_enabled and len(text) < ocr_min_text_chars:
            max_pages_reached = ocr_max_pages > 0 and ocr_attempted_pages >= ocr_max_pages
            total_timeout_reached = (
                ocr_total_timeout_seconds > 0
                and (monotonic() - ocr_started_at) >= ocr_total_timeout_seconds
            )
            if max_pages_reached or total_timeout_reached:
                ocr_skipped_due_to_limits += 1
            else:
                ocr_attempted_pages += 1
                ocr_text, page_ocr_available = _ocr_extract_page_text(
                    path=path,
                    page_number=page_number,
                    ocr_langs=ocr_langs,
                    ocr_tesseract_cmd=ocr_tesseract_cmd,
                    page_timeout_seconds=ocr_page_timeout_seconds,
                    isolate_worker=ocr_isolate_worker,
                )
                if not page_ocr_available:
                    ocr_available = False
                ocr_text_clean = ocr_text.strip()
                if ocr_text_clean:
                    text = ocr_text_clean
                    ocr_used_pages += 1

        if not text:
            continue

        page_heading = f"Page {page_number}"
        sections.append(
            {
                "ordinal": ordinal,
                "heading": page_heading,
                "heading_path": [page_heading],
                "content": text,
                "source_locator": f"page:{page_number}",
            }
        )
        ordinal += 1

    return {
        "metadata": {
            "title": title,
            "author": author,
            "language": None,
            "toc": [],
            "pdf": {"page_count": len(reader.pages)},
            "ocr": {
                "enabled": ocr_enabled,
                "langs": ocr_langs,
                "min_text_chars": ocr_min_text_chars,
                "max_pages": ocr_max_pages,
                "page_timeout_seconds": ocr_page_timeout_seconds,
                "total_timeout_seconds": ocr_total_timeout_seconds,
                "isolate_worker": ocr_isolate_worker,
                "attempted_pages": ocr_attempted_pages,
                "used_pages": ocr_used_pages,
                "skipped_due_to_limits": ocr_skipped_due_to_limits,
                "available": ocr_available,
            },
        },
        "sections": sections,
    }


def _ocr_extract_page_text(
    *,
    path: Path,
    page_number: int,
    ocr_langs: str,
    ocr_tesseract_cmd: str | None,
    page_timeout_seconds: int = 0,
    isolate_worker: bool = False,
) -> tuple[str, bool]:
    should_isolate = isolate_worker or page_timeout_seconds > 0
    if should_isolate:
        return _ocr_extract_page_text_isolated(
            path=path,
            page_number=page_number,
            ocr_langs=ocr_langs,
            ocr_tesseract_cmd=ocr_tesseract_cmd,
            page_timeout_seconds=page_timeout_seconds,
        )
    return _ocr_extract_page_text_inprocess(
        path=path,
        page_number=page_number,
        ocr_langs=ocr_langs,
        ocr_tesseract_cmd=ocr_tesseract_cmd,
    )


def _ocr_extract_page_text_inprocess(
    *,
    path: Path,
    page_number: int,
    ocr_langs: str,
    ocr_tesseract_cmd: str | None,
) -> tuple[str, bool]:
    try:
        import pytesseract
        from pdf2image import convert_from_path
    except ImportError:
        return "", False

    try:
        if ocr_tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = ocr_tesseract_cmd

        images = convert_from_path(
            str(path),
            first_page=page_number,
            last_page=page_number,
            fmt="png",
            single_file=True,
        )
        if not images:
            return "", True

        text = pytesseract.image_to_string(images[0], lang=ocr_langs)
        return text, True
    except Exception:
        # Graceful degradation: keep native PDF text path.
        return "", False


def _ocr_extract_page_text_isolated(
    *,
    path: Path,
    page_number: int,
    ocr_langs: str,
    ocr_tesseract_cmd: str | None,
    page_timeout_seconds: int,
) -> tuple[str, bool]:
    try:
        ctx = mp.get_context("spawn")
    except ValueError:
        return _ocr_extract_page_text_inprocess(
            path=path,
            page_number=page_number,
            ocr_langs=ocr_langs,
            ocr_tesseract_cmd=ocr_tesseract_cmd,
        )

    result_queue: Any = ctx.Queue()
    worker = ctx.Process(
        target=_ocr_worker_entrypoint,
        args=(
            str(path),
            page_number,
            ocr_langs,
            ocr_tesseract_cmd,
            result_queue,
        ),
    )

    try:
        worker.start()
        timeout = page_timeout_seconds if page_timeout_seconds > 0 else None
        worker.join(timeout=timeout)
        if worker.is_alive():
            worker.terminate()
            worker.join()
            return "", False

        try:
            result = result_queue.get_nowait()
        except Empty:
            return "", False
        if isinstance(result, tuple) and len(result) == 2:
            text, available = result
            if isinstance(text, str) and isinstance(available, bool):
                return text, available
        return "", False
    except Exception:
        return "", False
    finally:
        result_queue.close()
        result_queue.join_thread()


def _ocr_worker_entrypoint(
    path_str: str,
    page_number: int,
    ocr_langs: str,
    ocr_tesseract_cmd: str | None,
    result_queue: Any,
) -> None:
    text, available = _ocr_extract_page_text_inprocess(
        path=Path(path_str),
        page_number=page_number,
        ocr_langs=ocr_langs,
        ocr_tesseract_cmd=ocr_tesseract_cmd,
    )
    result_queue.put((text, available))


def _metadata_value(metadata_obj: Any, attr_name: str, key_name: str) -> str | None:
    if metadata_obj is None:
        return None

    value_attr = getattr(metadata_obj, attr_name, None)
    if isinstance(value_attr, str) and value_attr.strip():
        return value_attr.strip()

    if isinstance(metadata_obj, dict):
        value_key = metadata_obj.get(key_name)
        if isinstance(value_key, str) and value_key.strip():
            return value_key.strip()

    return None
