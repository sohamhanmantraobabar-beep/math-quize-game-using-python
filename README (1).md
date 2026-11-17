# Math Quiz Game

A colorful, timed math quiz built with **Python 3** and **Streamlit** for a college Python mini project. The player chooses a topic and difficulty, answers 10 multiple-choice questions, and receives a score breakdown at the end.

The project uses Python for all game logic and Streamlit for the web interface. Custom CSS handles the styling. No JavaScript, React, Node.js, or other programming language is required.

---

## Features

- Welcome screen with **Start the quiz** button
- Five categories: Addition, Subtraction, Multiplication, Division, and Mixed Math
- Three difficulty levels: Easy, Medium, and Hard
- Ten randomly generated questions per round
- Four unique answer options, always containing the correct answer
- One-answer-per-question locking so duplicate points are impossible
- 20-second timer for every question
- Correct, incorrect, and timeout feedback
- Live score and question progress
- Integer-only division (no division by zero, no decimals)
- Final score, percentage, correct count, missed count, and average time
- A full answer review and a personalized performance message
- Responsive custom CSS design
- Play Again and Change Category controls

---

## Project Structure

```text
math-quiz-game/
├── app.py              # Complete game, interface, and CSS
├── requirements.txt    # Python dependencies
├── README.md           # Setup, deployment, and viva notes
├── .gitignore          # Python files to exclude from Git
```

`.streamlit/secrets.toml` is deliberately excluded from version control. This project does not need any secrets.

---

## Requirements

- Python 3.9 or newer
- pip
- A web browser
- A free GitHub account (for deployment)
- A free Streamlit Community Cloud account (for deployment)

---

## Run Locally

### 1. Install Python

Download Python 3 from [python.org](https://www.python.org/downloads/). On Windows, tick **Add Python to PATH** during installation.

Check the installation:

```bash
python --version
```

On macOS or Linux, use `python3 --version` if `python` is not available.

### 2. Create and activate a virtual environment (recommended)

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Streamlit

```bash
streamlit run app.py
```

The terminal prints a local address such as **http://localhost:8501**. Open it in a browser. Press `Ctrl + C` in the terminal to stop the application.

If `streamlit` is not recognized, use:

```bash
python -m streamlit run app.py
```

---

## How to Play

1. Choose a math category and a difficulty.
2. Click **Start the quiz**.
3. Read the equation and choose one of the four options.
4. You have 20 seconds for each question. Your first click is final.
5. Read the feedback and click **Next question**.
6. After 10 questions, review your score, percentage, and answer breakdown.
7. Click **Play again** or change your category.

Division questions are generated as `dividend ÷ divisor = quotient`, where the dividend is built by multiplying the divisor and quotient. This guarantees a non-zero divisor and a whole-number answer.

---

## Game Logic and Functions

The code is intentionally split into short, presentation-friendly functions:

| Function | Responsibility |
|---|---|
| `initialize_game()` | Creates the initial values in `st.session_state` |
| `generate_question()` | Generates a random equation and its explanation |
| `generate_options()` | Builds four unique options that include the answer |
| `check_answer()` | Checks a selected option against the correct answer |
| `select_answer()` | Locks the first answer and blocks repeat attempts |
| `next_question()` | Saves the answer once, advances, or finishes the quiz |
| `calculate_score()` | Counts one point for every correct answer |
| `start_quiz()` / `play_again()` | Starts a new ten-question round |
| `reset_game()` | Clears the round and returns to the welcome screen |
| `main()` | Controls which Streamlit screen is displayed |

### Duplicate-point protection

When an answer is clicked, `select_answer()` checks `selected_answer` and `timed_out`. Once either value is set, the question is locked and later clicks are ignored. `next_question()` also checks `answer_saved` before appending the record. Finally, only records stored in the answers list are counted by `calculate_score()`.

### Timer

Each question stores a start timestamp. `time_remaining()` calculates the seconds left from that timestamp, so reruns cannot reset the clock. `render_live_timer()` is a Streamlit fragment that refreshes once per second. When it reaches zero, the question is marked as timed out and counted as incorrect.

---

## Quick Testing Checklist

- [x] Start a round in each of the five categories.
- [x] Test all three difficulty levels.
- [x] Confirm four options are always shown.
- [x] Confirm the correct answer is present in the options.
- [x] Submit a correct answer and confirm the score increases by exactly one.
- [x] Submit an incorrect answer and confirm the score does not change.
- [x] Click rapidly after answering and confirm no duplicate points.
- [x] Let the 20-second timer expire and confirm the question locks.
- [x] Complete exactly 10 questions and confirm the results screen appears.
- [x] Confirm percentage equals `(score / 10) × 100`.
- [x] Start a new round and confirm score and progress reset.
- [x] Test the layout on desktop and a narrow mobile viewport.

---

## GitHub Instructions

1. Create a new empty repository on [GitHub](https://github.com/new), for example `math-quiz-game`.
2. Do **not** commit a `.venv` folder or Streamlit secrets.
3. In the project folder, run:

```bash
git init
git add .
git commit -m "Add complete Math Quiz Game"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/math-quiz-game.git
git push -u origin main
```

4. Refresh the GitHub repository page and check that `app.py`, `requirements.txt`, `README.md`, and `.gitignore` are visible.
5. Never upload `.streamlit/secrets.toml`; this project does not require secrets.

---

## Deploy on Streamlit Community Cloud

1. Sign in at [share.streamlit.io](https://share.streamlit.io/) with GitHub and authorize Streamlit.
2. Click **Create app** (or **New app**).
3. Choose **Deploy a public app from GitHub**.
4. Select your repository, the `main` branch, and set **Main file path** to `app.py`.
5. Optionally choose a short app URL, then click **Deploy**.
6. Wait for Streamlit to install `requirements.txt` and start the app.
7. After a successful deployment, Streamlit provides a public URL such as:

```text
https://your-app-name.streamlit.app
```

Share that URL with your teacher or add it to the top of the README. To update the deployed app later, push your changes to GitHub; Streamlit Community Cloud redeploys automatically.

### Common deployment issues

- **App will not start:** check the logs in the Streamlit dashboard and confirm `app.py` is the main file.
- **Package install error:** keep only the dependencies you use. This project only needs Streamlit.
- **Wrong interface or broken styles:** refresh the page, then stop and reboot the app from the dashboard.
- **Changed code but app did not update:** use the app's **Reboot** option or confirm the latest commit is on the selected branch.

---

## Simple Explanation for a College Viva

**What is Streamlit?** Streamlit is a Python library that turns a normal Python script into an interactive web app. Widgets such as buttons and progress bars are created with Python function calls.

**What is `st.session_state`?** Streamlit reruns the script whenever a player clicks a button. Session state is a dictionary that survives those reruns. It stores the selected category, the questions, the current index, the player's answers, and the score.

**How are the questions generated?** The `random` module chooses numbers for the selected operation and difficulty. A dictionary stores each question, its options, the answer, and an explanation. A new list of ten unique expressions is created at the start of every round.

**Why is division safe?** The code first picks a divisor and a whole-number quotient, then calculates `dividend = divisor × quotient`. As a result, every division has a whole-number answer and division by zero is impossible.

**How is the score calculated?** Each completed answer record contains a boolean `correct` value. `calculate_score()` adds one for every record marked `True`. The percentage is `score ÷ 10 × 100`, rounded to an integer.

**How are duplicate points prevented?** The answer buttons are disabled after the first click. Changing `st.session_state` triggers a rerun, and the guard in `select_answer()` ignores further attempts. `answer_saved` provides a second protection before a record is appended.

**Why are functions used?** They separate generating, checking, scoring, and displaying. This makes the program easier to read, test, explain, and debug.

---

## Future Improvements

- Add a leaderboard with a database
- Add a sound toggle using Streamlit widgets
- Add a streak bonus or time-based points
- Add more question types such as percentages and sequences
- Add user accounts and saved progress

---

## License

This project is free to use and adapt for learning and college submissions.
