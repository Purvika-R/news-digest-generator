"""Command-line entry point.
Examples:
  python main.py --interests "Technology, Science" --source sample
  python main.py --interests "Sports, Health" --source live --out output
"""
import argparse
import os

from core.categories import CATEGORY_KEYWORDS
from core.digest import build_digest
from core.llm import summarize_with_ai, llm_available
from core.sources import DEFAULT_FEEDS, fetch_feed, load_sample
from utils.formatters import to_json, to_markdown
from utils.validators import parse_interests


def main():
    parser = argparse.ArgumentParser(description="Build a personalized news digest.")
    parser.add_argument("--interests", default="Technology, Science", help="Comma-separated interests")
    parser.add_argument("--source", choices=["sample", "live"], default="sample")
    parser.add_argument("--per-category", type=int, default=3)
    parser.add_argument("--ai", action="store_true", help="Use AI summaries (needs ANTHROPIC_API_KEY)")
    parser.add_argument("--out", default="output")
    args = parser.parse_args()

    interests = parse_interests(args.interests)
    if args.source == "live":
        articles = []
        for name, url in DEFAULT_FEEDS.items():
            try:
                articles += fetch_feed(url, name)
            except Exception as exc:
                print(f"Skipped {name}: {exc}")
    else:
        articles = load_sample()

    summarizer = summarize_with_ai if args.ai and llm_available() else None
    digest = build_digest(articles, interests, args.per_category, summarizer)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "digest.md"), "w", encoding="utf-8") as f:
        f.write(to_markdown(digest))
    with open(os.path.join(args.out, "digest.json"), "w", encoding="utf-8") as f:
        f.write(to_json(digest))

    print(to_markdown(digest))
    print(f"Saved to {args.out}/digest.md and digest.json")


if __name__ == "__main__":
    main()
