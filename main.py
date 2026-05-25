import argparse
import json
from pathlib import Path

from content_summarizer.summarizer import build_summary_response


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize long-form content and produce structured output."
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Path to a text file with content to summarize.",
    )
    parser.add_argument(
        "--text",
        type=str,
        help="Use a short text string directly for summarization.",
    )
    parser.add_argument(
        "--length",
        choices=["short", "medium", "detailed"],
        default="medium",
        help="Desired summary length.",
    )
    parser.add_argument(
        "--style",
        choices=["paragraph", "bullet points"],
        default="paragraph",
        help="Output style for the summary.",
    )
    return parser.parse_args()


def decode_bytes(data: bytes) -> str:
    # Attempt multiple encodings in sequence
    for encoding in ('utf-8-sig', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1'):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    # Ultimate fallback with character replacement
    return data.decode('utf-8', errors='replace')


def load_text_from_file(path: Path) -> str:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")
    return decode_bytes(path.read_bytes())


def main() -> None:
    args = parse_args()
    if args.file:
        content = load_text_from_file(args.file)
    elif args.text:
        content = args.text
    else:
        raise SystemExit("Provide input text with --file or --text.")

    response = build_summary_response(content, length=args.length, style=args.style)
    print(json.dumps(response, indent=3))


if __name__ == "__main__":
    main()
