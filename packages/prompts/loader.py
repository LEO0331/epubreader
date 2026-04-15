from __future__ import annotations

from pathlib import Path
from string import Template


class PromptNotFoundError(FileNotFoundError):
    pass


class PromptLoader:
    def __init__(self, prompts_dir: str | Path):
        self.prompts_dir = Path(prompts_dir)

    def load(self, name: str, *, variables: dict[str, str] | None = None) -> dict[str, str]:
        path = self.prompts_dir / f"{name}.md"
        if not path.exists():
            raise PromptNotFoundError(f"Prompt file not found: {path}")

        raw = path.read_text(encoding="utf-8")
        template = Template(raw)
        rendered = template.safe_substitute(variables or {})

        return {
            "name": name,
            "version": self._version(path),
            "content": rendered,
            "path": str(path),
        }

    def _version(self, path: Path) -> str:
        stat = path.stat()
        return f"mtime-{int(stat.st_mtime)}"
