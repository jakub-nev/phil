"""List scan candidates ending within N hours, soonest first.

Unscreened-selection fallback for FULL cycles that run after the daily
screener quota is spent (2026-10-11 21:00Z: day 150/150, and ad-hoc scripts
under work/ are not on the pi4 runner's allowlist, while strategy/tools/ is).

Usage: python3 strategy/tools/unscreened.py work/scan.json [hours] [min_liq]
"""
import json
import sys
from datetime import datetime, timezone, timedelta


def main():
    c = [json.loads(ln) for ln in open(sys.argv[1]) if ln.strip()]  # scan.py emits JSONL
    hrs = float(sys.argv[2]) if len(sys.argv) > 2 else 30
    min_liq = float(sys.argv[3]) if len(sys.argv) > 3 else 0
    now = datetime.now(timezone.utc)
    if c:
        print(len(c), "candidates; keys:", sorted(c[0].keys()))
    rows = []
    for m in c:
        end = m.get("end_date") or m.get("endDate") or ""
        try:
            e = datetime.fromisoformat(end.replace("Z", "+00:00"))
        except ValueError:
            continue
        if e < now or e - now > timedelta(hours=hrs):
            continue
        if float(m.get("liquidity") or 0) < min_liq:
            continue
        rows.append((e, m))
    rows.sort(key=lambda r: r[0])
    for e, m in rows:
        print(e.strftime("%m-%dT%H:%MZ"), m.get("id") or m.get("market_id"),
              round(float(m.get("liquidity") or 0)),
              m.get("outcomes"), m.get("outcome_prices"),
              (m.get("question") or "")[:90])


if __name__ == "__main__":
    main()
