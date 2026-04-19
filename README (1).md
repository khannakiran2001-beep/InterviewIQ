# 🎯 InterviewIQ – AI Interview Coach

> A Streamlit app that gives real-time AI-powered feedback on your interview answers.

## Features
- 🎤 **Practice** Behavioral & Technical questions across 5 role tracks
- 🔍 **AI Feedback** — scored across Clarity, Depth, Relevance, Structure (0–100)
- 🔑 **Keyword Analysis** — see which terms you used and which you missed
- 📊 **Session History** — track your progress across all answered questions
- 🌗 **Dark UI** — clean, professional dark theme

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a free Hugging Face token
Sign up at https://huggingface.co → Settings → Access Tokens → New token (read)

### 3. Add it to Streamlit secrets
Create `.streamlit/secrets.toml`:
```toml
HF_TOKEN = "hf_your_token_here"
```

### 3. Run
```bash
streamlit run app.py
```

## Role Tracks
- Software Engineering
- Data Science
- Product Management
- Cybersecurity
- General / Any Role

## Judging Alignment
| Criterion | How this app covers it |
|-----------|------------------------|
| Innovation (25%) | LLM-powered multi-dimensional scoring + keyword gap analysis |
| Functionality (25%) | Full working Streamlit app with question bank, feedback engine, history |
| Presentation (25%) | Dark theme UI with custom CSS, progress bars, score badges |
| Problem Solving (25%) | Addresses real student/job-seeker pain point with structured output |
