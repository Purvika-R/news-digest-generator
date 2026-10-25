"""Maps interests to keywords. Interests without a preset use their own name as the keyword."""
import re

CATEGORY_KEYWORDS = {
    "Technology": ["technology", "ai", "software", "chip", "startup", "cyber", "robot", "computing", "app"],
    "Science": ["science", "space", "climate", "research", "study", "scientist", "physics", "species"],
    "Business": ["business", "market", "economy", "stock", "company", "inflation", "bank", "trade"],
    "Sports": ["sport", "match", "cup", "league", "team", "coach", "tournament", "player"],
    "World": ["war", "election", "government", "minister", "summit", "talks", "president", "treaty"],
    "Health": ["health", "disease", "vaccine", "hospital", "medical", "patients", "drug", "doctor"],
}


def keywords_for(interest):
    return CATEGORY_KEYWORDS.get(interest, [interest.lower()])


def match_score(article, interest):
    text = f"{article.title} {article.description}".lower()
    return sum(1 for kw in keywords_for(interest) if re.search(rf"\b{re.escape(kw)}s?\b", text))
