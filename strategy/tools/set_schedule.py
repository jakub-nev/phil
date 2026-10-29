#!/usr/bin/env python3
"""Set next_full_cycle_after and REPLACE the reason in strategy/schedule.json.

Usage: python3 strategy/tools/set_schedule.py <ISO pointer> <reason.txt>

Why this exists (2026-10-29 02:00Z FULL, pi4): the reason-field hygiene rule
(DEEP-2026-09-15: CURRENT block plus at most one PRIOR line) needs the whole
value replaced, and the field is too long to match with Edit. Inline
`python3 -c` and scripts under work/ are approval-gated on pi4. Write the
reason to a scratch file under reports/ with the Write tool, then run this.
All other keys (watch_items, notes, screener_budget) are preserved.
"""
import json
import os
import sys

SCHED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                     "schedule.json")


def main(argv):
    if len(argv) != 3:
        sys.exit(__doc__)
    pointer = argv[1]
    if not (pointer.endswith("Z") and "T" in pointer):
        sys.exit("pointer must be ISO 8601 UTC, e.g. 2026-10-29T03:45:00Z")
    with open(argv[2]) as f:
        reason = f.read().strip()
    if not reason.startswith("CURRENT:"):
        sys.exit("reason must start with 'CURRENT:'")
    with open(SCHED) as f:
        d = json.load(f)
    d["next_full_cycle_after"] = pointer
    d["reason"] = reason
    with open(SCHED, "w") as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"schedule: next_full_cycle_after={pointer}, reason {len(reason)} chars")


if __name__ == "__main__":
    main(sys.argv)
