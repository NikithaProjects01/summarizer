import json
from typing import Any

from content_summarizer.summarizer import build_summary_response


def decode_uploaded_file(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="replace")


def generate_summary(text: str, length: str = "medium", style: str = "paragraph") -> dict[str, Any]:
    clean_text = text.strip()
    if not clean_text:
        raise ValueError("Please enter text or upload a file.")

    return build_summary_response(clean_text, length=length, style=style)


def format_summary_as_json(result: dict[str, Any]) -> str:
    return json.dumps(result, indent=2)


def format_summary_as_text(result: dict[str, Any]) -> str:
    lines = [
        f"Title: {result['title']}",
        f"Main Topic: {result['main_topic']}",
        f"Sentiment: {result['sentiment']}",
        "",
        "Summary:",
        str(result["summary"]),
        "",
        "Key Points:",
    ]
    lines.extend(f"- {point}" for point in result["key_points"])
    lines.extend(
        [
            "",
            f"Keywords: {', '.join(result['keywords'])}",
            "",
            "Reading Time:",
            f"- Original: {result['reading_time']['original']}",
            f"- Summary: {result['reading_time']['summary']}",
        ]
    )
    return "\n".join(lines)
