
# CLI Quiz Application

**Veda Technology: Python Programming Track · Level 1 · Task 24 (Day 24)**

A command-line quiz that **loads questions from a JSON file**, asks them in **random order**, accepts and validates answers, **calculates the score**, and shows a **final result summary**.

## Files
| File | Purpose |
|---|---|
| `quiz_app.py` | The quiz program (the file you run) |
| `questions.json` | **The question bank** (15 questions), kept separate from the program logic |
| `sample_run.txt` | A complete sample session (10 questions) |
| `REPORT.pdf` | Task report |

## Features
- **Question bank in JSON:** add, edit, or remove questions without touching any code
- **Random selection:** each round picks different questions (`random.sample`, no repeats) and also **shuffles the answer options**
- **Choose how many questions** to play (1 to 15, default 10), or use `--count`
- **Input validation:** answers must be A-D (or 1-4); anything else is rejected with a message and the same question is asked again
- **Instant feedback:** correct or wrong, the right answer, and a short explanation after each question
- **Score calculation:** 1 point per correct answer, shown as a score, a percentage, and a rating
- **Final result summary:** score, answered and skipped counts, time taken, a per-question table, and a "Topics to review" list with explanations for every wrong answer
- **Quit anytime** by typing `Q` (asks for confirmation; unanswered questions count as skipped)
- **Play again** without restarting the program
- The question file is **validated on load**: invalid questions are skipped with a reason, and a missing or broken file gives a clear message

## Requirements
Python 3.6+ (standard library only: `json`, `random`, `argparse`, `time`)

## How to Run
Keep `quiz_app.py` and `questions.json` in the same folder:
```bash
python quiz_app.py
```
Options:
| Option | Meaning |
|---|---|
| `--count N` | Number of questions per round (skips the question) |
| `--file PATH` | Use a different question file |
| `--seed N` | Fixed random seed: the same questions in the same order every time (useful for testing) |

Example: `python quiz_app.py --count 5`

## Question File Format (`questions.json`)
```json
{
  "quiz_title": "Python Basics Quiz",
  "questions": [
    {"id": 2, "question": "Which keyword is used to define a function in Python?",
     "options": ["func", "def", "function", "define"],
     "answer": "def",
     "explanation": "Functions are defined with the def keyword."}
  ]
}
```
- `id`: a unique whole number
- `options`: 2 to 6 different choices (they are shuffled every round)
- `answer`: the correct option, written exactly as it appears in `options` (so shuffling never breaks it)
- `explanation`: optional, shown after each answer

## Scoring and Ratings
1 point per correct answer; no negative marking. The percentage is calculated out of the questions in the round, so skipped questions score 0.

| Percentage | Result message |
|---|---|
| 90 or above | Excellent! You really know your Python. |
| 70 to 89.9 | Good job! A little more practice and you will master it. |
| 50 to 69.9 | Fair. Review the topics you missed and try again. |
| Below 50 | Keep practising. Read the explanations below and try again. |

## Sample Output
```
Question 1 of 10   (score so far: 0)
Which symbol starts a single-line comment in Python?
  A) #
  B) --
  C) /*
  D) //
Your answer (A/B/C/D, or Q to quit): A
Correct! +1 point
Explanation: Everything after # on a line is ignored by Python.
```
```
Question 4 of 10   (score so far: 3)
Which list method adds an item to the end of the list?
  A) insert()
  B) push()
  C) append()
  D) add()
Your answer (A/B/C/D, or Q to quit): A
Wrong. The correct answer is C) append()
Explanation: append(x) adds x at the end. insert(i, x) adds at position i.
```
```
==================================================
  FINAL RESULT: Python Basics Quiz
==================================================
Score        : 8 / 10  (80.0%)
Answered     : 10   Skipped: 0
Result       : Good job! A little more practice and you will master it.

Question summary:
   1. [OK   ] Which symbol starts a single-line comment in Python?
   2. [OK   ] What does len("Veda") return?
   3. [OK   ] How do you read the value of the key "name" from a dictionary d?
   4. [WRONG] Which list method adds an item to the end of the list?
   5. [OK   ] What is the output of print(type([]))?
   6. [OK   ] Which keyword is used to define a function in Python?
   7. [OK   ] Which module is used to work with JSON data in Python?
   8. [WRONG] What is the output of print("ab" * 3)?
   9. [OK   ] What is the result of int("5") + 2?
  10. [OK   ] What is the result of 7 // 2?

Topics to review:
  - Which list method adds an item to the end of the list?
      You answered: insert()   Correct: append()
      Why: append(x) adds x at the end. insert(i, x) adds at position i.
  - What is the output of print("ab" * 3)?
      You answered: It raises an error   Correct: ababab
      Why: Multiplying a string by an integer repeats it.
==================================================
```
The full session is in `sample_run.txt`. (A scripted run takes no time, so the "Time taken" line is left out of the sample. The real program always shows it.)

## Author
Nabila, Veda Technology Intern