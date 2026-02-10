# streamlit_gemini_interviewer.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# ---------------------- CONFIG ----------------------

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ API key not found. Please set GEMINI_API_KEY in your .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=API_KEY)

# Load Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


# ---------------------- HELPERS ------  ----------------

def generate_question(topic: str, difficulty: str) -> str:
    prompt = f"""
You are an interviewer. Generate ONE concise interview question for this topic:
Topic: {topic}
Difficulty: {difficulty}

Do NOT give explanations — only output the question.
"""
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"[Error generating question: {e}]"


def evaluate_answer(question: str, answer: str) -> str:
    prompt = f"""
You are an expert interviewer evaluating a candidate's answer.

Question: {question}
Answer: {answer}

Provide:
1) One-line evaluation (strengths/weaknesses)
2) A score out of 10
3) One short improvement tip
"""
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"[Error evaluating answer: {e}]"


# ---------------------- STREAMLIT UI ----------------------

# ---------------------- STREAMLIT GAME UI ----------------------

import streamlit as st
import time

st.set_page_config(page_title="AI Interview Game", page_icon="🎮", layout="wide")

# ---------------------- CUSTOM CSS ----------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #1e1f26, #2e3250);
    color: white;
}
.big-title {
    font-size: 45px;
    font-weight: 800;
    text-align: center;
    color: #00eaff;
}
.game-card {
    background: rgba(255,255,255,0.05);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
}
.badge {
    background: #ffc107;
    padding: 10px 20px;
    border-radius: 20px;
    font-weight: bold;
    color: black;
}
.progress-container {
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- SESSION STATE ----------------------
# ---------------------- SESSION STATE ----------------------
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "level" not in st.session_state:
    st.session_state.level = 1
if "badges" not in st.session_state:
    st.session_state.badges = 0
if "xp" not in st.session_state:
    st.session_state.xp = 0

# Question storage
num_questions = 10  # or dynamic slider if you use one

if "questions" not in st.session_state:
    st.session_state.questions = [None] * num_questions
if "answers" not in st.session_state:
    st.session_state.answers = [""] * num_questions
if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = [None] * num_questions


# Unlock logic
def update_progress():
    st.session_state.xp += 20   # each question = 20 xp
    if st.session_state.xp >= 100:
        st.session_state.xp = 0
        st.session_state.level += 1
        st.success(f"🎉 LEVEL UP! You reached Level {st.session_state.level}!")
        st.balloons()

    # Badge reward every 3 questions
    if (st.session_state.q_index + 1) % 3 == 0:
        st.session_state.badges += 1
        st.info(f"🏅 Badge Earned! Total Badges: {st.session_state.badges}")

# ---------------------- HEADER ----------------------
st.markdown("<div class='big-title'>🎮 AI Interview Adventure</div>", unsafe_allow_html=True)
st.write("Answer questions, gain XP, earn badges & unlock levels!")

# ---------------------- GAME HUD ----------------------
hud1, hud2, hud3 = st.columns(3)

with hud1:
    st.metric("Level", st.session_state.level)

with hud2:
    st.metric("Badges", st.session_state.badges)

with hud3:
    st.metric("XP", f"{st.session_state.xp}/100")

st.progress(st.session_state.xp / 100)

st.markdown("---")

# ---------------------- SETTINGS ----------------------
left, right = st.columns([2, 1])

with left:
    topic = st.selectbox("🎯 Choose Topic", [
        "AI/ML", "Python", "System Design", "Data Structures",
        "Web Dev", "Behavioral"
    ])

with right:
    difficulty = st.selectbox("🔥 Difficulty", ["Easy", "Medium", "Hard"], index=1)


# ---------------------- QUESTION AREA ----------------------
st.subheader(f"Question {st.session_state.q_index + 1}")

if st.button("🎲 Generate Question"):
    with st.spinner("Thinking..."):
        q = generate_question(topic, difficulty)
        st.session_state.questions[st.session_state.q_index] = q

if st.session_state.questions[st.session_state.q_index]:
    st.markdown(f"<div class='game-card'>{st.session_state.questions[st.session_state.q_index]}</div>", 
                unsafe_allow_html=True)

# Answer input
answer = st.text_area("✏️ Your Answer", height=150)
st.session_state.answers[st.session_state.q_index] = answer

# Evaluate
if st.button("⚡ Evaluate Answer"):
    if not answer.strip():
        st.warning("Please enter an answer!")
    else:
        with st.spinner("Evaluating..."):
            fb = evaluate_answer(
                st.session_state.questions[st.session_state.q_index],
                answer
            )
            st.session_state.feedbacks[st.session_state.q_index] = fb
            update_progress()

# Show feedback
if st.session_state.feedbacks[st.session_state.q_index]:
    st.markdown("### 🧠 Feedback")
    st.markdown(f"<div class='game-card'>{st.session_state.feedbacks[st.session_state.q_index]}</div>",
                unsafe_allow_html=True)


# ---------------------- NAVIGATION ----------------------
n1, n2, n3 = st.columns(3)

if n1.button("⬅️ Previous"):
    st.session_state.q_index = max(0, st.session_state.q_index - 1)

if n2.button("➡️ Next"):
    st.session_state.q_index = min(num_questions - 1, st.session_state.q_index + 1)

if n3.button("🔄 Reset Game"):
    for k in ("q_index", "level", "xp", "badges", "questions", "answers", "feedbacks"):
        st.session_state.pop(k, None)
    st.rerun()
