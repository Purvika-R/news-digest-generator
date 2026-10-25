"""Removes stories that cover the same event, so the digest does not repeat itself."""
import re

STOP_WORDS = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "with", "at", "as",
              "is", "are", "by", "from", "after", "over", "new", "its", "be", "has", "have"}


def tokens(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP_WORDS and len(w) > 2}


def similarity(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def deduplicate(articles, threshold=0.5):
    """Keeps the first article of each group of near-identical titles or links."""
    kept = []
    for art in articles:
        duplicate = any(
            (art.link and art.link == k.link) or similarity(art.title, k.title) >= threshold
            for k in kept
        )
        if not duplicate:
            kept.append(art)
    return kept
