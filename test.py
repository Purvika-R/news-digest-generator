import unittest
from datetime import datetime, timezone

from core.categories import match_score
from core.dedup import deduplicate, similarity
from core.digest import build_digest
from core.models import Article
from core.sources import load_sample, parse_feed
from core.summarizer import summarize
from utils.validators import parse_interests

RSS = """<?xml version="1.0"?><rss><channel>
<item><title>AI chip launched</title><link>https://a.test/1</link>
<description>&lt;p&gt;A new chip is out. It is fast.&lt;/p&gt;</description>
<pubDate>Sat, 24 Oct 2026 09:00:00 GMT</pubDate></item>
<item><title>Match ends in draw</title><link>https://a.test/2</link>
<description>Teams shared points.</description></item>
</channel></rss>"""

ATOM = """<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Vaccine trial results</title><link href="https://a.test/3"/>
<updated>2026-10-25T04:40:00Z</updated><summary>Trial shows strong results.</summary></entry>
</feed>"""


class SourceTests(unittest.TestCase):
    def test_parses_rss(self):
        arts = parse_feed(RSS, "Test")
        self.assertEqual(len(arts), 2)
        self.assertEqual(arts[0].published.year, 2026)
        self.assertEqual(arts[0].source, "Test")

    def test_parses_atom(self):
        arts = parse_feed(ATOM, "Test")
        self.assertEqual(arts[0].link, "https://a.test/3")
        self.assertIsNotNone(arts[0].published)

    def test_sample_loads(self):
        self.assertGreater(len(load_sample()), 5)


class SummarizerTests(unittest.TestCase):
    def test_strips_html_and_limits_sentences(self):
        out = summarize("<p>First sentence is here. Second sentence follows. Third one is extra.</p>")
        self.assertNotIn("<", out)
        self.assertIn("First sentence", out)
        self.assertNotIn("Third one", out)

    def test_limits_length(self):
        self.assertLessEqual(len(summarize("word " * 200 + ".", max_sentences=5, max_chars=50)), 53)


class DedupTests(unittest.TestCase):
    def test_similar_titles_are_similar(self):
        self.assertGreaterEqual(similarity("Storm hits coast, thousands evacuated",
                                           "Storm hits the coast and thousands are evacuated"), 0.5)

    def test_removes_repeats_keeps_first(self):
        arts = [Article(title="Storm hits coast, thousands evacuated", link="1"),
                Article(title="Storm hits the coast and thousands are evacuated", link="2"),
                Article(title="Markets rally after earnings", link="3")]
        self.assertEqual([a.link for a in deduplicate(arts)], ["1", "3"])


class DigestTests(unittest.TestCase):
    def setUp(self):
        self.articles = [
            Article(title="AI chip startup unveils processor", link="a", published=datetime(2026, 10, 25, tzinfo=timezone.utc)),
            Article(title="Mars water found by scientists", link="b", description="Research study", published=datetime(2026, 10, 24, tzinfo=timezone.utc)),
            Article(title="Cup final goes to extra time", link="c", description="team and coach"),
            Article(title="AI chip startup unveils processor again", link="d"),
        ]

    def test_respects_interests_and_limits(self):
        digest = build_digest(self.articles, ["Technology", "Science"], per_category=1)
        self.assertEqual(set(digest["sections"]), {"Technology", "Science"})
        self.assertEqual(len(digest["sections"]["Technology"]), 1)

    def test_story_appears_once(self):
        digest = build_digest(self.articles, ["Technology", "Sports", "Science"], per_category=5)
        titles = [it["title"] for items in digest["sections"].values() for it in items]
        self.assertEqual(len(titles), len(set(titles)))

    def test_reports_empty_interest(self):
        digest = build_digest(self.articles, ["Health"], per_category=3)
        self.assertEqual(digest["empty"], ["Health"])

    def test_requires_interest(self):
        with self.assertRaises(ValueError):
            build_digest(self.articles, [])

    def test_custom_interest_uses_its_name(self):
        self.assertGreater(match_score(Article(title="Cricket test match today"), "cricket"), 0)


class ValidatorTests(unittest.TestCase):
    def test_parse_interests_dedupes(self):
        self.assertEqual(parse_interests("AI, ai, Sports"), ["AI", "ai", "Sports"])

    def test_parse_interests_limit(self):
        with self.assertRaises(ValueError):
            parse_interests(", ".join(f"topic{i}" for i in range(9)))


if __name__ == "__main__":
    unittest.main()
