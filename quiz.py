"""CLI Quiz Application.

Loads questions from a JSON file, asks them in random order, accepts and
validates answers, calculates the score, and shows a final result summary.

Questions live in questions.json, separate from this program's logic, so new
questions can be added without touching any code.

Usage:
    python quiz_app.py [--file questions.json] [--count N] [--seed N]
"""
import argparse
import json
import os
import random
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FILE = os.path.join(BASE_DIR, "questions.json")
DEFAULT_COUNT = 10
LETTERS = "ABCDEF"
QUIT = "QUIT"

# (minimum percentage, message), checked from the top
RATINGS = [
    (90, "Excellent! You really know your Python."),
    (70, "Good job! A little more practice and you will master it."),
    (50, "Fair. Review the topics you missed and try again."),
    (0, "Keep practising. Read the explanations below and try again."),
]


# ---------- Loading and validation (data layer) ----------
def validate_question(q, seen_ids):
    """Return None if the question is valid, otherwise a message describing the problem."""
    if not isinstance(q, dict):
        return "not an object"
    missing = [k for k in ("id", "question", "options", "answer") if k not in q]
    if missing:
        return "missing key(s): " + ", ".join(missing)
    if isinstance(q["id"], bool) or not isinstance(q["id"], int):
        return "'id' must be a whole number"
    if q["id"] in seen_ids:
        return "duplicate id"
    if not isinstance(q["question"], str) or not q["question"].strip():
        return "'question' must be non-empty text"
    options = q["options"]
    if not isinstance(options, list) or not 2 <= len(options) <= len(LETTERS):
        return f"'options' must be a list of 2 to {len(LETTERS)} choices"
    if any(not isinstance(o, str) or not o.strip() for o in options):
        return "every option must be non-empty text"
    if len({o.strip().lower() for o in options}) != len(options):
        return "options contain duplicates"
    if q["answer"] not in options:
        return "'answer' must be one of the options"
    if "explanation" in q and not isinstance(q["explanation"], str):
        return "'explanation' must be text"
    return None


def load_questions(path):
    """Read the JSON file. Returns (valid_questions, problems, title, fatal_error)."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return [], [], "", f"Question file not found: {path}"
    except json.JSONDecodeError as error:
        return [], [], "", f"The question file is not valid JSON: {error}"
    if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        return [], [], "", "The question file must be an object containing a 'questions' list."

    valid, problems, seen_ids = [], [], set()
    for index, q in enumerate(data["questions"], start=1):
        error = validate_question(q, seen_ids)
        if error:
            label = q.get("id", f"#{index}") if isinstance(q, dict) else f"#{index}"
            problems.append(f"Question {label}: {error}")
        else:
            seen_ids.add(q["id"])
            valid.append(q)
    return valid, problems, str(data.get("quiz_title", "Quiz")), None


# ---------- Quiz logic ----------
def prepare_round(questions, count, rng):
    """Pick `count` different questions at random and shuffle each question's options.

    Works on copies, so the original question list is never changed.
    """
    chosen = rng.sample(questions, min(count, len(questions)))
    prepared = []
    for q in chosen:
        options = list(q["options"])
        rng.shuffle(options)
        prepared.append({"id": q["id"], "question": q["question"], "options": options,
                         "answer": q["answer"], "explanation": q.get("explanation", "")})
    return prepared


def parse_choice(text, option_count):
    """Turn 'b', 'B' or '2' into an option index, or None if it is not valid."""
    text = text.strip().upper()
    if len(text) == 1 and text in LETTERS[:option_count]:
        return LETTERS.index(text)
    if text.isdigit() and 1 <= int(text) <= option_count:
        return int(text) - 1
    return None


def parse_count(text, maximum, default=DEFAULT_COUNT):
    """Return (number of questions, None) or (None, error message)."""
    text = text.strip()
    if text == "":
        return min(default, maximum), None
    if not text.isdigit() or not 1 <= int(text) <= maximum:
        return None, f"Please enter a whole number from 1 to {maximum}."
    return int(text), None


def rating_for(percent):
    return next(message for minimum, message in RATINGS if percent >= minimum)


def calculate_result(results, total_questions):
    """Score = 1 point per correct answer. Unanswered questions score 0."""
    score = sum(1 for r in results if r["is_correct"])
    percent = round(score * 100 / total_questions, 1) if total_questions else 0.0
    return {"score": score, "total": total_questions, "answered": len(results),
            "skipped": total_questions - len(results), "percent": percent,
            "rating": rating_for(percent)}


# ---------- Interaction ----------
def ask_choice(option_count, input_fn):
    """Keep asking until the answer is valid (or the user types Q to quit)."""
    letters = "/".join(LETTERS[:option_count])
    while True:
        raw = input_fn(f"Your answer ({letters}, or Q to quit): ").strip()
        if raw.upper() == "Q":
            return QUIT
        index = parse_choice(raw, option_count)
        if index is not None:
            return index
        print(f"Invalid answer. Please type one of {letters} (or 1-{option_count}).")


def run_quiz(prepared, input_fn=None):
    """Ask every question. Returns (results, seconds_taken).

    input_fn defaults to the built-in input(); tests can pass a fake one.
    """
    input_fn = input_fn or input
    results, score, started = [], 0, time.perf_counter()
    for number, q in enumerate(prepared, start=1):
        print(f"\nQuestion {number} of {len(prepared)}   (score so far: {score})")
        print(q["question"])
        for i, option in enumerate(q["options"]):
            print(f"  {LETTERS[i]}) {option}")
        quitting = False
        while True:
            choice = ask_choice(len(q["options"]), input_fn)
            if choice != QUIT:
                break
            if input_fn("Quit the quiz now? (y/n): ").strip().lower() == "y":
                quitting = True
                break
        if quitting:
            print("Quiz ended early.")
            break
        picked = q["options"][choice]
        is_correct = picked == q["answer"]
        score += is_correct
        if is_correct:
            print("Correct! +1 point")
        else:
            print(f"Wrong. The correct answer is {LETTERS[q['options'].index(q['answer'])]}) {q['answer']}")
        if q["explanation"]:
            print(f"Explanation: {q['explanation']}")
        results.append({"question": q["question"], "your": picked, "correct": q["answer"],
                        "is_correct": is_correct, "explanation": q["explanation"]})
    return results, time.perf_counter() - started


def show_summary(results, total_questions, seconds, title):
    result = calculate_result(results, total_questions)
    minutes, secs = divmod(int(seconds), 60)
    print("\n" + "=" * 50)
    print(f"  FINAL RESULT: {title}")
    print("=" * 50)
    print(f"Score        : {result['score']} / {result['total']}  ({result['percent']}%)")
    print(f"Answered     : {result['answered']}   Skipped: {result['skipped']}")
    print(f"Time taken   : {minutes}m {secs:02d}s")
    print(f"Result       : {result['rating']}")
    if results:
        print("\nQuestion summary:")
        for number, r in enumerate(results, start=1):
            print(f"  {number:>2}. [{'OK   ' if r['is_correct'] else 'WRONG'}] {r['question']}")
        wrong = [r for r in results if not r["is_correct"]]
        if wrong:
            print("\nTopics to review:")
            for r in wrong:
                print(f"  - {r['question']}")
                print(f"      You answered: {r['your']}   Correct: {r['correct']}")
                if r["explanation"]:
                    print(f"      Why: {r['explanation']}")
        else:
            print("\nPerfect score on the questions you answered. No topics to review.")
    print("=" * 50)


def choose_count(maximum, preset):
    """Ask how many questions to play (unless --count was given)."""
    if preset is not None:
        return min(max(preset, 1), maximum)
    while True:
        count, error = parse_count(input(f"How many questions? (1-{maximum}, press Enter for {min(DEFAULT_COUNT, maximum)}): "),
                                   maximum)
        if error:
            print(error)
        else:
            return count


def main():
    parser = argparse.ArgumentParser(description="Command-line quiz application.")
    parser.add_argument("--file", default=DEFAULT_FILE, help="JSON file with the questions")
    parser.add_argument("--count", type=int, help="number of questions per round")
    parser.add_argument("--seed", type=int, help="fixed random seed (same questions and order every time)")
    args = parser.parse_args()

    questions, problems, title, fatal = load_questions(args.file)
    if fatal:
        print(fatal)
        return 1
    if not questions:
        print("No valid questions found in the file.")
        return 1
    for problem in problems:
        print("Skipped invalid question - " + problem)

    rng = random.Random(args.seed)
    print(f"\n=== {title.upper()} ===")
    print(f"{len(questions)} questions available. 1 point per correct answer.")
    try:
        while True:
            count = choose_count(len(questions), args.count)
            prepared = prepare_round(questions, count, rng)
            results, seconds = run_quiz(prepared)
            show_summary(results, len(prepared), seconds, title)
            if input("\nPlay again? (y/n): ").strip().lower() != "y":
                print("Thanks for playing. Goodbye!")
                return 0
    except (EOFError, KeyboardInterrupt):
        print("\nQuiz interrupted. Goodbye!")
        return 0


if __name__ == "__main__":
    sys.exit(main())