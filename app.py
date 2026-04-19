import streamlit as st
from huggingface_hub import InferenceClient
import json
import random
import io

# ── Page config ───────────────────────────────────────────────────────────────
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
    --bg:      #0b0c10;
    --surface: #13141a;
    --card:    #1a1c25;
    --border:  #2a2d3a;
    --accent:  #7fff6e;
    --accent2: #4af0c4;
    --danger:  #ff5e5e;
    --warn:    #ffc94a;
    --text:    #e8eaf0;
    --muted:   #6b7280;
    --radius:  12px;
}
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

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
[data-baseweb="select"] > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
}
[data-testid="metric-container"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}
.iq-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    margin-bottom: 1rem;
}
.iq-card.accent { border-left: 3px solid var(--accent); }
.iq-card.warn   { border-left: 3px solid var(--warn); }
.iq-card.info   { border-left: 3px solid var(--accent2); }
.iq-card.danger { border-left: 3px solid var(--danger); }

.score-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 2.4rem;
    font-weight: 500;
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
.tag.red  { background: rgba(255,94,94,0.1);  color: var(--danger);  border-color: rgba(255,94,94,0.2); }
.tag.blue { background: rgba(74,240,196,0.1); color: var(--accent2); border-color: rgba(74,240,196,0.2); }

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
.divider { border: none; border-top: 1px solid var(--border); margin: 1.2rem 0; }
.question-box {
    background: linear-gradient(135deg, rgba(127,255,110,0.05), rgba(74,240,196,0.05));
    border: 1px solid rgba(127,255,110,0.2);
    border-radius: var(--radius);
    padding: 1.5rem;
    font-size: 1.1rem;
    font-weight: 500;
    margin-bottom: 1rem;
}
.progress-bar-bg   { background: var(--border); border-radius: 999px; height: 6px; margin: 8px 0 4px; }
.progress-bar-fill { border-radius: 999px; height: 6px; }
.stSpinner > div   { border-top-color: var(--accent) !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-bottom: 1px solid var(--border) !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Syne', sans-serif !important; font-weight: 600 !important; color: var(--muted) !important; background: transparent !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; }
.token-hint { font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "hf_token": "",
        "q_type": "Behavioral",
        "difficulty": "Mid Level",
        "current_question": None,
        "feedback": None,
        "history": [],
        "session_scores": [],
        "resume_text": "",
        "jd_text": "",
        "generated_questions": [],
        "question_source": "bank",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Fallback question bank ────────────────────────────────────────────────────
QUESTION_BANK = {
    "Behavioral": [
        "Tell me about a time you had to learn something new quickly under pressure.",
        "Describe a situation where you disagreed with a team decision. How did you handle it?",
        "Give an example of a time you went above and beyond what was expected.",
        "Tell me about a time you failed. What did you learn from it?",
        "Describe how you prioritize when you have multiple competing deadlines.",
        "Tell me about a successful collaboration with a cross-functional team.",
    ],
    "Technical": [
        "Walk me through how you'd approach designing a scalable web application.",
        "Explain a complex technical concept you know well to a non-technical audience.",
        "How do you ensure the quality of your work before shipping?",
        "Describe your debugging process when you encounter an unfamiliar bug.",
        "What's the most technically challenging project you've worked on?",
        "How do you stay current with new tools and technologies in your field?",
    ],
}
DIFFICULTY_LEVELS = ["Entry Level", "Mid Level", "Senior Level"]

# ── Core helpers ──────────────────────────────────────────────────────────────
def get_client():
    token = st.session_state.hf_token.strip()
    if not token:
        return None
    return InferenceClient(model="mistralai/Mistral-7B-Instruct-v0.3", token=token)

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    raw = uploaded_file.read()
    if uploaded_file.name.lower().endswith(".pdf"):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(raw))
            return "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception:
            pass
    return raw.decode("utf-8", errors="ignore")

def score_color(s):
    return "#7fff6e" if s >= 80 else ("#ffc94a" if s >= 60 else "#ff5e5e")

def score_emoji(s):
    return "🟢" if s >= 80 else ("🟡" if s >= 60 else "🔴")

def clear_answer():
    if "answer_input" in st.session_state:
        del st.session_state["answer_input"]
    st.session_state.feedback = None

def call_llm(client, system_msg, user_msg, max_tokens=1200, temp=0.4):
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg},
        ],
        max_tokens=max_tokens,
        temperature=temp,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()

def generate_questions(client, jd_text, resume_text, q_type, difficulty, n=6):
    context = f"Job Description:\n{jd_text}\n"
    if resume_text:
        context += f"\nCandidate Resume:\n{resume_text}\n"
    system = "You are a senior technical interviewer. Respond ONLY with a valid JSON array of strings. No markdown, no backticks, no extra text."
    user = (
        f"Based on the following context, generate exactly {n} {q_type} interview questions "
        f"at {difficulty} difficulty.\nReturn ONLY a JSON array of {n} question strings.\n\n"
        f"{context}\n\nExample format: [\"Question 1?\", \"Question 2?\"]"
    )
    raw = call_llm(client, system, user, max_tokens=800, temp=0.7)
    questions = json.loads(raw)
    return [q.strip() for q in questions if q.strip()][:n]

def get_feedback(client, question, answer, q_type, difficulty, jd_text="", resume_text=""):
    ctx = ""
    if jd_text:
        ctx += f"\nJob Description context:\n{jd_text[:500]}\n"
    if resume_text:
        ctx += f"\nCandidate background:\n{resume_text[:400]}\n"
    system = "You are an expert technical interviewer. Always respond with valid JSON only — no markdown, no backticks, no extra text."
    user = f"""Evaluate this interview answer.

Question type: {q_type}
Difficulty: {difficulty}{ctx}

Question: {question}

Candidate's Answer: {answer}

Respond ONLY with this exact JSON:
{{
  "overall_score": <integer 0-100>,
  "dimension_scores": {{"clarity": <int>, "depth": <int>, "relevance": <int>, "structure": <int>}},
  "strengths": ["<strength 1>", "<strength 2>"],
  "improvements": ["<improvement 1>", "<improvement 2>"],
  "ideal_answer_outline": "<2-4 sentences on what a strong answer covers>",
  "keywords_used": ["<kw1>", "<kw2>"],
  "keywords_missing": ["<missing1>", "<missing2>"],
  "verdict": "<Excellent|Strong|Needs Work|Insufficient>"
}}"""
    raw = call_llm(client, system, user, max_tokens=1000, temp=0.3)
    return json.loads(raw)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="hero-title" style="font-size:1.5rem;">InterviewIQ</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b7280;font-size:0.8rem;margin-top:-0.5rem;">AI Interview Coach</p>', unsafe_allow_html=True)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("**🔑 Hugging Face Token**")
    hf_token_input = st.text_input(
        "HF Token",
        value=st.session_state.hf_token,
        type="password",
        placeholder="hf_xxxxxxxxxxxxxxxxxxxx",
        label_visibility="collapsed",
        key="hf_token_widget",
    )
    st.session_state.hf_token = hf_token_input

    if not hf_token_input:
        st.markdown(
            '<div class="token-hint">🔗 Get a free token at '
            '<a href="https://huggingface.co/settings/tokens" target="_blank" style="color:#7fff6e;">'
            'huggingface.co/settings/tokens</a></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="token-hint" style="color:#7fff6e;">✓ Token set</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("**📋 Question Type**")
    st.session_state.q_type = st.selectbox("Type", ["Behavioral", "Technical"], label_visibility="collapsed")

    st.markdown("**⚡ Difficulty**")
    st.session_state.difficulty = st.selectbox("Difficulty", DIFFICULTY_LEVELS, index=1, label_visibility="collapsed")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if st.session_state.session_scores:
        avg = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
        st.markdown(f"""
        <div class="iq-card" style="padding:1rem;">
          <div class="score-label">Session Stats</div>
          <div class="score-badge" style="color:#7fff6e;font-size:1.8rem;">{avg:.0f}</div>
          <span style="color:#6b7280;font-size:0.8rem;"> avg score</span><br>
          <span style="color:#6b7280;font-size:0.8rem;">📝 {len(st.session_state.history)} answered</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    if st.button("🗑️ Reset Session", use_container_width=True):
        for k in ["history", "session_scores", "generated_questions"]:
            st.session_state[k] = []
        for k in ["current_question", "feedback"]:
            st.session_state[k] = None
        for k in ["resume_text", "jd_text"]:
            st.session_state[k] = ""
        st.session_state.question_source = "bank"
        clear_answer()
        st.rerun()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📄  Setup & Questions", "🎤  Practice", "📊  History"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Setup
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<h2 style="font-family:\'Syne\',sans-serif;font-weight:800;margin-bottom:0.25rem;">Set Up Your Session</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color:#6b7280;margin-bottom:1.5rem;">Upload a job description (and optionally your resume) to get AI-personalized interview questions.</p>', unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")

    with col_l:
        st.markdown("### 📋 Job Description")
        st.markdown('<p style="color:#6b7280;font-size:0.85rem;">Required — upload a file or paste text.</p>', unsafe_allow_html=True)

        jd_file = st.file_uploader("Upload JD", type=["txt", "pdf"], key="jd_file", label_visibility="collapsed")
        if jd_file:
            extracted = extract_text_from_file(jd_file)
            if extracted.strip():
                st.session_state.jd_text = extracted
                st.success(f"✓ Loaded {len(extracted.split())} words from {jd_file.name}")

        st.session_state.jd_text = st.text_area(
            "Or paste JD here",
            value=st.session_state.jd_text,
            height=220,
            placeholder="Paste the full job description here…",
            key="jd_paste",
        )

    with col_r:
        st.markdown("### 📄 Resume *(optional)*")
        st.markdown('<p style="color:#6b7280;font-size:0.85rem;">Upload for questions tailored to your background.</p>', unsafe_allow_html=True)

        resume_file = st.file_uploader("Upload Resume", type=["txt", "pdf"], key="resume_file", label_visibility="collapsed")
        if resume_file:
            extracted = extract_text_from_file(resume_file)
            if extracted.strip():
                st.session_state.resume_text = extracted
                st.success(f"✓ Loaded {len(extracted.split())} words from {resume_file.name}")

        st.session_state.resume_text = st.text_area(
            "Or paste resume here",
            value=st.session_state.resume_text,
            height=220,
            placeholder="Paste your resume text here (optional)…",
            key="resume_paste",
        )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    has_jd    = bool(st.session_state.jd_text.strip())
    has_token = bool(st.session_state.hf_token.strip())

    if not has_token:
        st.warning("⚠️ Enter your Hugging Face token in the sidebar first.")
    elif not has_jd:
        st.info("💡 Add a job description above, then click Generate.")

    btn_gen, btn_skip = st.columns([2, 1])
    with btn_gen:
        if st.button("✦ Generate Personalized Questions", disabled=not (has_jd and has_token), use_container_width=True):
            client = get_client()
            with st.spinner("Generating questions tailored to the role…"):
                try:
                    qs = generate_questions(
                        client,
                        st.session_state.jd_text,
                        st.session_state.resume_text,
                        st.session_state.q_type,
                        st.session_state.difficulty,
                        n=6,
                    )
                    st.session_state.generated_questions = qs
                    st.session_state.question_source = "generated"
                    st.success(f"✓ Generated {len(qs)} personalized questions! Head to the Practice tab.")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

    with btn_skip:
        if st.button("Use General Questions →", use_container_width=True):
            st.session_state.question_source = "bank"
            st.session_state.generated_questions = []
            st.info("Using built-in question bank. Head to the Practice tab.")

    if st.session_state.generated_questions:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("**Generated Questions Preview:**")
        for i, q in enumerate(st.session_state.generated_questions, 1):
            st.markdown(f"""
            <div class="iq-card" style="padding:1rem;margin-bottom:0.5rem;">
                <span style="font-family:'DM Mono',monospace;color:#6b7280;font-size:0.8rem;">Q{i}</span><br>
                <span style="font-size:0.95rem;">{q}</span>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Practice
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<h1 class="hero-title">Interview<br>Coaching.</h1>', unsafe_allow_html=True)
        source_label = "personalized" if (st.session_state.question_source == "generated" and st.session_state.generated_questions) else "general"
        st.markdown(
            f'<p style="color:#6b7280;margin-top:0.25rem;">Using <span style="color:#e8eaf0;">{source_label}</span> '
            f'<span style="color:#e8eaf0;">{st.session_state.q_type}</span> questions at '
            f'<span style="color:#e8eaf0;">{st.session_state.difficulty}</span>.</p>',
            unsafe_allow_html=True,
        )

        if not has_token:
            st.markdown('<div class="iq-card danger">⚠️ <b>No HF token set.</b> Enter it in the sidebar to enable AI analysis.</div>', unsafe_allow_html=True)

        def pick_question():
            if st.session_state.question_source == "generated" and st.session_state.generated_questions:
                pool = st.session_state.generated_questions
            else:
                pool = QUESTION_BANK[st.session_state.q_type]
            used   = [h["question"] for h in st.session_state.history]
            unused = [q for q in pool if q not in used] or pool
            st.session_state.current_question = random.choice(unused)
            clear_answer()

        if st.button("✦ Get a Question", use_container_width=False):
            pick_question()

        if st.session_state.current_question:
            st.markdown(f'<div class="question-box">💬 {st.session_state.current_question}</div>', unsafe_allow_html=True)

            st.text_area(
                "Your Answer",
                height=200,
                placeholder="Type your answer here. Aim for 2-4 minutes of speech (roughly 200-400 words)…",
                key="answer_input",
            )
            answer     = st.session_state.get("answer_input", "")
            word_count = len(answer.split()) if answer.strip() else 0
            wc_color   = "#7fff6e" if 150 <= word_count <= 500 else ("#ffc94a" if word_count > 0 else "#6b7280")
            st.markdown(f'<span style="color:{wc_color};font-family:\'DM Mono\',monospace;font-size:0.8rem;">📝 {word_count} words</span>', unsafe_allow_html=True)

            b1, b2 = st.columns([2, 1])
            with b1:
                submit = st.button(
                    "🔍 Analyze My Answer",
                    use_container_width=True,
                    disabled=(word_count < 20 or not has_token),
                )
            with b2:
                if st.button("⟳ New Question", use_container_width=True):
                    pick_question()
                    st.rerun()

            if submit and word_count >= 20:
                client = get_client()
                with st.spinner("Analyzing your answer…"):
                    try:
                        fb = get_feedback(
                            client,
                            st.session_state.current_question,
                            answer,
                            st.session_state.q_type,
                            st.session_state.difficulty,
                            jd_text=st.session_state.jd_text,
                            resume_text=st.session_state.resume_text,
                        )
                        st.session_state.feedback = fb
                        st.session_state.session_scores.append(fb["overall_score"])
                        st.session_state.history.insert(0, {
                            "question": st.session_state.current_question,
                            "answer":   answer,
                            "feedback": fb,
                            "type":     st.session_state.q_type,
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")
        else:
            st.markdown("""
            <div class="iq-card" style="text-align:center;padding:3rem 2rem;">
                <div style="font-size:3rem;margin-bottom:1rem;">🎯</div>
                <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:600;">Ready to practice?</div>
                <div style="color:#6b7280;margin-top:0.5rem;font-size:0.9rem;">
                    Set up your session in the <b>Setup tab</b>, then hit "Get a Question".
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Feedback panel ────────────────────────────────────────────────────────
    with col_right:
        if st.session_state.feedback:
            fb    = st.session_state.feedback
            score = fb["overall_score"]
            sc    = score_color(score)

            st.markdown(f"""
            <div class="iq-card" style="text-align:center;padding:1.5rem;">
                <div class="score-label">Overall Score</div>
                <div class="score-badge" style="color:{sc};">{score}</div>
                <div style="font-size:0.7rem;color:#6b7280;">/100</div>
                <div style="margin-top:0.5rem;">
                    <span class="tag" style="color:{sc};">{fb['verdict']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="iq-card">', unsafe_allow_html=True)
            st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.75rem;">Dimensions</div>', unsafe_allow_html=True)
            for dim, val in fb["dimension_scores"].items():
                c = score_color(val)
                st.markdown(f"""
                <div style="margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;">
                        <span style="font-size:0.82rem;text-transform:capitalize;">{dim}</span>
                        <span style="font-family:'DM Mono',monospace;font-size:0.8rem;color:{c};">{val}</span>
                    </div>
                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:{val}%;background:{c};"></div></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if fb.get("strengths"):
                st.markdown('<div class="iq-card accent">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.5rem;">✅ Strengths</div>', unsafe_allow_html=True)
                for s in fb["strengths"]:
                    st.markdown(f'<div style="font-size:0.85rem;margin-bottom:0.4rem;color:#b0b8c8;">• {s}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if fb.get("improvements"):
                st.markdown('<div class="iq-card warn">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.5rem;">⚡ Improve</div>', unsafe_allow_html=True)
                for s in fb["improvements"]:
                    st.markdown(f'<div style="font-size:0.85rem;margin-bottom:0.4rem;color:#b0b8c8;">• {s}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            kw_used = fb.get("keywords_used", [])
            kw_miss = fb.get("keywords_missing", [])
            if kw_used or kw_miss:
                st.markdown('<div class="iq-card info">', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'Syne\',sans-serif;font-weight:700;margin-bottom:0.5rem;">🔑 Keywords</div>', unsafe_allow_html=True)
                if kw_used:
                    st.markdown(" ".join(f'<span class="tag">{k}</span>' for k in kw_used[:6]), unsafe_allow_html=True)
                if kw_miss:
                    st.markdown('<div style="font-size:0.75rem;color:#6b7280;margin:0.4rem 0 0.2rem;">Missing:</div>', unsafe_allow_html=True)
                    st.markdown(" ".join(f'<span class="tag red">{k}</span>' for k in kw_miss[:6]), unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            if fb.get("ideal_answer_outline"):
                with st.expander("💡 Model Answer Outline"):
                    st.markdown(f'<div style="font-size:0.88rem;color:#b0b8c8;line-height:1.6;">{fb["ideal_answer_outline"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding-top:6rem;text-align:center;color:#3a3d4a;">
                <div style="font-size:4rem;">📋</div>
                <div style="font-family:'Syne',sans-serif;font-size:1rem;margin-top:1rem;">
                    Feedback appears<br>after you submit an answer.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — History
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<h2 style="font-family:\'Syne\',sans-serif;font-weight:800;">Session History</h2>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("""
        <div class="iq-card" style="text-align:center;padding:3rem;">
            <div style="font-size:2.5rem;">📭</div>
            <div style="font-family:'Syne',sans-serif;margin-top:0.75rem;">No history yet.</div>
            <div style="color:#6b7280;font-size:0.88rem;">Answer questions in the Practice tab to see your progress here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        avg   = sum(st.session_state.session_scores) / len(st.session_state.session_scores)
        best  = max(st.session_state.session_scores)
        worst = min(st.session_state.session_scores)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Questions", len(st.session_state.history))
        c2.metric("Avg Score", f"{avg:.0f}")
        c3.metric("Best", best)
        c4.metric("Lowest", worst)
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.history):
            fb    = item["feedback"]
            score = fb["overall_score"]
            sc    = score_color(score)
            with st.expander(f"{score_emoji(score)} Q{len(st.session_state.history)-i}: {item['question'][:70]}… — {score}/100"):
                ca, cb = st.columns([2, 1])
                with ca:
                    st.markdown(f"**Question:** {item['question']}")
                    st.markdown("**Your Answer:**")
                    st.markdown(f'<div style="background:var(--card);border-radius:8px;padding:1rem;font-size:0.88rem;color:#b0b8c8;border:1px solid var(--border);">{item["answer"]}</div>', unsafe_allow_html=True)
                with cb:
                    st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:2rem;color:{sc};text-align:center;">{score}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="text-align:center;color:#6b7280;font-size:0.8rem;">{fb["verdict"]}</div>', unsafe_allow_html=True)
                    if fb.get("strengths"):
                        st.markdown("**Strengths:**")
                        for s in fb["strengths"]:
                            st.markdown(f"- {s}")
