import re
from collections import Counter

STOPWORDS={"the","a","an","and","or","of","to","in","on","for","is","are","with"}

def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text.lower()).strip()
    return re.sub(r"[^a-z0-9\s.,!?-]", "", text)

def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", normalize_text(text)) if t not in STOPWORDS]

def keyword_risk_score(text: str, keywords: tuple[str,...]=("fraud","breach","outage","attack","loss","incident")) -> float:
    tokens=tokenize(text)
    if not tokens: return 0.0
    counts=Counter(tokens)
    hits=sum(counts[k] for k in keywords)
    return min(1.0, hits / max(3.0, len(tokens) * 0.08))
