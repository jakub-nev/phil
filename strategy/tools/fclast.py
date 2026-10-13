#!/usr/bin/env python3
"""Print the latest forecast row per market id from journal/forecasts.jsonl.

Usage: python3 strategy/tools/fclast.py <market_id> [<market_id> ...]

Why this exists (2026-10-13 01:0xZ FULL, pi4): collect's top divergences
are mostly repeats of markets that already carry an open researched
forecast, and the pi4 sandbox refuses inline `python3 -c`, shell loops and
scripts outside the repo, so checking "do I already have a live row here"
for a 15-market shortlist was an approval-gated call each time. One line
per id: row count, latest ts, outcome, est_prob, skip_reason, id, settled
flag, first 140 chars of the note. "NONE" means no forecast was ever
recorded on that market.
"""
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")


def main(ids):
    rows = {}
    with open(os.path.join(ROOT, "journal", "forecasts.jsonl")) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            m = str(d.get("market_id"))
            if m in ids:
                rows.setdefault(m, []).append(d)
    for m in ids:
        rs = rows.get(m)
        if not rs:
            print(m, "NONE")
            continue
        d = rs[-1]
        ts = str(d.get("ts") or d.get("recorded_at") or "")[:16]
        settled = d.get("settled", d.get("status", ""))
        note = (d.get("note") or "")[:140]
        print(m, len(rs), ts, d.get("outcome"), d.get("est_prob"),
              d.get("skip_reason"), d.get("id"), settled, note)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
