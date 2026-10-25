"""Extractive summaries: keep the first sentences of the article text, cleaned of HTML."""
import html
import re


def clean_text(raw):
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def summarize(text, max_sentences=2, max_chars=300):
    sentences = re.split(r"(?<=[.!?])\s+", clean_text(text))
    picked = [s for s in sentences if len(s) > 20][:max_sentences]
    out = " ".join(picked)
    if len(out) > max_chars:
        out = out[:max_chars].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return out
