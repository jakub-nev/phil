#!/usr/bin/env python3
"""Print forecast rows settled at or after a UTC timestamp prefix.

Usage: python3 strategy/tools/settled.py <settled_ts prefix, e.g. 2026-10-13T08>

Why this exists (2026-10-13 09:0xZ FULL, pi4): a retro must grade every
forecast resolve.py settled this tick, but resolve.py prints only the
question text, and the pi4 sandbox refuses inline `python3 -c`, so pulling
the rows (id, market, est, mid at record, skip reason, note) was an
approval-gated call. One line per row plus own/market brier and
dBrier (= market brier - own brier; positive means we beat the mid).
"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def main(prefix):
    tot = 0.0
    n = 0
    with open(os.path.join(ROOT, "journal", "forecasts.jsonl")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            ts = d.get("settled_ts") or ""
            if not ts or ts < prefix:
                continue
            won = d.get("outcome_won")
            y = 1.0 if won == d.get("outcome") else 0.0
            if "won" in d and isinstance(d["won"], bool):
                y = 1.0 if d["won"] else 0.0
            elif d.get("status") in ("won", "lost"):
                y = 1.0 if d["status"] == "won" else 0.0
            p = float(d.get("est_prob"))
            mid = d.get("market_prob_at_record")
            line_out = "%s %s mkt=%s %r est=%.3f mid=%s %s y=%d" % (
                d.get("id"), (d.get("ts") or "")[:16], d.get("market_id"),
                d.get("outcome"), p, mid, d.get("skip_reason"), int(y))
            if mid is not None:
                db = (float(mid) - y) ** 2 - (p - y) ** 2
                tot += db
                n += 1
                line_out += " dB=%+.4f" % db
            print(line_out + " | " + (d.get("note") or "")[:300])
    print("rows=%d sum_dBrier(mkt-own)=%+.4f" % (n, tot))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
