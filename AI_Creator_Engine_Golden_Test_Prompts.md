# AI Creator Engine — Golden Test Prompts

## Purpose

Use these prompts to demonstrate the **reliable teaching path** of the current Teaching Edition.

The project is intentionally strongest when the user gives a clear Python/AI topic or a specific Python creation request.

These are **recommended demo prompts**, not restrictions on what the system can accept.

---

## 1. CHAT — RECOMMENDED QUESTIONS

Use these in the normal Chat screen.

## Python Basics

### Test 1 — Variables

**Prompt:**
> What are variables in Python? Explain them for a beginner and give one small code example.

**Expected result:**

- Defines a Python variable.
- Uses a short beginner-friendly explanation.
- Gives a small Python example.
- Does not wander into unrelated topics.

### Test 2 — Lists

**Prompt:**
> What are lists in Python? Explain how to create a list, access an item, and add an item. Show one small example.

**Expected result:**

- Explains what a list is.
- Shows creation.
- Shows indexing/access.
- Shows adding an item.
- Includes a valid Python example.

### Test 3 — Loops

**Prompt:**
> What are loops in Python? Explain the difference between a `for` loop and a `while` loop, with one small example of each.

**Expected result:**

- Explains both loop types.
- Gives one `for` example.
- Gives one `while` example.
- Keeps the explanation beginner-friendly.

### Test 4 — Functions

**Prompt:**
> What is a function in Python? Explain parameters and return values, then show a small function that adds two numbers.

**Expected result:**

- Explains functions.
- Explains parameters.
- Explains `return`.
- Provides a working small function.

### Test 5 — Dictionaries

**Prompt:**
> What is a dictionary in Python? Explain keys and values and show how to read and update one value.

**Expected result:**

- Defines a dictionary.
- Explains keys and values.
- Shows reading a value.
- Shows updating a value.

### Test 6 — Conditional Statements

**Prompt:**
> Explain `if`, `elif`, and `else` in Python for a beginner. Give a small example that checks whether a number is positive, negative, or zero.

**Expected result:**

- Explains the three conditions.
- Uses a clear example.
- Code should be valid Python.

---

## 2. CHAT — PYTHON + RAG TESTS\

These are useful for demonstrating that Chat is using the prepared knowledge base.

### Test 7 — Python and RAG

**Prompt:**
> Explain how a Python program can read data from a file. Keep the explanation beginner-friendly and show a small Python example.

**Expected result:**

- Explains file reading.
- Provides a small Python example.
- Uses relevant Python knowledge rather than inventing an unrelated method.

### Test 8 — Random Module

**Prompt:**
> What is the Python `random` module? Explain `random.choice()` and show a small example using a list.

**Expected result:**

- Explains the standard-library module.
- Explains `random.choice()`.
- Shows a correct example.

### Test 9 — Error Handling

**Prompt:**
> What is `try` and `except` in Python? Explain why it is used and show a small example that safely handles invalid number input.

**Expected result:**

- Explains the purpose of exception handling.
- Shows `try`.
- Shows `except`.
- Gives a sensible beginner example.

### Test 10 — Classes

**Prompt:**
> What is a class in Python? Explain the idea using a simple `Student` example and show how to create one object.

**Expected result:**

- Explains class/object in simple language.
- Uses a small `Student` example.
- Shows object creation.

---

## 3. CREATOR — RECOMMENDED PYTHON PROGRAM REQUESTS

Use these in the Creator screen.

## Test 11 — Simple Function

**Prompt:**
> Create a Python function named `add_numbers(a, b)` that returns the sum of two numbers. Include the complete Python code and a small example showing how to call the function.

**Expected result:**

- Valid Python.
- Correct function name.
- Correct parameters.
- Uses `return`.
- Includes a call example.
- Includes all required code.

## Test 12 — Even/Odd Function

**Prompt:**
> Create a Python function named `is_even(number)` that returns `True` when the number is even and `False` when it is odd. Include a small test example.

**Expected result:**

- Correct use of `%`.
- Returns a Boolean.
- Contains a runnable example.

## Test 13 — Word Counter

**Prompt:**
> Create a Python function named `count_words(text)` that counts how many words are in a sentence. Keep it simple for a beginner and include one example call.

**Expected result:**

- Correct function.
- Uses a simple string/list approach.
- Returns the word count.
- Includes an example.

## Test 14 — Number Guessing Game

**Prompt:**
> Create a simple Python number guessing game. The computer should choose a random number from 1 to 10, the user enters a guess, and the program tells the user whether the guess is correct. Use beginner-friendly Python.

**Expected result:**

- Uses `random`.
- Accepts user input.
- Compares the guess.
- Produces a correct result.
- Includes required imports.

## Test 15 — Rock Paper Scissors

**Prompt:**
> Create a complete beginner-friendly Python Rock Paper Scissors game. The computer should randomly choose rock, paper, or scissors. The user should enter a choice. Compare both choices and print whether the user wins, loses, or ties. Include all required imports and a `main` section.

**Expected result:**

- Imports `random`.
- Uses consistent lowercase choices.
- Compares both player and computer choices.
- Correctly handles win, loss, and tie.
- Includes a runnable `if __name__ == "__main__":` section.
- Does not use another programming language.

## Test 16 — Menu Program

**Prompt:**
> Create a simple Python menu program with three options: add two numbers, subtract two numbers, or exit. Use a `while` loop and beginner-friendly functions.

**Expected result:**

- Uses a `while` loop.
- Has three clear options.
- Uses functions.
- Handles exit.
- Keeps the code readable.

## Test 17 — Simple Calculator

**Prompt:**
> Create a beginner-friendly Python calculator that can add, subtract, multiply, and divide two numbers. Use separate functions for the four operations and handle division by zero.

**Expected result:**

- Four simple functions.
- Correct arithmetic.
- Division-by-zero handling.
- Clear user input flow.

## Test 18 — List Processing

**Prompt:**
> Create a Python function named `find_largest(numbers)` that returns the largest value in a list. Explain the code with short comments and include a small example.

**Expected result:**

- Accepts a list.
- Returns the largest value.
- Works for a normal list example.
- Comments are useful and not excessive.

---

## 4. CREATOR — DOCUMENT GENERATION TESTS

These test the PDF/DOCX generation path rather than only code generation.

### Test 19 — Beginner Report

**Prompt:**
> Create a beginner-friendly report about Python loops. Explain `for` loops and `while` loops, include a small Python example for each, and organize the report with headings.

**Expected result:**

- Clear title.
- Headings.
- Correct Python examples.
- Useful explanatory text.
- Generates a readable PDF or DOCX.

### Test 20 — Python Functions Report

**Prompt:**
> Create a beginner-friendly Python functions report. Explain functions, parameters, return values, and include two small examples.

**Expected result:**

- Structured document.
- Correct Python concepts.
- Two examples.
- Readable formatting.

---

## 5. PROMPTS TO AVOID FOR THE MAIN DEMO

These are valid natural-language questions, but they are **less useful as the first classroom demonstration** because they are vague.

Avoid starting with:

> hii teach me Python
>
> explain programming
>
> tell me about loops
>
> make something cool
>
> create a game
>
> teach me everything about Python

The model may still answer these, but the result is less predictable.

Instead, make the request specific.

For example:

**Less specific:**
> tell me about loops

**Better:**
> What are loops in Python? Explain `for` and `while` loops with one small example of each.

**Less specific:**
> make a game

**Better:**
> Create a beginner-friendly Python Rock Paper Scissors game using `random`, user input, and win/lose/tie logic.

---

## 6. GOLDEN DEMO SEQUENCE

For a classroom demonstration, use this order:

### Chat

1. What are lists in Python? Explain how to create a list, access an item, and add an item. Show one small example.
2. What are loops in Python? Explain the difference between a `for` loop and a `while` loop, with one small example of each.
3. What is a function in Python? Explain parameters and return values, then show a small function that adds two numbers.
4. What is the Python `random` module? Explain `random.choice()` and show a small example using a list.

### Creator

1. Create a Python function named `is_even(number)` that returns `True` when the number is even and `False` when it is odd. Include a small test example.
2. Create a simple Python number guessing game. The computer should choose a random number from 1 to 10, the user enters a guess, and the program tells the user whether the guess is correct.
3. Create a complete beginner-friendly Python Rock Paper Scissors game. The computer should randomly choose rock, paper, or scissors. The user should enter a choice. Compare both choices and print whether the user wins, loses, or ties. Include all required imports and a `main` section.
4. Create a beginner-friendly report about Python loops. Explain `for` loops and `while` loops, include a small Python example for each, and organize the report with headings.

---

## 7. WHAT COUNTS AS A GOOD RESULT

For the current Teaching Edition, a good result should generally be:

- Directly related to the user's request.
- Correct for the requested Python concept or task.
- Written at a beginner-friendly level when requested.
- Supported by relevant knowledge from the RAG system when applicable.
- Free from repeated sentences or paragraphs.
- Valid Python when the Creator request is specifically for Python code.
- Complete enough to run or to demonstrate the requested function.
- Properly formatted when exported to PDF or DOCX.

Remember: the current Teaching Edition is deliberately optimized for **Python program generation**. Chat can still discuss other subjects, but Python is the language where the Creator is intended to be the most reliable.

---

## 8. TROUBLESHOOTING A BAD DEMO RESULT

If a vague prompt produces a strange answer, first make the prompt more specific.

Example:

> Explain loops.

becomes:

> What are loops in Python? Explain `for` and `while` loops for a beginner and show one small example of each.

For Creator:

> make rock paper scissors

becomes:

> Create a complete beginner-friendly Python Rock Paper Scissors game. Use `random`, user input, and correct win/lose/tie logic. Include all required imports and a runnable `main` section.

This makes the intended task much clearer to the small local model while keeping the application itself simple.
