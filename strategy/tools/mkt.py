#!/usr/bin/env python3
"""Print a one-screen summary of gamma markets for research.

Usage: python3 strategy/tools/mkt.py <market_id> [<market_id> ...] [--desc N]

Why this exists (2026-10-12 00:0xZ FULL, pi4): the pi4 sandbox refuses
inline `python3 -c` and shell loops, so pulling question / endDate / book /
resolution rules for a screener shortlist took one approval-gated call per
market. This prints, per id: question, endDate, outcomes with mids, gamma
bestBid/bestAsk, liquidity, closed / UMA status, and the first N chars of
the resolution description (default 900).
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", ".."))
from core.pmapi import gamma_market  # noqa: E402


def main(argv):
    n = 900
    ids = []
    i = 0
    while i < len(argv):
        if argv[i] == "--desc":
            n = int(argv[i + 1])
            i += 2
            continue
        ids.append(argv[i])
        i += 1
    for mid in ids:
        try:
            m = gamma_market(mid)
        except Exception as e:  # network or unknown id
            print(f"{mid}: ERROR {e}")
            continue
        if isinstance(m, list):
            m = m[0] if m else {}
        outs = m.get("outcomes")
        prices = m.get("outcomePrices")
        try:
            outs = json.loads(outs) if isinstance(outs, str) else outs
            prices = json.loads(prices) if isinstance(prices, str) else prices
        except ValueError:
            pass
        print(f"== {m.get('id')} {m.get('question')}")
        print(f"   end {m.get('endDate')} closed={m.get('closed')} "
              f"uma={m.get('umaResolutionStatus')} liq={m.get('liquidityNum')}"
              f" vol24={m.get('volume24hr')}")
        print(f"   outcomes {outs} prices {prices} "
              f"bid/ask {m.get('bestBid')}/{m.get('bestAsk')}")
        toks = m.get("clobTokenIds")
        try:
            toks = json.loads(toks) if isinstance(toks, str) else toks
        except ValueError:
            pass
        # token ids feed strategy/tools/quote.py (added 2026-10-13 09:2xZ)
        print(f"   tokens {dict(zip(outs or [], toks or []))}")
        ev = (m.get("events") or [{}])[0]
        print(f"   event {ev.get('id')} {ev.get('title')}")
        desc = (m.get("description") or "").replace("\n", " ")
        print(f"   DESC: {desc[:n]}")


if __name__ == "__main__":
    main(sys.argv[1:])
