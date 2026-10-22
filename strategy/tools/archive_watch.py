"""Move one watch item from strategy/schedule.json to strategy/watch-archive.jsonl.

Usage: archive_watch.py <item prefix> <archived_by> <reason>
The prefix must match exactly one item (DEEP-2026-10-02 archive rule).
"""
import json
import sys

SCHED = 'strategy/schedule.json'
ARCHIVE = 'strategy/watch-archive.jsonl'


def main():
    prefix, archived_by, reason = sys.argv[1:4]
    d = json.load(open(SCHED))
    hits = [i for i in d['watch_items'] if i.startswith(prefix)]
    if len(hits) != 1:
        sys.exit(f"prefix matched {len(hits)} items, need exactly 1")
    d['watch_items'] = [i for i in d['watch_items'] if i is not hits[0]]
    with open(ARCHIVE, 'a') as f:
        f.write(json.dumps({"item": hits[0], "archived_by": archived_by, "reason": reason}) + "\n")
    with open(SCHED, 'w') as f:
        json.dump(d, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"archived 1 item, {len(d['watch_items'])} remain")


if __name__ == '__main__':
    main()
