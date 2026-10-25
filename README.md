# AI News Digest Generator

Builds a personalized daily digest from news feeds. Stories are grouped by the interests you choose, summarized briefly, and de-duplicated so the same event never appears twice.

Built with Python and Streamlit only.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Command line:

```bash
python main.py --interests "Technology, Science" --source sample
python main.py --interests "Sports, Health" --source live --out output
```

Tests:

```bash
python -m unittest test -v
```

## How it works

1. **Collect:** RSS or Atom feeds (live) or `data/sample_articles.json` (offline).
2. **De-duplicate:** titles or links that match closely are dropped, keeping the first one.
3. **Categorize:** each story goes to the single interest it matches best. Interests without a preset use their own name as the keyword.
4. **Summarize:** the first sentences of the article text, cleaned of HTML. Optionally AI-written with `ANTHROPIC_API_KEY`.

Edit `DEFAULT_FEEDS` in `core/sources.py` to change sources, and `CATEGORY_KEYWORDS` in `core/categories.py` to tune categories.

## Structure

```
app.py                 Streamlit UI
main.py                Command-line entry point
core/
  models.py            Article dataclass
  sources.py           RSS/Atom parsing, live fetching, sample loading
  summarizer.py        Extractive summaries
  dedup.py             Removes repeated stories
  categories.py        Interest keywords and matching
  digest.py            Builds the final digest
  llm.py               Optional AI summaries with fallback
utils/
  validators.py        Input parsing
  formatters.py        Markdown and JSON export
data/sample_articles.json
test.py
```
