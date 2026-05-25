import json
import math
import re
from collections import Counter

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "this", "these", "those",
    "their", "there", "them", "they", "but", "or", "not", "so", "if",
    "then", "than", "when", "which", "what", "who", "whom", "where",
    "why", "how", "into", "over", "after", "before", "during", "within"
}

POSITIVE_WORDS = {
    "positive", "improve", "success", "benefit", "effective", "growth",
    "support", "better", "gain", "enhance", "strong", "good", "help"
}

NEGATIVE_WORDS = {
    "negative", "decline", "risk", "problem", "fail", "loss", "weak",
    "worse", "harm", "issue", "damage", "challenge"
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def split_sentences(text: str) -> list[str]:
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence.strip() for sentence in raw if sentence.strip()]


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[A-Za-z']+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def sentence_score(sentence: str, freq: Counter[str]) -> int:
    return sum(freq[word] for word in tokenize(sentence))


def summarize_text(text: str, length: str = "medium") -> str:
    text = normalize_text(text)
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return text

    tokens = tokenize(text)
    if not tokens:
        return sentences[0]

    freq = Counter(tokens)
    ratio = {
        "short": 0.15,
        "medium": 0.25,
        "detailed": 0.45,
    }.get(length.lower(), 0.25)

    summary_count = max(1, math.ceil(len(sentences) * ratio))
    ranked = sorted(sentences, key=lambda s: sentence_score(s, freq), reverse=True)
    selected = sorted(ranked[:summary_count], key=lambda s: sentences.index(s))
    return " ".join(selected)


def extract_keywords(text: str, limit: int = 6) -> list[str]:
    tokens = tokenize(text)
    most_common = Counter(tokens).most_common(limit)
    return [word for word, _ in most_common]


def detect_sentiment(text: str) -> str:
    tokens = tokenize(text)
    positive_count = sum(1 for token in tokens if token in POSITIVE_WORDS)
    negative_count = sum(1 for token in tokens if token in NEGATIVE_WORDS)
    if positive_count > negative_count:
        return "Positive"
    if negative_count > positive_count:
        return "Negative"
    return "Neutral"


def estimate_reading_time(text: str, wpm: int = 200) -> str:
    words = len(re.findall(r"\w+", text))
    minutes = max(1, math.ceil(words / wpm))
    return f"{minutes} minutes"


def build_summary_response(
    text: str,
    length: str = "medium",
    style: str = "paragraph",
) -> dict[str, object]:
    text = normalize_text(text)
    sentences = split_sentences(text)
    summary = summarize_text(text, length)
    keywords = extract_keywords(text, limit=5)
    sentiment = detect_sentiment(text)
    original_time = estimate_reading_time(text)
    summary_time = estimate_reading_time(summary)

    title = sentences[0] if sentences else "Summary"
    main_topic = keywords[0].title() if keywords else "General"

    return {
        "title": title,
        "main_topic": main_topic,
        "summary": summary,
        "key_points": keywords[:4],
        "keywords": keywords,
        "sentiment": sentiment,
        "reading_time": {
            "original": original_time,
            "summary": summary_time,
        },
    }


def format_output(response: dict[str, object], style: str = "paragraph") -> str:
    if style.lower() == "bullet points":
        lines = [f"Title: {response['title']}", f"Main Topic: {response['main_topic']}", "Summary:"]
        lines.extend([f"- {line}" for line in response["summary"].split(". ") if line])
        lines.append("Key Points:")
        lines.extend([f"- {point}" for point in response["key_points"]])
        lines.append(f"Keywords: {', '.join(response['keywords'])}")
        lines.append(f"Sentiment: {response['sentiment']}")
        lines.append("Reading Time:")
        lines.append(f"- Original: {response['reading_time']['original']}")
        lines.append(f"- Summary: {response['reading_time']['summary']}")
        return "\n".join(lines)

    return json.dumps(response, indent=3)
