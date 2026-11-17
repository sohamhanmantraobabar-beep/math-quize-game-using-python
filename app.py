"""
Math Quiz Game
==============
A complete college Python mini project built with Python 3 and Streamlit.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py

All game logic, scoring, and validation lives in Python.
Custom CSS is used only for the visual design.
"""

import random
import time

import streamlit as st

# ---------------------------------------------------------------------------
# Game settings
# ---------------------------------------------------------------------------

TOTAL_QUESTIONS = 10
QUESTION_TIME = 20  # seconds allowed for each question

CATEGORIES = {
    "addition": {"label": "Addition", "symbol": "+", "tagline": "Build it up"},
    "subtraction": {"label": "Subtraction", "symbol": "−", "tagline": "Take it away"},
    "multiplication": {"label": "Multiplication", "symbol": "×", "tagline": "Times it by"},
    "division": {"label": "Division", "symbol": "÷", "tagline": "Share it out"},
    "mixed": {"label": "Mixed Math", "symbol": "✦", "tagline": "A bit of everything"},
}

DIFFICULTIES = {
    "easy": {"label": "Easy", "tagline": "Gentle warm-up"},
    "medium": {"label": "Medium", "tagline": "Balanced challenge"},
    "hard": {"label": "Hard", "tagline": "For brave brains"},
}

OPERATIONS = ["addition", "subtraction", "multiplication", "division"]


# ---------------------------------------------------------------------------
# Initialisation and state helpers
# ---------------------------------------------------------------------------

def initialize_game():
    """Create the session-state values used by the game exactly once."""
    defaults = {
        "screen": "welcome",
        "category": "mixed",
        "difficulty": "easy",
        "questions": [],
        "current_index": 0,
        "answers": [],
        "selected_answer": None,
        "timed_out": False,
        "question_start": None,
        "time_spent": 0,
        "answer_saved": False,
        "best_score": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # These keys are intentionally kept when the player restarts a round.
    if "best_score" not in st.session_state:
        st.session_state.best_score = 0


def reset_game():
    """Send the player back to the welcome screen and clear the current round."""
    st.session_state.questions = []
    st.session_state.current_index = 0
    st.session_state.answers = []
    st.session_state.selected_answer = None
    st.session_state.timed_out = False
    st.session_state.question_start = None
    st.session_state.time_spent = 0
    st.session_state.answer_saved = False
    st.session_state.screen = "welcome"
    st.rerun()


def start_quiz():
    """Generate ten new questions and begin a fresh round."""
    try:
        questions = generate_quiz(st.session_state.category, st.session_state.difficulty)
    except ValueError as error:
        st.error(str(error))
        return

    st.session_state.questions = questions
    st.session_state.current_index = 0
    st.session_state.answers = []
    st.session_state.selected_answer = None
    st.session_state.timed_out = False
    st.session_state.time_spent = 0
    st.session_state.answer_saved = False
    st.session_state.question_start = time.time()
    st.session_state.screen = "quiz"
    st.rerun()


def play_again():
    """Start a new round with the same category and difficulty."""
    st.session_state.category = st.session_state.category
    st.session_state.difficulty = st.session_state.difficulty
    start_quiz()


# ---------------------------------------------------------------------------
# Question generation
# ---------------------------------------------------------------------------

def random_int(minimum, maximum):
    """Return a random whole number in an inclusive range."""
    return random.randint(minimum, maximum)


def generate_options(answer):
    """Return four unique multiple-choice options that include the answer."""
    options = {answer}
    offsets = [1, -1, 2, -2, 3, -3, 10, -10, 5, -5]
    random.shuffle(offsets)

    for offset in offsets:
        if len(options) == 4:
            break
        candidate = answer + offset
        if candidate >= 0:  # Keep options friendly, never negative.
            options.add(candidate)

    next_fallback = answer + 4
    while len(options) < 4:
        options.add(next_fallback)
        next_fallback += 1

    options = list(options)
    random.shuffle(options)
    return options


def make_numbers(operation, difficulty):
    """Create two numbers and a whole-number answer for one operation."""
    if operation == "addition":
        ranges = {
            "easy": (1, 20),
            "medium": (12, 89),
            "hard": (105, 799),
        }
        low, high = ranges[difficulty]
        first = random_int(low, high)
        second = random_int(low, high)
        return first, second, first + second

    if operation == "subtraction":
        ranges = {
            "easy": (1, 18),
            "medium": (10, 60),
            "hard": (60, 420),
        }
        low, high = ranges[difficulty]
        second = random_int(low, high)
        answer = random_int(1 if difficulty == "easy" else 8, 300 if difficulty == "hard" else 45)
        return second + answer, second, answer

    if operation == "multiplication":
        ranges = {
            "easy": (2, 10),
            "medium": (3, 15),
            "hard": (8, 24),
        }
        low, high = ranges[difficulty]
        first = random_int(low, high)
        second = random_int(max(2, low - 1), high)
        return first, second, first * second

    # Division always uses a non-zero divisor and a whole-number quotient.
    ranges = {
        "easy": {"divisor": (2, 9), "quotient": (2, 10)},
        "medium": {"divisor": (3, 12), "quotient": (4, 16)},
        "hard": {"divisor": (5, 16), "quotient": (8, 26)},
    }
    divisor = random_int(*ranges[difficulty]["divisor"])
    answer = random_int(*ranges[difficulty]["quotient"])
    return divisor * answer, divisor, answer


def generate_question(category, difficulty):
    """Create one question dictionary, including validated options."""
    operation = random.choice(OPERATIONS) if category == "mixed" else category
    if operation not in OPERATIONS:
        raise ValueError("Please choose a valid math category.")

    first, second, answer = make_numbers(operation, difficulty)

    symbols = {
        "addition": "+",
        "subtraction": "−",
        "multiplication": "×",
        "division": "÷",
    }

    explanations = {
        "addition": f"Add {first} and {second} to get {answer}.",
        "subtraction": f"Take {second} away from {first} to get {answer}.",
        "multiplication": f"{first} groups of {second} make {answer}.",
        "division": f"{second} × {answer} = {first}, so {first} ÷ {second} = {answer}.",
    }

    return {
        "expression": f"{first} {symbols[operation]} {second}",
        "answer": answer,
        "options": generate_options(answer),
        "operation": operation,
        "category": category,
        "explanation": explanations[operation],
    }


def generate_quiz(category, difficulty):
    """Generate ten questions, avoiding identical expressions in one round."""
    if category not in CATEGORIES:
        raise ValueError("Unknown category.")
    if difficulty not in DIFFICULTIES:
        raise ValueError("Unknown difficulty.")

    questions = []
    seen = set()
    attempts = 0

    while len(questions) < TOTAL_QUESTIONS and attempts < 500:
        question = generate_question(category, difficulty)
        if question["expression"] not in seen:
            seen.add(question["expression"])
            question["question_number"] = len(questions) + 1
            questions.append(question)
        attempts += 1

    if len(questions) != TOTAL_QUESTIONS:
        raise ValueError("Could not create enough unique questions. Please try again.")

    return questions


# ---------------------------------------------------------------------------
# Gameplay and scoring
# ---------------------------------------------------------------------------

def check_answer(question, selected_option):
    """Return True when the selected option matches the stored answer."""
    return selected_option == question["answer"]


def calculate_score(answers):
    """Count only one point for each correct answer dictionary."""
    return sum(1 for answer in answers if answer["correct"])


def current_question():
    """Return the active question dictionary."""
    return st.session_state.questions[st.session_state.current_index]


def select_answer(option):
    """Lock the first answer for a question and prevent duplicate scoring."""
    state = st.session_state

    # Guard: once an answer or timeout exists, further clicks are ignored.
    if state.selected_answer is not None or state.timed_out:
        return

    elapsed = time.time() - state.question_start
    if elapsed >= QUESTION_TIME:
        state.timed_out = True
        state.selected_answer = None
        state.time_spent = QUESTION_TIME
    else:
        state.selected_answer = option
        state.time_spent = min(QUESTION_TIME, max(1, int(round(elapsed))))

    st.rerun()


def time_remaining():
    """Calculate the number of seconds left from a timestamp, not a loop."""
    start = st.session_state.question_start or time.time()
    return max(0, QUESTION_TIME - int(time.time() - start))


def next_question():
    """Save the current answer once, then advance or finish the quiz."""
    state = st.session_state

    if state.selected_answer is None and not state.timed_out:
        return
    if state.answer_saved:
        return

    question = current_question()
    correct = (
        state.selected_answer is not None
        and check_answer(question, state.selected_answer)
    )

    record = {
        "question": question,
        "selected": state.selected_answer,
        "correct": correct,
        "timed_out": state.timed_out,
        "time_spent": state.time_spent,
    }
    state.answers.append(record)
    state.answer_saved = True  # Extra safety against duplicate points.

    if len(state.answers) >= TOTAL_QUESTIONS:
        score = calculate_score(state.answers)
        state.best_score = max(state.best_score, score)
        state.screen = "results"
    else:
        state.current_index += 1
        state.selected_answer = None
        state.timed_out = False
        state.time_spent = 0
        state.answer_saved = False
        state.question_start = time.time()

    st.rerun()


# ---------------------------------------------------------------------------
# Page setup and styling
# ---------------------------------------------------------------------------

def configure_page():
    st.set_page_config(
        page_title="Math Quiz Game",
        page_icon="➕",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def inject_css():
    """Apply the full custom design. No JavaScript is used."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');

        :root {
            --ink: #09081c;
            --panel: #14112e;
            --lime: #c9f56b;
            --lilac: #b7a4ff;
            --mint: #7de7c0;
            --coral: #ff9c8d;
            --muted: rgba(255,255,255,.48);
        }

        #MainMenu, footer, header { visibility: hidden; }
        .stApp {
            background:
                radial-gradient(900px 500px at 88% -5%, rgba(118,86,220,.22), transparent 65%),
                radial-gradient(700px 450px at -5% 35%, rgba(201,245,107,.06), transparent 60%),
                #09081c;
            color: #f8f7ff;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }
        .block-container {
            max-width: 1080px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        h1, h2, h3 { font-family: 'Space Grotesk', sans-serif !important; }

        /* Brand header */
        .brand { display:flex; align-items:center; gap:12px; margin-bottom: 2rem; }
        .brand-mark {
            display:grid; place-items:center; width:40px; height:40px;
            border-radius:12px; background:var(--lime); color:var(--ink);
            font-size:25px; font-weight:800; box-shadow:0 0 30px rgba(201,245,107,.28);
        }
        .brand-name { font-family:'Space Grotesk'; font-weight:700; font-size:18px; }
        .brand-sub { color:rgba(255,255,255,.35); font-size:9px; letter-spacing:.18em; text-transform:uppercase; }
        .pill {
            display:inline-flex; align-items:center; gap:8px; padding:7px 12px;
            border:1px solid rgba(201,245,107,.2); background:rgba(201,245,107,.07);
            border-radius:999px; color:var(--lime); font-size:10px; font-weight:800;
            letter-spacing:.12em; text-transform:uppercase;
        }

        /* Welcome */
        .hero-title {
            font-family:'Space Grotesk'; font-size: clamp(48px, 7vw, 78px);
            line-height:.94; letter-spacing:-.065em; margin:20px 0 0; font-weight:700;
        }
        .hero-title span { color:var(--lime); }
        .hero-copy { color:rgba(255,255,255,.55); max-width:500px; line-height:1.8; font-size:15px; }
        .section-label {
            color:rgba(255,255,255,.35); font-size:9px; font-weight:800;
            text-transform:uppercase; letter-spacing:.17em; margin:4px 0 10px;
        }
        .setup-panel {
            background:linear-gradient(155deg, rgba(27,23,56,.98), rgba(15,12,36,.98));
            border:1px solid rgba(255,255,255,.11); border-radius:24px; padding:22px;
        }
        .setup-title { font-family:'Space Grotesk'; font-size:20px; font-weight:600; }
        .setup-sub { color:rgba(255,255,255,.38); font-size:12px; margin-top:2px; }
        .meta-row { color:rgba(255,255,255,.35); font-size:10px; font-weight:600; }
        .how-card {
            height:100%; padding:22px; border-radius:18px; background:rgba(255,255,255,.027);
            border:1px solid rgba(255,255,255,.075);
        }
        .how-number { font-family:'JetBrains Mono'; color:rgba(255,255,255,.2); font-size:11px; }
        .how-icon { font-size:22px; }
        .how-title { font-family:'Space Grotesk'; font-size:17px; font-weight:600; margin:14px 0 7px; }
        .how-copy { color:rgba(255,255,255,.38); font-size:12px; line-height:1.7; }
        .python-note {
            margin-top:2.5rem; padding:18px 20px; border-radius:16px;
            background:rgba(183,164,255,.055); border:1px solid rgba(183,164,255,.13);
            color:rgba(255,255,255,.45); font-size:11px; line-height:1.7;
        }

        /* Streamlit controls */
        div[data-testid="stButton"] > button {
            font-family:'Plus Jakarta Sans', sans-serif;
            border-radius:11px; font-weight:700; font-size:12px;
            border:1px solid rgba(255,255,255,.09);
            background:rgba(255,255,255,.035); color:rgba(255,255,255,.68);
            min-height:42px; transition:all .2s ease;
        }
        div[data-testid="stButton"] > button:hover {
            border-color:rgba(201,245,107,.35); color:white;
            background:rgba(255,255,255,.06); transform:translateY(-1px);
        }
        div[data-testid="stButton"] > button[kind="primary"] {
            background:var(--lime); color:var(--ink) !important;
            border-color:var(--lime); box-shadow:0 12px 30px -10px rgba(201,245,107,.4);
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background:#d7ff83; border-color:#d7ff83; color:var(--ink) !important;
        }
        div[data-testid="stButton"] > button:disabled {
            opacity:.48; transform:none;
        }
        div[class*="st-key-category_"] button { min-height:56px; }
        div[class*="st-key-difficulty_"] button { min-height:40px; }
        div[class*="st-key-answer_"] button {
            min-height:58px; font-family:'JetBrains Mono'; font-size:18px;
            background:rgba(255,255,255,.03);
        }
        .stProgress > div > div > div > div { background:var(--lime); }
        div[data-testid="stExpander"] {
            background:rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.075);
            border-radius:14px;
        }

        /* Quiz */
        .quiz-top { display:flex; justify-content:space-between; align-items:center; color:rgba(255,255,255,.35); font-size:11px; }
        .quiz-score { color:var(--lime); font-family:'JetBrains Mono'; font-weight:700; }
        .quiz-card,
        div[class*="st-key-quiz_card"] {
            background:linear-gradient(155deg, rgba(26,22,54,.98), rgba(15,12,36,.98));
            border:1px solid rgba(255,255,255,.11); border-radius:22px;
            padding:20px; box-shadow:0 30px 80px -35px #000;
        }
        .q-tag {
            display:inline-flex; align-items:center; gap:7px; padding:6px 10px;
            border-radius:7px; background:rgba(183,164,255,.1); color:var(--lilac);
            font-size:9px; font-weight:800; text-transform:uppercase; letter-spacing:.1em;
        }
        .equation {
            text-align:center; font-family:'JetBrains Mono'; font-weight:700;
            color:white; font-size:clamp(40px, 8vw, 62px); letter-spacing:-.06em;
            padding:24px 0 14px;
        }
        .equation .operator { color:var(--lime); }
        .equation .unknown { color:rgba(255,255,255,.28); }
        .equation-hint { text-align:center; color:rgba(255,255,255,.25); font-size:9px; font-weight:800; letter-spacing:.18em; text-transform:uppercase; }

        /* Timer */
        .timer-wrap { display:flex; justify-content:center; padding:8px 0 2px; }
        .timer-ring {
            width:56px; height:56px; border-radius:50%; display:grid; place-items:center;
            background:conic-gradient(var(--lime) var(--progress), rgba(255,255,255,.07) 0);
            position:relative;
        }
        .timer-ring::before { content:''; position:absolute; inset:4px; background:#15112f; border-radius:50%; }
        .timer-ring span { position:relative; font-family:'JetBrains Mono'; font-size:15px; font-weight:700; }
        .timer-label { color:rgba(255,255,255,.28); text-align:center; font-size:9px; text-transform:uppercase; letter-spacing:.14em; }

        /* Feedback */
        .feedback { padding:13px 15px; border-radius:12px; margin:14px 0 4px; font-size:12px; }
        .feedback strong { display:block; font-size:13px; margin-bottom:2px; }
        .feedback.correct { background:rgba(125,231,192,.08); border:1px solid rgba(125,231,192,.22); color:#b9f7e3; }
        .feedback.wrong { background:rgba(255,156,141,.07); border:1px solid rgba(255,156,141,.2); color:#ffc8c0; }
        .feedback.timeout { background:rgba(255,200,117,.07); border:1px solid rgba(255,200,117,.2); color:#ffe0b0; }
        .option-list { display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:12px; }
        .option {
            padding:16px; border-radius:12px; background:rgba(255,255,255,.025);
            border:1px solid rgba(255,255,255,.075); color:rgba(255,255,255,.45);
            font-family:'JetBrains Mono'; font-size:18px;
        }
        .option.correct { border-color:rgba(125,231,192,.7); background:rgba(125,231,192,.13); color:white; }
        .option.wrong { border-color:rgba(255,156,141,.65); background:rgba(255,156,141,.12); color:white; }
        .option small { display:block; font-family:'Plus Jakarta Sans'; font-size:8px; text-transform:uppercase; letter-spacing:.08em; margin-top:4px; opacity:.65; }
        .locked-note { text-align:center; color:rgba(255,255,255,.24); font-size:10px; margin:10px 0; }

        /* Results */
        .result-card {
            background:linear-gradient(145deg, #1a153a, #0f0d27);
            border:1px solid rgba(255,255,255,.12); border-radius:24px;
            padding:clamp(22px, 4vw, 40px); box-shadow:0 40px 100px -40px #000;
        }
        .score-circle {
            width:180px; height:180px; margin:0 auto; border-radius:50%;
            display:grid; place-items:center; position:relative;
            background:conic-gradient(var(--lime) var(--score), rgba(255,255,255,.065) 0);
        }
        .score-circle::before { content:''; position:absolute; inset:9px; border-radius:50%; background:#14102e; }
        .score-inner { position:relative; text-align:center; }
        .score-value { font-family:'Space Grotesk'; font-size:52px; font-weight:700; letter-spacing:-.06em; line-height:1; }
        .score-label { color:rgba(255,255,255,.3); font-size:8px; text-transform:uppercase; letter-spacing:.2em; margin-top:8px; }
        .result-title { font-family:'Space Grotesk'; font-size:clamp(30px, 5vw, 44px); font-weight:600; letter-spacing:-.05em; line-height:1.05; margin:8px 0 10px; }
        .result-copy { color:rgba(255,255,255,.48); font-size:13px; line-height:1.7; max-width:440px; }
        .stat-label { color:rgba(255,255,255,.28); font-size:8px; text-transform:uppercase; letter-spacing:.1em; font-weight:800; }
        .stat-value { font-family:'JetBrains Mono'; font-size:22px; font-weight:700; margin-top:6px; }
        .stat-box { background:rgba(255,255,255,.025); border:1px solid rgba(255,255,255,.07); border-radius:12px; padding:14px; }
        .review-row { display:flex; justify-content:space-between; align-items:center; gap:12px; padding:11px 12px; border-bottom:1px solid rgba(255,255,255,.055); font-size:12px; }
        .review-expression { font-family:'JetBrains Mono'; font-weight:600; color:rgba(255,255,255,.75); }
        .review-answer { font-family:'JetBrains Mono'; font-size:11px; color:rgba(255,255,255,.4); }
        .review-ok { color:var(--mint); } .review-bad { color:var(--coral); }
        .review-no { color:#ffc875; }
        .footer-note { text-align:center; color:rgba(255,255,255,.22); font-size:10px; margin-top:24px; }
        @media (max-width: 700px) {
            .block-container { padding:1rem; }
            .option-list { grid-template-columns:1fr; }
            .quiz-card { padding:14px; }
            .brand { margin-bottom:1rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">+</div>
            <div>
                <div class="brand-name">Math Quiz</div>
                <div class="brand-sub">Game lab</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def render_welcome():
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown(
            '<div class="pill">✦ A two-minute brain workout</div>'
            '<div class="hero-title">Math Quiz<br><span>Game.</span></div>'
            '<p class="hero-copy">Quick numbers, a ticking clock, and four choices. '
            "Pick your topic, lock in your answers, and see how sharp your mental math really is.</p>"
            '<p class="meta-row">10 QUESTIONS &nbsp;·&nbsp; 20 SECONDS EACH &nbsp;·&nbsp; INSTANT FEEDBACK</p>',
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        best = st.session_state.best_score
        best_copy = "No best score yet — you set the bar today." if best == 0 else f"Personal best: {best} / {TOTAL_QUESTIONS}. Can you beat it?"

        st.markdown(
            f"""
            <div style="display:flex; gap:12px; align-items:center; padding:14px;
                 border:1px solid rgba(255,255,255,.075); border-radius:14px;
                 background:rgba(255,255,255,.025); max-width:480px;">
                <div style="font-size:20px;">🏆</div>
                <div>
                    <div class="section-label" style="margin:0 0 3px">Your personal best</div>
                    <div style="color:rgba(255,255,255,.72);font-size:11px;font-weight:600">{best_copy}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="setup-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div class="setup-title">Set up your round</div>'
            '<div class="setup-sub">Two quick choices, then you are in.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-label" style="margin-top:18px">01 · Choose a topic</div>', unsafe_allow_html=True)

        category_columns = st.columns(5)
        for index, (key, info) in enumerate(CATEGORIES.items()):
            with category_columns[index]:
                if st.button(
                    f"{info['symbol']} {info['label']}",
                    key=f"category_{key}",
                    use_container_width=True,
                    type="primary" if st.session_state.category == key else "secondary",
                ):
                    st.session_state.category = key
                    st.rerun()

        st.markdown('<div class="section-label" style="margin-top:14px">02 · Difficulty</div>', unsafe_allow_html=True)
        difficulty_columns = st.columns(3)
        for index, (key, info) in enumerate(DIFFICULTIES.items()):
            with difficulty_columns[index]:
                if st.button(
                    info["label"],
                    key=f"difficulty_{key}",
                    use_container_width=True,
                    help=info["tagline"],
                    type="primary" if st.session_state.difficulty == key else "secondary",
                ):
                    st.session_state.difficulty = key
                    st.rerun()

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Start the quiz  →", key="start_quiz", use_container_width=True, type="primary"):
            start_quiz()

        st.markdown(
            '<p class="locked-note">10 questions · 4 choices · 1 point each</p>'
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)
    st.markdown("## Pick. Think. Score.")

    step_data = [
        ("01", "◎", "Pick your challenge", "Choose addition, subtraction, multiplication, division, or mixed math."),
        ("02", "◷", "Beat the clock", "You get 20 seconds per question. Your first answer is your final answer."),
        ("03", "★", "Make it count", "Earn one point per correct answer and review your performance at the end."),
    ]
    columns = st.columns(3)
    for column, (number, icon, title, copy) in zip(columns, step_data):
        with column:
            st.markdown(
                f"""
                <div class="how-card">
                    <div style="display:flex;justify-content:space-between">
                        <span class="how-icon">{icon}</span><span class="how-number">{number}</span>
                    </div>
                    <div class="how-title">{title}</div>
                    <div class="how-copy">{copy}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="python-note"><strong style="color:rgba(255,255,255,.8)">College mini project:</strong> '
        "This game is powered by Python 3, the random module, functions, lists, dictionaries, and "
        "Streamlit session state. All questions are generated on the fly — no hard-coded question bank.</div>",
        unsafe_allow_html=True,
    )


@st.fragment(run_every=1.0)
def render_live_timer():
    """Streamlit-native countdown. It refreshes only this small element."""
    if st.session_state.screen != "quiz":
        return
    if st.session_state.selected_answer is not None or st.session_state.timed_out:
        return

    remaining = time_remaining()
    progress = max(0, min(100, int((remaining / QUESTION_TIME) * 100)))
    color = "#ff9c8d" if remaining <= 5 else "#c9f56b"

    st.markdown(
        f"""
        <div class="timer-wrap">
            <div class="timer-ring" style="--progress:{progress}%; background:conic-gradient({color} {progress}%, rgba(255,255,255,.07) 0)">
                <span>{remaining}</span>
            </div>
        </div>
        <div class="timer-label">seconds left</div>
        """,
        unsafe_allow_html=True,
    )

    # When the clock reaches zero, lock the question and count it as missed.
    if remaining <= 0:
        st.session_state.timed_out = True
        st.session_state.selected_answer = None
        st.session_state.time_spent = QUESTION_TIME
        st.rerun()


def render_answered_options(question, selected):
    """Show all four options after answering, with clear colour feedback."""
    option_html = []
    for option in question["options"]:
        css_class = ""
        note = ""
        if option == question["answer"]:
            css_class = "correct"
            note = "Correct answer"
        elif option == selected:
            css_class = "wrong"
            note = "Your answer"
        option_html.append(
            f'<div class="option {css_class}">{option}'
            + (f"<small>{note}</small>" if note else "")
            + "</div>"
        )

    st.markdown(
        f'<div class="option-list">{" ".join(option_html)}</div>',
        unsafe_allow_html=True,
    )


def render_quiz():
    state = st.session_state
    question = current_question()
    answered = state.selected_answer is not None or state.timed_out
    score = calculate_score(state.answers) + (
        1 if state.selected_answer is not None and check_answer(question, state.selected_answer) else 0
    )

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.markdown(
            f'<div class="quiz-top"><span>QUESTION {state.current_index + 1} OF {TOTAL_QUESTIONS}'
            " &nbsp;·&nbsp; "
            f'{CATEGORIES[state.category]["label"]} / {DIFFICULTIES[state.difficulty]["label"]}</span></div>',
            unsafe_allow_html=True,
        )
    with top_right:
        st.markdown(
            f'<div class="quiz-top" style="justify-content:flex-end">SCORE <span class="quiz-score">&nbsp;{score} / {TOTAL_QUESTIONS}</span></div>',
            unsafe_allow_html=True,
        )

    completed = len(state.answers) + (1 if answered else 0)
    st.progress(completed / TOTAL_QUESTIONS)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    with st.container(key="quiz_card"):
        symbol = CATEGORIES[state.category]["symbol"]
        operation = question["operation"].capitalize()
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<div class="q-tag">{symbol} {state.category.capitalize()} · {operation}</div>'
            f'<div class="q-tag" style="color:rgba(255,255,255,.35);background:rgba(255,255,255,.035)">{state.difficulty.upper()}</div>'
            "</div>",
            unsafe_allow_html=True,
        )

        if not answered:
            render_live_timer()
        else:
            st.markdown(
                '<div class="locked-note">Answer locked · this question is complete</div>',
                unsafe_allow_html=True,
            )

        expression_parts = question["expression"].split(" ")
        st.markdown(
            f'<div class="equation-hint">Solve the equation</div>'
            f'<div class="equation">{expression_parts[0]} '
            f'<span class="operator">{expression_parts[1]}</span> '
            f'{expression_parts[2]} <span class="unknown">= ?</span></div>',
            unsafe_allow_html=True,
        )

        if answered:
            render_answered_options(question, state.selected_answer)
        else:
            option_columns = st.columns(2)
            for index, option in enumerate(question["options"]):
                with option_columns[index % 2]:
                    letter = ["A", "B", "C", "D"][index]
                    if st.button(
                        f"{letter}.   {option}",
                        key=f"answer_{option}",
                        use_container_width=True,
                    ):
                        select_answer(option)

        if answered:
            correct = (
                state.selected_answer is not None
                and check_answer(question, state.selected_answer)
            )
            if correct:
                st.markdown(
                    '<div class="feedback correct"><strong>✓ That is correct! +1 point</strong>'
                    f'{question["explanation"]}</div>',
                    unsafe_allow_html=True,
                )
            elif state.timed_out:
                st.markdown(
                    '<div class="feedback timeout"><strong>◷ Time is up!</strong>'
                    f'The correct answer is {question["answer"]}. {question["explanation"]}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="feedback wrong"><strong>✕ Not quite.</strong>'
                    f'The correct answer is {question["answer"]}. {question["explanation"]}</div>',
                    unsafe_allow_html=True,
                )

        button_label = (
            "See my results  →"
            if state.current_index == TOTAL_QUESTIONS - 1
            else "Next question  →"
        )
        if st.button(
            button_label,
            key="next_question",
            use_container_width=True,
            type="primary",
            disabled=not answered,
        ):
            next_question()

    st.markdown(
        '<p class="footer-note">Each question can only be answered once. Accuracy beats speed.</p>',
        unsafe_allow_html=True,
    )

    if st.button("Leave round", key="leave_round"):
        reset_game()


def render_results():
    state = st.session_state
    answers = state.answers
    score = calculate_score(answers)
    total = len(answers)
    percent = round((score / total) * 100) if total else 0
    incorrect = total - score
    average_time = round(sum(item["time_spent"] for item in answers) / total, 1) if total else 0

    if percent >= 90:
        title, message, icon = "Outstanding work!", "You made those numbers look easy. Calculator-level confidence!", "🏆"
    elif percent >= 70:
        title, message, icon = "You have got this!", "A little more practice and a perfect score is within reach.", "🌟"
    elif percent >= 50:
        title, message, icon = "Solid effort!", "A good foundation. Try another round and beat this score.", "💪"
    else:
        title, message, icon = "Every expert starts here.", "Tricky round? Pick a topic and give it another shot.", "🌱"

    left, right = st.columns([0.85, 1.15], gap="large")
    with left:
        st.markdown(
            f"""
            <div class="result-card" style="text-align:center;height:100%">
                <div class="score-circle" style="--score:{percent}%">
                    <div class="score-inner">
                        <div class="score-value">{percent}<span style="font-size:20px;opacity:.35">%</span></div>
                        <div class="score-label">Accuracy</div>
                    </div>
                </div>
                <div style="margin-top:16px;font-family:'JetBrains Mono';font-size:24px;font-weight:700">
                    {score}<span style="color:rgba(255,255,255,.25);font-size:12px"> / {total} correct</span>
                </div>
                <div class="section-label" style="margin-top:16px">
                    {CATEGORIES[state.category]['symbol']} {CATEGORIES[state.category]['label']} · {DIFFICULTIES[state.difficulty]['label']}
                </div>
                <div style="color:rgba(255,255,255,.38);font-size:10px">Personal best: {state.best_score} / {TOTAL_QUESTIONS}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <div style="padding-top:8px">
                <div class="pill">✦ Round complete</div>
                <div class="result-title">{icon} {title}</div>
                <div class="result-copy">{message}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        stat_columns = st.columns(3)
        for column, label, value, colour in zip(
            stat_columns,
            ["Correct", "Missed", "Avg. time"],
            [score, incorrect, f"{average_time}s"],
            ["#7de7c0", "#ff9c8d", "#b7a4ff"],
        ):
            with column:
                st.markdown(
                    f'<div class="stat-box"><div class="stat-label">{label}</div>'
                    f'<div class="stat-value" style="color:{colour}">{value}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        action_left, action_right = st.columns(2)
        with action_left:
            if st.button("Play again  ↻", key="play_again", use_container_width=True, type="primary"):
                play_again()
        with action_right:
            if st.button("Change category", key="change_setup", use_container_width=True):
                reset_game()

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    with st.expander("Review all 10 answers", expanded=True):
        for index, item in enumerate(answers, start=1):
            question = item["question"]
            if item["correct"]:
                result_text = f'<span class="review-ok">✓ Correct ({question["answer"]})</span>'
            elif item["timed_out"]:
                result_text = f'<span class="review-no">◷ No answer · {question["answer"]}</span>'
            else:
                result_text = f'<span class="review-bad">✕ You chose {item["selected"]} · {question["answer"]}</span>'
            st.markdown(
                f'<div class="review-row"><span class="review-answer">{index:02d}</span>'
                f'<span class="review-expression" style="flex:1">{question["expression"]}</span>'
                f"{result_text}</div>",
                unsafe_allow_html=True,
            )

    if st.button("Back to welcome", key="results_home"):
        reset_game()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Control which screen is shown and keep the game state valid."""
    configure_page()
    inject_css()
    initialize_game()
    render_header()

    if st.session_state.screen == "welcome":
        render_welcome()
    elif st.session_state.screen == "quiz":
        if not st.session_state.questions:
            reset_game()
        else:
            render_quiz()
    elif st.session_state.screen == "results":
        render_results()
    else:
        reset_game()


if __name__ == "__main__":
    main()
