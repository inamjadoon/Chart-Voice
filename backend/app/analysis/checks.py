"""Sanity checks: warn the user when the extracted data looks wrong."""

from app.extraction.parse import ParsedTable

MESSAGES = {
    "parse_failed": "We could not read a data table from this image. Try a clearer or larger chart.",
    "missing_values": "Some values could not be read and are shown as blank.",
    "non_numeric": "Some cells did not contain numbers and were left blank.",
    "single_point": "Only one data point was found, so trends cannot be described.",
    "shares_not_100": "The pie chart's percentages do not add up to about 100%, so some values may be misread.",
}


def warning(code: str) -> dict:
    return {"code": code, "message": MESSAGES[code]}


def run_checks(parsed: ParsedTable, chart_type: str) -> list[dict]:
    if not parsed.ok:
        return [warning("parse_failed")]

    warnings = []
    numeric = [row[1:] for row in parsed.rows]
    if any(v is None for row in numeric for v in row):
        warnings.append(warning("missing_values"))
    if parsed.non_numeric:
        warnings.append(warning("non_numeric"))
    if len(parsed.rows) < 2:
        warnings.append(warning("single_point"))

    if chart_type == "pie":
        values = [row[0] for row in numeric if row and isinstance(row[0], (int, float))]
        looks_like_percentages = values and all(0 <= v <= 100 for v in values)
        if looks_like_percentages and not 95 <= sum(values) <= 105:
            warnings.append(warning("shares_not_100"))
    return warnings
