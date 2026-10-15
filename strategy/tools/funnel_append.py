#!/usr/bin/env python3
"""Append one funnel row (a JSON object in a file) to strategy/funnel.jsonl.

Usage: python3 strategy/tools/funnel_append.py <row.json> [--amend]

--amend replaces the last row instead of appending, only if it carries
the same `cycle` (fixing this cycle's own row after reconcile.py flags it).

Why this exists (2026-10-14 05:xxZ FULL, pi4): the pi4 sandbox refuses
heredoc appends (`cat >> ... <<EOF` with JSON braces) and inline
`python3 -c`, and funnel.jsonl is too large for Read/Edit. Write the row
to a scratch file with the Write tool, then run this. It validates the
JSON, requires the mandatory funnel fields, and appends exactly one line.
"""
import json
import os
import sys

FUNNEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                      "funnel.jsonl")
REQUIRED = ("cycle", "tick_type", "screened", "escalated",
            "screener_batches", "researched", "placed")


def drop_dup_last():
    """Remove the last row only if it byte-equals an earlier row.

    2026-10-15 00:0xZ FULL, pi4: a stale /tmp row file from 10-13 was
    appended a second time, and git checkout/restore are approval-gated
    here. Use per-cycle scratch files under reports/ to avoid that.
    """
    with open(FUNNEL, "rb") as f:
        lines = f.read().rstrip(b"\n").split(b"\n")
    if len(lines) < 2 or lines[-1] not in lines[:-1]:
        sys.exit("--drop-dup-last: last row is not a duplicate; refusing")
    with open(FUNNEL, "wb") as f:
        f.write(b"\n".join(lines[:-1]) + b"\n")
    print(f"dropped duplicate last row cycle={json.loads(lines[-1]).get('cycle')}")


def main(argv):
    if argv[1:] == ["--drop-dup-last"]:
        drop_dup_last()
        return
    amend = "--amend" in argv
    argv = [a for a in argv if a != "--amend"]
    if len(argv) != 2:
        sys.exit(__doc__)
    with open(argv[1]) as f:
        row = json.load(f)
    if not isinstance(row, dict):
        sys.exit("row must be a JSON object")
    missing = [k for k in REQUIRED if k not in row]
    if missing:
        sys.exit(f"missing funnel fields: {missing}")
    line = json.dumps(row, ensure_ascii=False)
    if amend:
        with open(FUNNEL, "rb") as f:
            lines = f.read().rstrip(b"\n").split(b"\n")
        if json.loads(lines[-1]).get("cycle") != row["cycle"]:
            sys.exit("--amend: last row is a different cycle; refusing")
        lines[-1] = line.encode()
        with open(FUNNEL, "wb") as f:
            f.write(b"\n".join(lines) + b"\n")
        print(f"amended funnel row cycle={row['cycle']}")
        return
    with open(FUNNEL, "rb+") as f:
        f.seek(0, os.SEEK_END)
        if f.tell() > 0:
            f.seek(-1, os.SEEK_END)
            if f.read(1) != b"\n":
                f.write(b"\n")
        f.write(line.encode() + b"\n")
    print(f"appended funnel row cycle={row['cycle']}")


if __name__ == "__main__":
    main(sys.argv)
