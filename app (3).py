import streamlit as st
from huggingface_hub import InferenceClient
import json
import time
import random

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InterviewIQ – AI Interview Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
    --bg:        #0b0c10;
    --surface:   #13141a;
    --card:      #1a1c25;
    --border:    #2a2d3a;
    --accent:    #7fff6e;
    --accent2:   #4af0c4;
    --danger:    #ff5e5e;
    --warn:      #ffc94a;
    --text:      #e8eaf0;
    --muted:     #6b7280;
    --radius:    12px;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Headings */
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #0b0c10 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.6rem !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(127,255,110,0.3) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background: var(--card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}

/* Text inputs / text areas */
.stTextArea textarea, .stTextInput input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(127,255,110,0.15) !important;
}

/* Select boxes */
.stSelectbox select, [data-baseweb="select"] {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: var(--radius) !important;
}
[data-baseweb="select"] > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}

/* Custom card */
.iq-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.iq-card.accent { border-left: 3px solid var(--accent); }
.iq-card.danger  { border-left: 3px solid var(--danger); }
.iq-card.warn    { border-left: 3px solid var(--warn); }
.iq-card.info    { border-left: 3px solid var(--accent2); }

.score-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 2.4rem;
    font-weight: 500;
    color: var(--accent);
}
.score-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.tag {
    display: inline-block;
    background: rgba(127,255,110,0.1);
    color: var(--accent);
    border: 1px solid rgba(127,255,110,0.2);
    border-radius: 999px;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    padding: 2px 10px;
    margin: 2px;
}
.tag.red   { background: rgba(255,94,94,0.1); color: var(--danger); border-color: rgba(255,94,94,0.2); }
.tag.yellow{ background: rgba(255,201,74,0.1); color: var(--warn); border-color: rgba(255,201,74,0.2); }
.tag.blue  { background: rgba(74,240,196,0.1); color: var(--accent2); border-color: rgba(74,240,196,0.2); }

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #7fff6e 0%, #4af0c4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.5rem 0;
}

.question-box {
    background: linear-gradient(135deg, rgba(127,255,110,0.05), rgba(74,240,196,0.05));
    border: 1px solid rgba(127,255,110,0.2);
    border-radius: var(--radius);
    padding: 1.5rem;
    font-family: 'DM Sans', sans-serif;
    font-size: 1.1rem;
    font-weight: 500;
    color: var(--text);
    margin-bottom: 1rem;
}

.progress-bar-bg {
    background: var(--border);
    border-radius: 999px;
    height: 6px;
    margin: 8px 0 4px;
}
.progress-bar-fill {
    border-radius: 999px;
    height: 6px;
}

/* Spinner override */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Expander */
.streamlit-expanderHeader {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    color: var(--muted) !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hugging Face client ───────────────────────────────────────────────────────
HF_TOKEN = st.secrets.get("HF_TOKEN", None)
HF_MODEL  = "mistralai/Mistral-7B-Instruct-v0.3"
client = InferenceClient(model=HF_MODEL, token=HF_TOKEN)

# ── Question bank ─────────────────────────────────────────────────────────────
QUESTION_BANK = {
    "Software Engineering": {
        "Behavioral": [
            "Tell me about a time you debugged a complex production issue under time pressure.",
            "Describe a situation where you had to push back on a product requirement. How did you handle it?",
            "Tell me about a project where you had to learn a new technology quickly. What was your approach?",
            "Describe a time when you disagreed with a technical decision made by your team. What did you do?",
            "Give an example of when you improved an existing codebase or process significantly.",
        ],
        "Technical": [
            "Explain the difference between horizontal and vertical scaling. When would you use each?",
            "Walk me through how you'd design a URL shortener service.",
            "What is the difference between REST and GraphQL? When would you choose one over the other?",
            "Explain how you'd approach optimizing a slow database query.",
            "What are SOLID principles? Give an example of one in practice.",
        ],
    },
    "Data Science": {
        "Behavioral": [
            "Tell me about a time your model performed poorly in production. How did you diagnose and fix it?",
            "Describe a project where you had to communicate complex results to non-technical stakeholders.",
            "Give an example of a time you had to work with messy, incomplete data.",
            "Tell me about a time you identified a business insight that led to a significant decision.",
            "Describe a situation where you had to prioritize between multiple competing analysis requests.",
        ],
        "Technical": [
            "Explain the bias-variance tradeoff and how it affects model selection.",
            "How would you handle class imbalance in a binary classification problem?",
            "Walk me through how you'd build a recommendation system from scratch.",
            "What is the difference between bagging and boosting? Give examples of each.",
            "How do you prevent overfitting in a neural network?",
        ],
    },
    "Product Management": {
        "Behavioral": [
            "Tell me about a product you launched. What was your role and what was the outcome?",
            "Describe a time you had to make a difficult prioritization decision. How did you approach it?",
            "Tell me about a time a product you worked on failed. What did you learn?",
            "Give an example of how you used data to drive a product decision.",
            "Describe a situation where you had to align stakeholders with conflicting priorities.",
        ],
        "Technical": [
            "How would you define and measure success for a new onboarding flow?",
            "Walk me through how you'd prioritize a backlog of 50 feature requests.",
            "How would you design a notification system for a mobile app to maximize engagement without annoying users?",
            "Explain how you'd approach A/B testing a new checkout flow.",
            "How would you decide whether to build, buy, or partner for a new capability?",
        ],
    },
    "Cybersecurity": {
        "Behavioral": [
            "Tell me about a security incident you handled. What was your response process?",
            "Describe a time you had to balance security requirements with usability. How did you resolve it?",
            "Give an example of a security risk you identified before it became a problem.",
            "Tell me about a time you had to educate non-technical colleagues about security practices.",
            "Describe a situation where you had to make a security trade-off under time pressure.",
        ],
        "Technical": [
            "Explain the difference between authentication and authorization.",
            "Walk me through how you'd approach a penetration test on a web application.",
            "What is SQL injection and how do you prevent it?",
            "Explain how TLS/SSL works and why it's important.",
            "How would you design a secure password storage system?",
        ],
    },
    "General / Any Role": {
        "Behavioral": [
            "Tell me about yourself and why you're interested in this role.",
            "Describe a time you had to work with a difficult teammate. How did you handle it?",
            "Tell me about a significant challenge you overcame. What did you learn?",
            "Give an example of a time you went above and beyond what was expected.",
            "Where do you see yourself in 5 years?",
        ],
        "Technical": [
            "What's your greatest professional strength and how have you applied it?",
            "How do you stay current with trends in your field?",
            "Describe your ideal working environment and team structure.",
            "How do you manage competing deadlines and priorities?",
            "What questions do you have for us?",
        ],
    },
}

DIFFICULTY_LEVELS = ["Entry Level", "Mid Level", "Senior Level"]

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "page": "home",
        "role": "Software Engineering",
        "q_type": "Behavioral",
        "difficulty": "Mid Level",
        "current_question": None,
        "answer": "",
        "feedback": None,
        "history": [],
        "session_scores": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ───────────────────────────────────────────────────────────────────
def pick_question():
    pool = QUESTION_BANK[st.session_state.role][st.session_state.q_type]
    used = [h["question"] for h in st.session_state.history]
    unused = [q for q in pool if q not in used]
    if not unused:
        unused = pool
    st.session_state.current_question = random.choice(unused)
    st.session_state.answer = ""
    st.session_state.feedback = None

def score_color(score):
    if score >= 80: return "#7fff6e"
    if score >= 60: return "#ffc94a"
    return "#ff5e5e"

def score_emoji(score):
    if score >= 80: return "🟢"
    if score >= 60: return "🟡"
    return "🔴"

def get_feedback(question, answer, role, q_type, difficulty):
    prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

Role applied for: {role}
Question type: {q_type}
Difficulty level: {difficulty}

Interview Question:
{question}

Candidate's Answer:
{answer}

Evaluate the answer and respond ONLY with a valid JSON object (no markdown, no backticks) with exactly this structure:
{{
  "overall_score": <integer 0-100>,
  "dimension_scores": {{
    "clarity": <integer 0-100>,
    "depth": <integer 0-100>,
    "relevance": <integer 0-100>,
    "structure": <integer 0-100>
  }},
  "strengths": [<2-3 specific strings about what was done well>],
  "improvements": [<2-3 specific actionable strings about what to improve>],
  "ideal_answer_outline": "<2-4 sentence outline of what a strong answer would cover>",
  "keywords_used": [<list of strong keywords/phrases the candidate used>],
  "keywords_missing": [<list of important keywords/frameworks they should have mentioned>],
  "verdict": "<one of: Excellent, Strong, Needs Work, Insufficient>"
}}"""

    messages = [
        {"role": "system", "content": "You are an expert technical interviewer. Always respond with valid JSON only — no markdown, no backticks, no extra text."},
        {"role": "user",   "content": prompt},
    ]
    response = client.chat_completion(messages=messages, max_tokens=1000, temperature=0.3)
    raw = response.choices[0].message.content.strip()
    # Strip accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="hero-title" style="font-size:1.6rem;">InterviewIQ</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b7280;font-size:0.85rem;margin-top:-0.5rem;">AI Interview Coach</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("**🎯 Target Role**")
    st.session_state.role = st.selectbox(
        "Role", list(QUESTION_BANK.keys()), label_visibility="collapsed"
    )

    st.markdown("**📋 Question Type**")
    st.session_state.q_type = st.selectbox(
        "Type", ["Behavioral", "Technical"], label_visibility="collapsed"
    )

    st.markdown("**⚡ Difficulty**")
    st.session_state.difficulty = st.selectbox(
        "Difficulty", DIFFICULTY_LEVELS, index=1, label_visibility="collapsed"
    )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # Session stats
    if st.session_state.session_scores:
        avg = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
        st.markdown(f"""
        <div class="iq-card" style="padding:1rem;">
          <div class="score-label">Session Stats</div>
          <div class="score-badge" style="font-size:1.8rem;">{avg:.0f}</div>
          <span style="color:#6b7280;font-size:0.8rem;"> avg score</span>
          <br>
          <span style="color:#6b7280;font-size:0.8rem;">📝 {len(st.session_state.history)} answered</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="color:#6b7280;font-size:0.85rem;text-align:center;padding:1rem;">
        No questions answered yet.<br>Start practicing! 🚀
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️ Reset Session", use_container_width=True):
        st.session_state.history = []
        st.session_state.session_scores = []
        st.session_state.current_question = None
        st.session_state.feedback = None
        st.rerun()

# ── Main content ──────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🎤  Practice", "📊  History"])

# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<h1 class="hero-title">Interview<br>Coaching.</h1>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="color:#6b7280;margin-top:0.25rem;">Practicing <span style="color:#e8eaf0;">{st.session_state.q_type}</span> '
            f'questions for <span style="color:#e8eaf0;">{st.session_state.role}</span> '
            f'at <span style="color:#e8eaf0;">{st.session_state.difficulty}</span>.</p>',
            unsafe_allow_html=True
        )

        if st.button("✦ Get a Question", use_container_width=False):
            pick_question()

        if st.session_state.current_question:
            st.markdown(f'<div class="question-box">💬 {st.session_state.current_question}</div>', unsafe_allow_html=True)

            answer = st.text_area(
                "Your Answer",
                value=st.session_state.answer,
                height=200,
                placeholder="Type your answer here. Aim for 2-4 minutes of speech (roughly 200-400 words)…",
                key="answer_input",
            )
            st.session_state.answer = answer

            word_count = len(answer.split()) if answer.strip() else 0
            wc_color = "#7fff6e" if 150 <= word_count <= 500 else ("#ffc94a" if word_count > 0 else "#6b7280")
            st.markdown(f'<span style="color:{wc_color};font-family:\'DM Mono\',monospace;font-size:0.8rem;">📝 {word_count} words</span>', unsafe_allow_html=True)

            col_btn1, col_btn2 = st.columns([2, 1])
            with col_btn1:
                submit = st.button("🔍 Analyze My Answer", use_container_width=True, disabled=word_count < 20)
            with col_btn2:
                if st.button("⟳ New Question", use_container_width=True):
                    pick_question()
                    st.rerun()

            if submit and word_count >= 20:
                with st.spinner("Analyzing your answer…"):
                    try:
                        fb = get_feedback(
                            st.session_state.current_question,
                            answer,
                            st.session_state.role,
                            st.session_state.q_type,
                            st.session_state.difficulty,
                        )
                        st.session_state.feedback = fb
                        st.session_state.session_scores.append(fb["overall_score"])
                        st.session_state.history.insert(0, {
                            "question": st.session_state.current_question,
                            "answer": answer,
                            "feedback": fb,
                            "role": st.session_state.role,
                            "type": st.session_state.q_type,
                        })
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

        else:
            st.markdown("""
            <div class="iq-card" style="text-align:center;padding:3rem 2rem;">
                <div style="font-size:3rem;margin-bottom:1rem;">🎯</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;">Ready to practice?</div>
                <div style="color:#6b7280;margin-top:0.5rem;font-size:0.9rem;">Hit "Get a Question" to start your session.</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Feedback panel ────────────────────────────────────────────────────────
    with col_right:
        if st.session_state.feedback:
            fb = st.session_state.feedback
            score = fb["overall_score"]
            verdict = fb["verdict"]
            sc = score_color(score)

            st.markdown(f"""
            <div class="iq-card" style="text-align:center;padding:1.5rem;">
                <div class="score-label">Overall Score</div>
                <div class="score-badge" style="color:{sc};">{score}</div>
                <div style="font-size:0.7rem;color:#6b7280;">/100</div>
                <div style="margin-top:0.5rem;">
                    <span class="tag" style="background:rgba(127,255,110,0.1);color:{sc};border-color:rgba(127,255,110,0.2);">{verdict}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Dimension scores
            st.markdown('<div class="iq-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.75rem;">Dimensions</div>', unsafe_allow_html=True)
            for dim, val in fb["dimension_scores"].items():
                c = score_color(val)
                pct = val
                st.markdown(f"""
                <div style="margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-size:0.82rem;text-transform:capitalize;">{dim}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:{c};">{val}</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width:{pct}%;background:{c};"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Strengths
            if fb.get("strengths"):
                st.markdown('<div class="iq-card accent">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.5rem;">✅ Strengths</div>', unsafe_allow_html=True)
                for s in fb["strengths"]:
                    st.markdown(f'<div style="font-size:0.85rem;margin-bottom:0.4rem;color:#b0b8c8;">• {s}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Improvements
            if fb.get("improvements"):
                st.markdown('<div class="iq-card warn">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.5rem;">⚡ Improve</div>', unsafe_allow_html=True)
                for s in fb["improvements"]:
                    st.markdown(f'<div style="font-size:0.85rem;margin-bottom:0.4rem;color:#b0b8c8;">• {s}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Keywords
            kw_used = fb.get("keywords_used", [])
            kw_miss = fb.get("keywords_missing", [])
            if kw_used or kw_miss:
                st.markdown('<div class="iq-card info">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.5rem;">🔑 Keywords</div>', unsafe_allow_html=True)
                if kw_used:
                    tags = " ".join([f'<span class="tag">{k}</span>' for k in kw_used[:6]])
                    st.markdown(f'<div style="margin-bottom:0.4rem;">{tags}</div>', unsafe_allow_html=True)
                if kw_miss:
                    tags = " ".join([f'<span class="tag red">{k}</span>' for k in kw_miss[:6]])
                    st.markdown(f'<div style="font-size:0.75rem;color:#6b7280;margin-bottom:0.25rem;">Missing:</div>{tags}', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Ideal outline
            if fb.get("ideal_answer_outline"):
                with st.expander("💡 Model Answer Outline"):
                    st.markdown(f'<div style="font-size:0.88rem;color:#b0b8c8;line-height:1.6;">{fb["ideal_answer_outline"]}</div>', unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style="padding-top:6rem;text-align:center;color:#3a3d4a;">
                <div style="font-size:4rem;">📋</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;margin-top:1rem;">Feedback appears<br>after you submit an answer.</div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<h2 style="font-family:\'Syne\',sans-serif;font-weight:800;">Session History</h2>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class="iq-card" style="text-align:center;padding:3rem;">
            <div style="font-size:2.5rem;">📭</div>
            <div style="font-family:'Syne',sans-serif;margin-top:0.75rem;">No history yet.</div>
            <div style="color:#6b7280;font-size:0.88rem;">Answer some questions in the Practice tab.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary bar
        avg = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
        best = max(st.session_state.session_scores)
        worst = min(st.session_state.session_scores)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Questions", len(st.session_state.history))
        c2.metric("Avg Score", f"{avg:.0f}")
        c3.metric("Best", best)
        c4.metric("Needs Work", worst)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.history):
            fb = item["feedback"]
            score = fb["overall_score"]
            sc = score_color(score)
            emoji = score_emoji(score)

            with st.expander(f"{emoji} Q{len(st.session_state.history)-i}: {item['question'][:70]}… — Score: {score}/100"):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown(f"**Your Answer:**")
                    st.markdown(f'<div style="background:var(--card);border-radius:8px;padding:1rem;font-size:0.88rem;color:#b0b8c8;border:1px solid var(--border);">{item["answer"]}</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:2rem;color:{sc};text-align:center;">{score}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="text-align:center;color:#6b7280;font-size:0.8rem;">{fb["verdict"]}</div>', unsafe_allow_html=True)
                    if fb.get("strengths"):
                        st.markdown("**Strengths:**")
                        for s in fb["strengths"]:
                            st.markdown(f"- {s}")
