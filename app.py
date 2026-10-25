from datetime import datetime

import streamlit as st

from core.categories import CATEGORY_KEYWORDS
from core.digest import build_digest
from core.llm import llm_available, summarize_with_ai
from core.sources import DEFAULT_FEEDS, fetch_feed, load_sample
from utils.formatters import to_json, to_markdown
from utils.validators import parse_interests

st.set_page_config(page_title="News Digest", layout="wide")
st.title("AI News Digest")
st.caption("Pick your interests and get a short digest with no repeated stories.")

with st.sidebar:
    st.header("Settings")
    source = st.radio("Source", ["Live RSS feeds", "Sample articles (offline)"])
    live = source.startswith("Live")
    feed_names = st.multiselect("Feeds", list(DEFAULT_FEEDS), default=list(DEFAULT_FEEDS), disabled=not live)
    preset = st.multiselect("Interests", list(CATEGORY_KEYWORDS), default=["Technology", "Science"])
    custom = st.text_input("Other interests", placeholder="cricket, electric vehicles")
    per_category = st.slider("Stories per interest", 1, 5, 3)
    use_ai = st.checkbox("AI summaries", disabled=not llm_available())
    build = st.button("Build digest", type="primary", use_container_width=True)

if build:
    try:
        interests = list(dict.fromkeys(preset + parse_interests(custom)))
        if not interests:
            raise ValueError("Choose at least one interest.")
        if live and not feed_names:
            raise ValueError("Select at least one feed.")
    except ValueError as exc:
        st.error(str(exc))
    else:
        failed = []
        with st.spinner("Collecting stories..."):
            if live:
                articles = []
                for name in feed_names:
                    try:
                        articles += fetch_feed(DEFAULT_FEEDS[name], name)
                    except Exception as exc:
                        failed.append(f"{name}: {exc}")
            else:
                articles = load_sample()
        digest = build_digest(articles, interests, per_category,
                              summarize_with_ai if use_ai else None)
        digest["failed"] = failed
        st.session_state["digest"] = digest

digest = st.session_state.get("digest")
if digest:
    for problem in digest.get("failed", []):
        st.warning(f"Could not load {problem}")
    stats = digest["stats"]
    st.caption(f"{stats['collected']} stories collected, {stats['unique']} after removing repeats, "
               f"{stats['included']} shown.")

    for interest, items in digest["sections"].items():
        st.header(interest)
        for it in items:
            st.markdown(f"**[{it['title']}]({it['link']})**")
            meta = " · ".join(x for x in [it["source"], it["published"][:16].replace("T", " ")] if x)
            if meta:
                st.caption(meta)
            st.write(it["summary"])
    if digest["empty"]:
        st.info("No stories matched: " + ", ".join(digest["empty"]))

    st.divider()
    c1, c2 = st.columns(2)
    c1.download_button("Download Markdown", to_markdown(digest), file_name="digest.md")
    c2.download_button("Download JSON", to_json(digest), file_name="digest.json")
