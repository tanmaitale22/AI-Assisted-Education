import re


def normalize_text(text):
    """Lowercase and strip punctuation/extra whitespace for comparison."""
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def text_tokens(text):
    """Word set used for Jaccard similarity."""
    return set(normalize_text(text).split())


def jaccard_similarity(tokens_a, tokens_b):
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def is_near_duplicate(text_a, text_b, threshold=0.6):
    """
    Word-overlap similarity check.

    Unlike difflib.SequenceMatcher (which compares character sequences and
    is thrown off by reordered sentences or reworded phrasing), this
    compares the *set of words* used, which is much more robust for
    content that an LLM has regenerated/reworded from the same source
    material - the classic cause of near-duplicate chunks in this app.
    """
    return jaccard_similarity(text_tokens(text_a), text_tokens(text_b)) >= threshold


def dedupe_chunks(chunks, threshold=0.6, key=lambda c: c.get("content", "")):
    """
    Given a list of chunk dicts, return a new list with near-duplicates
    (by word-overlap similarity of `key(chunk)`) removed, keeping the
    first occurrence of each.
    """
    kept = []
    kept_tokens = []

    for chunk in chunks:
        content = key(chunk)

        if not content or not content.strip():
            continue

        tokens = text_tokens(content)

        if any(jaccard_similarity(tokens, existing) >= threshold for existing in kept_tokens):
            continue

        kept.append(chunk)
        kept_tokens.append(tokens)

    return kept
