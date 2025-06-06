# `theme_identifier.py`

This module extracts high-level themes from multiple document-specific answers using **Groq's LLM**. It helps summarize and group insights at a conceptual level after document-level question answering has been performed.

---

## Responsibilities

- Take in all per-document answers
- Construct a well-engineered prompt with guidance and formatting rules
- Call the **Groq LLM** (`llama-3.3-70b-versatile`) to:
  - Identify recurring themes
  - Include all relevant documents per theme
  - Format results clearly and consistently

---

## Function Overview

### `extract_themes(responses: List[Dict[str, str]]) -> str`

Given a list of `{"doc_id": ..., "answer": ...}` items:

1. Merges answers into a single prompt body
2. Instructs the LLM to group them by semantic similarity
3. Returns a **plain-text summary** with headers like:
Theme 1 - [Risk Management]:
Documents (Q1.pdf, Report.docx) discuss ...

---

## Prompt Design

The prompt:
- Ensures **all document IDs** are mentioned
- Requires a theme even for unique, unmatched answers
- Prohibits introductory phrases, bullet lists, JSON, or generalizations
- Allows multiple appearances of a document across themes

This makes the output highly structured and suitable for direct rendering in UI or reports.

---

## Example Response Snippet

Theme 1 - [Cost Reduction]:\
Documents (budget2023.pdf, operations.txt) propose new cost-saving measures...

Theme 2 - [AI Adoption]:\
Document (future_strategy.docx) highlights the increasing use of AI tools...

---

## Dependencies

- `Groq` – LLM client used to generate the response
- `GROQ_API_KEY` – loaded via `config.py`
- `logger` vis `logger.py` logs both successful and failed attempts

---

## Notes

- Document answers are truncated to 300 characters to fit context limits
- Handles any errors with a default fallback message
- Designed to be called after `extract_answers_from_docs()` in the pipeline

---

## Related Modules

- `query_engine.py` – provides the answer list used here
- `pipeline_routes.py` – calls this after document answers are collected
- `config.py` – provides API key and path settings









