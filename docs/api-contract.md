# ChartVoice API contract

For the frontend. Backend base URL in development: `http://localhost:8000`.
Interactive docs (try every endpoint in the browser): `http://localhost:8000/docs`.
Example responses: `backend/samples/*.json` — use them as mock data before the backend is running.

Errors from every endpoint: HTTP 400 (bad input), 422 (validation), 503 (model not loaded, or AI offline) with body:

```json
{ "detail": "Human-readable message to show the user" }
```

## GET /api/health

```json
{ "status": "ok", "model_loaded": true, "extractor": "auto", "online": true }
```

`model_loaded` is `false` for the first 10–60 seconds after the server starts while DePlot (the offline reader) loads. When `online` is `true`, analyze still works during that time using the online reader.

## POST /api/analyze

Reads a chart image and returns its data, facts, summary and explanation. Online: about 5–10 s. Offline (DePlot on the CPU): 30–90 s. Show a loading state. Sending the same image again returns instantly from a cache.

Request: `multipart/form-data`

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `image` | file | yes | PNG, JPG or WEBP, max 10 MB |
| `chart_type` | string | no | `auto` (default), `bar`, `line`, `pie` |

```js
const form = new FormData();
form.append("image", file);
form.append("chart_type", "auto");
const res = await fetch(`${API_URL}/api/analyze`, { method: "POST", body: form });
```

Response:

```json
{
  "chart_type": "bar",
  "title": "Monthly sales 2025",
  "table": { "columns": ["Month", "Sales"], "rows": [["Jan", 20], ["Feb", 25], ["May", 55]] },
  "facts": { "series": [ { "name": "Sales", "max": {"label": "May", "value": 55}, "min": {"label": "Jan", "value": 20}, "trend": "increasing", "...": "see samples/analyze_response.json" } ] },
  "summary": "Sales rose from 20 in Jan to 55 in May. ...",
  "explanation": "This bar chart shows sales for each month ...",
  "text_source": "llm",
  "extractor": "vision",
  "warnings": [ { "code": "llm_unavailable", "message": "AI explanation unavailable (offline mode); showing a basic summary." } ],
  "timing_ms": { "extract": 6200, "llm": 900, "total": 7300 }
}
```

- `chart_type`: always `bar` | `line` | `pie`. With `auto`, the backend guesses: one series summing to about 100 → `pie`; years or months as labels → `line`; otherwise `bar`.
- `title`: may be `null`.
- `table.rows`: first cell is the label (string); the others are numbers or `null` (unreadable).
- `facts.series[]`: one entry per numeric column. Fields: `name`, `max`, `min`, `first`, `last` (each `{label, value}`), `change_abs`, `change_pct`, `trend` (`increasing` | `decreasing` | `flat` | `mixed`), `biggest_rise`, `biggest_drop` (each `{from, to, change}` or `null`), `total`, `shares` (`[{label, percent}]` for pie charts, else `null`).
- `text_source`: `llm` = written by the AI and every number checked against the data (online mode); `template` = basic summary built from the numbers (offline mode, or the AI failed the number check). Show this to the user as a badge.
- `extractor`: which reader produced the table: `vision` (Groq vision model, online) or `deplot` (DePlot on this computer, offline). Worth showing as a small label.
- `warnings[]`: show each `message` to the user (messages can be long; they explain what to check). Codes:
  - data problems: `parse_failed`, `missing_values`, `non_numeric`, `single_point`, `shares_not_100`
  - reading reliability: `complex_chart` (many series or points), `low_confidence` (table probably read sideways), `extraction_truncated` (chart too complex to finish reading), `dual_axis` (one series uses the right-hand scale), `values_estimated` (no printed numbers; values read from axes), `readings_disagree` (two independent readings differ; lists the values)
  - text: `llm_unavailable`, `llm_numbers_unverified`
- New codes may be added later; display any unknown code's `message` as-is.

## POST /api/ask

Answers a question about the analyzed chart. The backend stores nothing, so send the chart data from the analyze response back with every question.

Request: JSON

```json
{
  "question": "Which month had the biggest increase?",
  "title": "Monthly sales 2025",
  "chart_type": "bar",
  "table": { "columns": ["Month", "Sales"], "rows": [["Jan", 20], ["Feb", 25]] },
  "facts": { "series": [] },
  "history": [
    { "role": "user", "content": "What is the highest value?" },
    { "role": "assistant", "content": "May had the highest sales, 55." }
  ]
}
```

- `question`: 1–500 characters. `history`: the last 6 messages at most (older ones → 422).
- Pass `title`, `chart_type`, `table`, `facts` exactly as received from `/api/analyze`.

Response:

```json
{ "answer": "The biggest increase was from Apr to May, +17.", "on_topic": true }
```

`on_topic: false` means the question was unrelated to the chart; the answer politely says so. Offline, the answer explains that questions need internet.

## POST /api/compare

A generic AI description of the raw image (no ChartVoice processing), for the side-by-side comparison panel. Needs internet.

Request: `multipart/form-data` with `image` (same rules as analyze).

Response:

```json
{ "description": "The image shows a bar chart ...", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "timing_ms": 1400 }
```

Returns 503 with a clear `detail` when offline.
