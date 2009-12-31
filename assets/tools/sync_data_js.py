#!/usr/bin/env python3
"""Regenerate the file:// compatible data.js wrapper from data.json."""

from pathlib import Path
import json


def main() -> int:
    assets = Path(__file__).resolve().parents[1]
    data = json.loads((assets / "data.json").read_text(encoding="utf-8"))
    (assets / "data.js").write_text(
        "window.NOTES_DATA="
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"synced: {assets / 'data.js'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
