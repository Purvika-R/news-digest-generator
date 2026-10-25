"""Builds the digest: de-duplicate, assign each story to its best interest, summarize, and cap sizes."""
from datetime import datetime, timezone

from .categories import match_score
from .dedup import deduplicate
from .summarizer import summarize

MIN_DATE = datetime.min.replace(tzinfo=timezone.utc)


def build_digest(articles, interests, per_category=3, summarizer=None):
    """
    summarizer: optional function(article) -> str or None, used for AI summaries.
    Falls back to the extractive summary when it returns nothing.
    """
    if not interests:
        raise ValueError("Choose at least one interest.")

    unique = deduplicate(articles)
    buckets = {interest: [] for interest in interests}
    for art in unique:
        best, best_score = None, 0
        for interest in interests:
            score = match_score(art, interest)
            if score > best_score:
                best, best_score = interest, score
        if best:  # each story lands in one section only, so nothing repeats across sections
            buckets[best].append(art)

    sections, empty = {}, []
    for interest in interests:
        ranked = sorted(buckets[interest], key=lambda a: a.published or MIN_DATE, reverse=True)
        items = []
        for art in ranked[:per_category]:
            ai_text = summarizer(art) if summarizer else None
            items.append({
                "title": art.title,
                "link": art.link,
                "source": art.source,
                "published": art.published.isoformat() if art.published else "",
                "summary": ai_text or summarize(art.description) or art.title,
            })
        if items:
            sections[interest] = items
        else:
            empty.append(interest)

    return {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "sections": sections,
        "empty": empty,
        "stats": {"collected": len(articles), "unique": len(unique),
                  "included": sum(len(v) for v in sections.values())},
    }
