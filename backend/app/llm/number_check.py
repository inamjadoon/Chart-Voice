"""Find numbers in AI-written text that are not supported by the chart data.

This is ChartVoice's guard against hallucinated numbers: every number the
model writes must match (within 0.5%) a value from the table or the facts.
"""

import re

_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")
TOLERANCE = 0.005
ALWAYS_ALLOWED = set(range(0, 13))  # counting words: "3 months", "2 lines"


def _collect(obj, out: set) -> None:
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.add(float(obj))
    elif isinstance(obj, str):
        for m in _NUMBER.findall(obj):
            try:
                out.add(float(m.replace(",", "")))
            except ValueError:
                pass
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect(v, out)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            _collect(v, out)


def allowed_numbers(table: dict, facts: dict, title: str | None = None) -> set:
    found: set = set()
    _collect(table.get("rows", []), found)
    _collect(table.get("columns", []), found)
    _collect(facts, found)
    _collect(title or "", found)
    allowed = set()
    for x in found:
        for v in (x, abs(x)):
            allowed.update({v, round(v), round(v, 1), round(v, 2)})
    return allowed


def _supported(x: float, allowed: set) -> bool:
    if x in ALWAYS_ALLOWED or abs(x) in ALWAYS_ALLOWED:
        return True
    return any(abs(x - a) <= TOLERANCE * max(abs(a), 1e-9) for a in allowed)


def check_numbers(text: str, table: dict, facts: dict, title: str | None = None) -> list[str]:
    allowed = allowed_numbers(table, facts, title)
    bad = []
    for raw in _NUMBER.findall(text):
        cleaned = raw.replace(",", "").rstrip(".")
        try:
            value = float(cleaned)
        except ValueError:
            continue
        if not _supported(value, allowed):
            bad.append(raw)
    return bad
