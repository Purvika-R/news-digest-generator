"""Optional AI summaries. Returns None on any problem so the extractive summary is used instead."""
import os

DEFAULT_MODEL = "claude-haiku-4-5"


def llm_available():
    if not os.getenv("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def summarize_with_ai(article):
    if not llm_available():
        return None
    try:
        import anthropic
        client = anthropic.Anthropic()
        prompt = (
            "Summarize this news item in at most two sentences. Use only facts stated in the text. "
            f"Title: {article.title}\nText: {article.description}\n\nReturn only the summary."
        )
        msg = client.messages.create(
            model=os.getenv("NEWS_LLM_MODEL", DEFAULT_MODEL),
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()
    except Exception:
        return None
    if not text or len(text) > 400:
        return None
    return text
