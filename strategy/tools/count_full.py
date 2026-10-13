#!/usr/bin/env python3
"""Count FULL (or TRIGGERED-without-LIGHT) cycle.log lines in the last 24h.

Mirrors the COUNT COMMAND v5 awk one-liner pinned in strategy/schedule.json's
"notes" field: for each cycle-done line timestamped within the last 24h,
classify by whichever marker — "FULL" or "LIGHT" — appears first in the line.
"""
import datetime as dt
import sys

LOG = "journal/cycles.log"


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(hours=24)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M")
    n = 0
    with open(LOG) as f:
        for line in f:
            if "Z cycle done" not in line[:40]:
                continue
            ts = line[:16]
            if ts <= cutoff_str:
                continue
            i = line.find("FULL")
            j = line.find("LIGHT")
            if i != -1 and (j == -1 or i < j):
                n += 1
    print(n)


if __name__ == "__main__":
    sys.exit(main())
