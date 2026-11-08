"""A report card for your project.   Run with:  python -m eval.run_eval

For each test question it checks:
  1. Did search bring back the RIGHT file?              (retrieval hit)
  2. For off-topic questions, did we correctly refuse?   (refusal check)
Add --with-llm to also run the full pipeline (uses your free API quota).

Edit eval/questions.json to match YOUR data, then re-run after every change you
make (chunk size, MAX_DISTANCE, ...) and note the score. Those before/after
numbers are great for your README.
"""
import argparse
import json
from pathlib import Path

from src.config import MAX_DISTANCE
from src.retrieve import search

QUESTIONS = Path(__file__).parent / "questions.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-llm", action="store_true", help="also test full answers")
    args = ap.parse_args()

    tests = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    passed = 0
    for t in tests:
        chunks = search(t["question"])
        best = chunks[0]["distance"] if chunks else 9
        if t.get("should_refuse"):
            ok = best > MAX_DISTANCE
            detail = f"best distance {best:.2f} (should be > {MAX_DISTANCE})"
        else:
            ok = any(c["source"] == t["expected_source"] for c in chunks)
            detail = f"wanted {t['expected_source']}, got {[c['source'] for c in chunks]}"
        passed += ok
        print(("PASS" if ok else "FAIL"), "|", t["question"], "\n      ", detail)

        if args.with_llm:
            from src.llm import answer_question
            ans, _ = answer_question(t["question"])
            print("      answer:", ans[:200].replace("\n", " "))

    print(f"\nScore: {passed}/{len(tests)}")


if __name__ == "__main__":
    main()
