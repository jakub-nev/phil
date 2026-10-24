"""Split a category's settled-forecast brier_delta into empty-book rows
(bid/ask spread > 0.5 at record, so the mid is a placeholder) and the rest.

Usage: python3 strategy/tools/emptybook_split.py [category]
Added RETRO-20261024-2200: LA rain 8d2dbe8ca622 scored dB -0.23 against a
0.48 mid on a 0.004/0.958 book -- credit no tradable price ever offered.
"""
import json
import sys

cat = sys.argv[1] if len(sys.argv) > 1 else "weather"
rows = {"empty": [], "real": []}
for line in open("journal/forecasts.jsonl"):
    r = json.loads(line)
    if r.get("category") != cat or r.get("status") not in ("won", "lost"):
        continue
    m = r.get("market_prob_at_record")
    if m is None:
        continue
    y = 1 if r["status"] == "won" else 0
    d = (r["est_prob"] - y) ** 2 - (m - y) ** 2
    b, a = r.get("best_bid_at_record"), r.get("best_ask_at_record")
    key = "empty" if b is not None and a is not None and a - b > 0.5 else "real"
    rows[key].append(d)
for k, v in rows.items():
    mean = sum(v) / len(v) if v else float("nan")
    print(f"{cat} {k}-book: n={len(v)} brier_delta={mean:+.4f}")
