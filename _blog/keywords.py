#!/usr/bin/env python3
"""Pull real search phrasings from Google autocomplete.

    python3 _blog/keywords.py canada            # all Canada seeds
    python3 _blog/keywords.py walkfirst
    python3 _blog/keywords.py --seed "citizenship oath" --gl ca

For each seed it asks Google for completions of the seed itself, the seed
followed by each letter a-z, and question forms ("how <seed>", "can <seed>",
...). A phrase that comes back for many of those prompts, and near the top,
is one people type a lot. Output is a tab-separated list, best first:
score, number of prompts it appeared for, phrase.

Autocomplete has no search volumes. It tells you what people type and in
which words, not how many of them. Use it to pick topics and phrase titles,
then check Search Console once pages are live.
"""
import json
import string
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict

SEEDS = {
    "canada": ("ca", [
        "canadian citizenship test", "citizenship test canada", "discover canada",
        "canadian citizenship", "citizenship ceremony canada", "citizenship oath canada",
        "citizenship interview canada", "citizenship hearing canada",
    ]),
    "walkfirst": ("us", [
        "walking", "walking after eating", "steps a day", "walking for weight loss",
        "screen time", "phone addiction", "stop scrolling", "app blocker",
    ]),
}
QUESTIONS = ["how", "what", "when", "can", "is", "do", "why", "does"]


def suggest(q, gl):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "hl": "en", "gl": gl, "q": q})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                return json.loads(r.read().decode("utf-8", "replace"))[1]
        except Exception:
            time.sleep(1 + attempt)
    return []


def expand(seed, gl, scores, hits):
    prompts = [seed] + [f"{seed} {c}" for c in string.ascii_lowercase] + [f"{w} {seed}" for w in QUESTIONS]
    for p in prompts:
        for rank, phrase in enumerate(suggest(p, gl)):
            scores[phrase] += 10 - min(rank, 9)
            hits[phrase] += 1
        time.sleep(0.15)


def main():
    args = sys.argv[1:]
    if "--seed" in args:
        seeds = [args[args.index("--seed") + 1]]
        gl = args[args.index("--gl") + 1] if "--gl" in args else "us"
    else:
        gl, seeds = SEEDS[args[0]]
    scores, hits = defaultdict(int), defaultdict(int)
    for s in seeds:
        expand(s, gl, scores, hits)
    for phrase in sorted(scores, key=lambda k: (-scores[k], k)):
        print(f"{scores[phrase]}\t{hits[phrase]}\t{phrase}")


if __name__ == "__main__":
    main()
