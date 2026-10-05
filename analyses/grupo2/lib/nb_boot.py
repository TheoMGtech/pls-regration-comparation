"""Helpers compartilhados pelos notebooks da Base 2.

Uso no topo de cada notebook (a partir de analyses/grupo2/...):

    from pathlib import Path
    import sys
    GROUP = Path("../..").resolve() if Path.cwd().name in {...} else ...
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def bootstrap(notebook_file: str | Path | None = None) -> Path:
    """Coloca analyses/grupo2 no sys.path e devolve GROUP_DIR."""
    # tenta achar a pasta grupo2 subindo a partir do cwd
    here = Path.cwd().resolve()
    candidates = [
        here,
        here.parent,
        here.parent.parent,
        here.parent.parent.parent,
        Path(__file__).resolve().parents[1],
    ]
    group = None
    for c in candidates:
        if (c / "config.py").exists() and (c / "lib").is_dir():
            group = c
            break
    if group is None:
        raise RuntimeError(
            "Não achei analyses/grupo2 (config.py). "
            "Abra o notebook a partir dessa árvore ou rode com o kernel na pasta certa."
        )
    if str(group) not in sys.path:
        sys.path.insert(0, str(group))
    return group


def require_file(path: Path, hint: str) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"Arquivo necessário não encontrado: {path}\n"
            f"Rode antes: {hint}"
        )
    return path


def save_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
