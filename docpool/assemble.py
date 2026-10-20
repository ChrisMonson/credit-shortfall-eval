"""Assembles the pinned pool of synthetic documents from hand-written drafts.

    python -m docpool.assemble

The pool was planned by generate.plan() but written by hand rather than through
the Batches API, one draft per plan item in drafts/<id>.json with the shape
{"title": ..., "text": ...}. This reads the drafts in plan order, screens each
with the same screen() the generator would have used, names them with
filename(), and writes the first POOL_SIZE that pass to documents.json.

Rejections are printed with their reasons so the draft can be rewritten rather
than skipped: the pool should stay close to the plan.
"""

import json
import sys

from docpool.generate import HERE, OUTPUT_FILE, POOL_SIZE, REQUESTED, SEED, filename, plan, screen

DRAFTS_DIR = HERE / "drafts"


def main() -> None:
    kept: list[tuple[str, str]] = []
    rejected: dict[str, str] = {}
    for item in plan(REQUESTED, SEED):
        if len(kept) == POOL_SIZE:
            break  # the remaining plan items are spares and need no draft
        path = DRAFTS_DIR / f"{item['id']}.json"
        if not path.exists():
            rejected[item["id"]] = "no draft"
            continue
        document = json.loads(path.read_text())
        if reason := screen(document["text"]):
            rejected[item["id"]] = reason
            continue
        kept.append((filename(document["title"]), document["text"]))

    # Same naming as collect(): a repeated title gets _2 so every name in the pool is distinct.
    pool, names = [], set()
    for name, text in kept[:POOL_SIZE]:
        while name in names:
            name = name.removesuffix(".txt") + "_2.txt"
        names.add(name)
        pool.append({"name": name, "text": text})

    OUTPUT_FILE.write_text(json.dumps(pool, indent=2, ensure_ascii=False) + "\n")
    print(f"Kept {len(pool)} of {REQUESTED} ({len(kept)} passed screening).")
    for custom_id, reason in sorted(rejected.items()):
        print(f"  rejected {custom_id}: {reason}")
    if len(pool) < POOL_SIZE:
        sys.exit(f"Short of {POOL_SIZE}: rewrite the rejected drafts or write the spare plan items.")


if __name__ == "__main__":
    main()
