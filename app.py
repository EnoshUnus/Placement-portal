import streamlit as st
import pandas as pd
import joblib
import os
import hashlib
from dotenv import load_dotenv
import ollama
from PyPDF2 import PdfReader

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Placement Portal – Sona College",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg-base:       #0d0f14;
    --bg-surface:    #13161e;
    --bg-card:       #1a1e2a;
    --bg-card-hover: #1e2333;
    --border:        rgba(255,255,255,0.07);
    --border-bright: rgba(255,255,255,0.13);
    --accent-1:      #4f8ef7;
    --accent-2:      #a78bfa;
    --accent-green:  #34d399;
    --accent-amber:  #fbbf24;
    --text-1:        #f0f2f8;
    --text-2:        #8892a4;
    --text-3:        #50596a;
    --radius-sm:     8px;
    --radius-md:     14px;
    --radius-lg:     20px;
    --glow-blue:     0 0 28px rgba(79,142,247,0.18);
    --glow-purple:   0 0 28px rgba(167,139,250,0.15);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg-base) !important;
    color: var(--text-1) !important;
}

/* ── Sidebar ─────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text-1) !important; }

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(79,142,247,0.10) !important;
    border: 1px solid rgba(79,142,247,0.25) !important;
    color: var(--accent-1) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.3px !important;
    width: 100%;
    transition: all 0.18s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(79,142,247,0.20) !important;
    border-color: rgba(79,142,247,0.5) !important;
}

/* ── Main area ───────────────────────────── */
.main { background: var(--bg-base) !important; }
.main .block-container {
    padding: 2rem 2.5rem 4rem;
    max-width: 1280px;
    background: var(--bg-base) !important;
}

/* ── Hero ────────────────────────────────── */
.hero {
    background: var(--bg-card);
    border: 1px solid var(--border-bright);
    border-radius: var(--radius-lg);
    padding: 44px 52px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(79,142,247,0.18) 0%, transparent 65%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute; bottom: -60px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 65%);
    border-radius: 50%;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(79,142,247,0.12);
    border: 1px solid rgba(79,142,247,0.3);
    color: var(--accent-1);
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 1.5px; text-transform: uppercase;
    padding: 5px 14px; border-radius: 30px; margin-bottom: 18px;
    font-family: 'IBM Plex Mono', monospace;
}
.hero-title {
    font-family: 'Sora', sans-serif;
    font-size: 2.4rem; font-weight: 800;
    color: var(--text-1);
    letter-spacing: -1px; line-height: 1.15;
}
.hero-title span {
    background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 0.95rem; color: var(--text-2);
    margin-top: 10px; font-weight: 400; line-height: 1.6;
}
.hero-dots {
    position: absolute; top: 20px; right: 52px;
    display: flex; gap: 6px;
}
.hero-dot { width: 8px; height: 8px; border-radius: 50%; }

/* ── Section titles ──────────────────────── */
.section-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.72rem; font-weight: 700;
    color: var(--text-3);
    letter-spacing: 2px; text-transform: uppercase;
    margin: 32px 0 14px;
    display: flex; align-items: center; gap: 10px;
}
.section-title::before {
    content: '';
    width: 3px; height: 14px;
    background: linear-gradient(180deg, var(--accent-1), var(--accent-2));
    border-radius: 2px; flex-shrink: 0;
}
.section-title::after {
    content: ''; flex: 1; height: 1px;
    background: var(--border); border-radius: 1px;
}

/* ── Info cards ──────────────────────────── */
.info-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    margin-bottom: 16px;
    color: var(--text-1) !important;
    transition: border-color 0.2s;
}
.info-card * { color: var(--text-1) !important; }
.info-card:hover { border-color: var(--border-bright); }
.info-card b { font-weight: 700; color: var(--text-1) !important; }

/* ── Metric row ──────────────────────────── */
.metric-row { display: flex; gap: 14px; margin: 20px 0; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 155px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 22px 24px;
    position: relative; overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
}
.metric-card:hover { border-color: var(--border-bright); transform: translateY(-2px); }
.metric-card::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
    opacity: 0.7;
}
.metric-label {
    font-size: 0.68rem; font-weight: 700;
    color: var(--text-3);
    text-transform: uppercase; letter-spacing: 1.5px;
    font-family: 'IBM Plex Mono', monospace;
}
.metric-value {
    font-size: 2.1rem; font-weight: 800;
    color: var(--text-1); margin-top: 6px;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: -1px;
}
.metric-value.green { color: var(--accent-green); }
.metric-value.blue  { color: var(--accent-1); }

/* ── Student pills ───────────────────────── */
.student-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.25);
    color: var(--accent-green);
    border-radius: 30px;
    padding: 5px 14px; font-weight: 600; font-size: 0.82rem; margin: 3px;
    font-family: 'DM Sans', sans-serif;
}

/* ── Pill tags ───────────────────────────── */
.pill {
    display: inline-flex; align-items: center;
    background: rgba(79,142,247,0.08);
    border: 1px solid rgba(79,142,247,0.2);
    color: var(--accent-1);
    border-radius: 20px;
    padding: 3px 12px; font-size: 0.75rem; font-weight: 600; margin: 2px;
    font-family: 'DM Sans', sans-serif;
}

/* ── Buttons ─────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #4f8ef7) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.2px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 12px rgba(79,142,247,0.25) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(79,142,247,0.38) !important;
}

/* ── Progress bar ────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent-1), var(--accent-2)) !important;
    border-radius: 10px !important;
}

/* ── Inputs & selects ────────────────────── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
.stSelectbox [data-baseweb="select"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-1) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.12) !important;
}

/* ── Dataframe ───────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}

/* ── Tabs ────────────────────────────────── */
[data-testid="stTabs"] [role="tablist"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 4px !important; padding: 6px 8px 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
    color: var(--text-2) !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    transition: all 0.15s !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent-1) !important;
    background: rgba(79,142,247,0.08) !important;
    border-color: rgba(79,142,247,0.3) !important;
}

/* ── File uploader ───────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1px dashed var(--border-bright) !important;
    border-radius: var(--radius-md) !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"] * { color: var(--text-2) !important; }

/* ── Chat messages ───────────────────────── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 4px 0 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    color: #fff !important;
    border-radius: 16px 16px 4px 16px !important;
    padding: 12px 16px !important;
    max-width: 72% !important;
    margin-left: auto !important;
    box-shadow: 0 2px 16px rgba(37,99,235,0.22) !important;
    font-size: 0.88rem !important; line-height: 1.6 !important;
    border: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown p {
    color: #fff !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: var(--bg-card) !important;
    color: var(--text-1) !important;
    border-radius: 16px 16px 16px 4px !important;
    padding: 12px 16px !important;
    max-width: 78% !important;
    border: 1px solid var(--border-bright) !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.25) !important;
    font-size: 0.88rem !important; line-height: 1.65 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown p {
    color: var(--text-1) !important;
}
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, var(--accent-1), #1e40af) !important;
    border-radius: 50% !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, var(--accent-2), #4f46e5) !important;
    border-radius: 50% !important;
}

/* ── Chat input ──────────────────────────── */
[data-testid="stChatInput"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.3) !important;
    transition: border-color 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent-1) !important;
    box-shadow: 0 0 0 3px rgba(79,142,247,0.12), 0 2px 16px rgba(0,0,0,0.3) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    color: var(--text-1) !important;
    background: transparent !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #1e40af, var(--accent-1)) !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    color: white !important;
}

/* ── Chat wrapper ────────────────────────── */
.chat-container-box {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: 0 4px 32px rgba(0,0,0,0.35);
    margin-bottom: 10px;
}
.chat-topbar {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    padding: 16px 22px;
    display: flex; align-items: center; gap: 14px;
}
.chat-topbar-avatar {
    width: 38px; height: 38px; border-radius: 50%;
    background: linear-gradient(135deg, var(--accent-2), #4f46e5);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
    box-shadow: var(--glow-purple);
}
.chat-topbar-name {
    color: var(--text-1); font-weight: 700;
    font-size: 0.92rem; line-height: 1.2;
    font-family: 'Sora', sans-serif;
}
.chat-topbar-sub {
    color: var(--text-3); font-size: 0.7rem;
    margin-top: 2px; font-family: 'IBM Plex Mono', monospace;
}
.chat-topbar-status {
    margin-left: auto; display: flex; align-items: center; gap: 6px;
}
.chat-topbar-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent-green);
    box-shadow: 0 0 8px var(--accent-green);
}
.chat-topbar-status-txt {
    color: var(--accent-green); font-size: 0.68rem;
    font-weight: 600; font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.5px;
}
.chat-empty {
    text-align: center; padding: 48px 24px;
    color: var(--text-3);
}
.chat-empty-icon { font-size: 2.6rem; margin-bottom: 12px; opacity: 0.7; }
.chat-empty-title {
    font-weight: 700; font-size: 0.95rem;
    color: var(--text-2);
    font-family: 'Sora', sans-serif;
}
.chat-empty-sub { font-size: 0.8rem; margin-top: 6px; color: var(--text-3); line-height: 1.6; }

/* ── Sidebar branding ────────────────────── */
.sidebar-logo {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 20px 16px; margin-bottom: 18px; text-align: center;
}
.sidebar-logo-title {
    font-family: 'Sora', sans-serif;
    font-size: 0.95rem; font-weight: 800;
    color: var(--text-1); letter-spacing: -0.3px;
}
.sidebar-logo-sub {
    font-size: 0.68rem; color: var(--text-3);
    margin-top: 4px; font-family: 'IBM Plex Mono', monospace;
}
.role-badge {
    background: rgba(79,142,247,0.10);
    border: 1px solid rgba(79,142,247,0.22);
    border-radius: var(--radius-sm);
    padding: 7px 12px;
    font-size: 0.75rem; font-weight: 700;
    text-align: center; margin-bottom: 14px;
    color: var(--accent-1);
    font-family: 'Sora', sans-serif;
    letter-spacing: 0.3px;
}
.sidebar-email {
    font-size: 0.72rem; color: var(--text-3);
    margin-bottom: 20px; text-align: center;
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Footer ──────────────────────────────── */
.footer {
    background: var(--bg-card);
    border: 1px solid var(--border);
    color: var(--text-3);
    padding: 28px 36px;
    border-radius: var(--radius-lg);
    text-align: center;
    margin-top: 52px;
}
.footer h4 {
    color: var(--text-1);
    font-size: 1rem; font-weight: 800;
    font-family: 'Sora', sans-serif;
    margin-bottom: 6px; letter-spacing: -0.3px;
}
.footer p { font-size: 0.78rem; margin: 3px 0; }

/* ── Divider ─────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Alert & info boxes ──────────────────── */
[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-1) !important;
}

/* ── Scrollbar ───────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

/* ── Bar chart ───────────────────────────── */
[data-testid="stVegaLiteChart"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 8px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-dots">
        <div class="hero-dot" style="background:#ef4444;"></div>
        <div class="hero-dot" style="background:#fbbf24;"></div>
        <div class="hero-dot" style="background:#34d399;"></div>
    </div>
    <div class="hero-badge">🎓 Sona College of Technology</div>
    <div class="hero-title">AI Powered Smart<br><span>Placement Management</span></div>
    <div class="hero-sub">Intelligent eligibility analysis &nbsp;·&nbsp; ML placement prediction &nbsp;·&nbsp; AI career guidance</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENV & MODEL
# ─────────────────────────────────────────────
load_dotenv()
model = joblib.load("placement_model.pkl") if os.path.exists("placement_model.pkl") else None

COMPANY_FILE  = "newcompany.csv"
STUDENTS_FILE = "students.csv"
USERS_FILE    = "users.csv"

# ─────────────────────────────────────────────
# HELPER: Call Ollama (Llama3)
# ─────────────────────────────────────────────
def ask_llama(system_prompt: str, user_message: str) -> str:
    response = ollama.chat(
        model='llama3',
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ]
    )
    return response['message']['content']

def ask_llama_chat(system_prompt: str, messages: list) -> str:
    chat_messages = [{"role": "system", "content": system_prompt}]
    chat_messages.extend(messages)
    response = ollama.chat(
        model='llama3',
        messages=chat_messages
    )
    return response['message']['content']

# ─────────────────────────────────────────────
# CSV NORMALISER
# ─────────────────────────────────────────────
def normalise_companies(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.str.strip()
    if "Company" in df.columns:
        for col, default in [
            ("Job Roles",       "N/A"),
            ("Job Location",    "N/A"),
            ("CTC (LPA)",       "N/A"),
            ("Eligibility CGPA","0"),
            ("Departments",     "All Branches"),
            ("Number of Rounds","N/A"),
        ]:
            if col not in df.columns:
                df[col] = default
        return df
    if "Company_Name" in df.columns:
        df = df.rename(columns={
            "Company_Name":        "Company",
            "Minimum_CGPA":        "Eligibility CGPA",
            "Required_Department": "Departments",
        })
        roles_parts = []
        if "Job_Role" in df.columns:
            roles_parts.append(df["Job_Role"].fillna(""))
        if "Required_Skill" in df.columns:
            roles_parts.append(df["Required_Skill"].fillna(""))
        if roles_parts:
            df["Job Roles"] = roles_parts[0] if len(roles_parts) == 1 else (
                roles_parts[0] + " | " + roles_parts[1]
            )
        if "Domain" in df.columns and "Job Location" not in df.columns:
            df["Job Location"] = df["Domain"]
        for col, default in [
            ("Job Location",    "N/A"),
            ("CTC (LPA)",       "N/A"),
            ("Number of Rounds","N/A"),
        ]:
            if col not in df.columns:
                df[col] = default
    return df

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    return df

def load_companies(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return normalise_companies(df)

def safe_str(val) -> str:
    if pd.isna(val):
        return ""
    return str(val).strip().lower()

def is_eligible(student_dept, student_cgpa, company) -> bool:
    dept_field = safe_str(company["Departments"])
    dept_ok    = "all branches" in dept_field
    if not dept_ok:
        for d in str(company["Departments"]).split(","):
            if d.strip().lower() == safe_str(student_dept):
                dept_ok = True
                break
    try:
        min_cgpa = float(str(company["Eligibility CGPA"]).strip())
    except Exception:
        min_cgpa = 0.0
    return dept_ok and float(student_cgpa) >= min_cgpa

def match_score(student_dept, student_cgpa, student_skills, company) -> int:
    score      = 0
    dept_field = safe_str(company["Departments"])
    if "all branches" in dept_field:
        score += 40
    else:
        for d in str(company["Departments"]).split(","):
            if d.strip().lower() == safe_str(student_dept):
                score += 40
                break
    try:
        min_cgpa = float(str(company["Eligibility CGPA"]).strip())
    except Exception:
        min_cgpa = 0.0
    if float(student_cgpa) >= min_cgpa:
        score += 40
    for skill in str(student_skills).split(","):
        if skill.strip().lower() in safe_str(company["Job Roles"]):
            score += 20
            break
    return score

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
def hash_pw(p): return hashlib.sha256(p.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        pd.DataFrame(columns=["email","password","role"]).to_csv(USERS_FILE, index=False)
    return pd.read_csv(USERS_FILE)

def register_user(email, password, role):
    users = load_users()
    if not email.endswith("@gmail.com"):
        return "Use a Gmail address (@gmail.com)."
    if email in users["email"].values:
        return "User already exists."
    new_row = pd.DataFrame([{"email": email, "password": hash_pw(password), "role": role}])
    pd.concat([users, new_row], ignore_index=True).to_csv(USERS_FILE, index=False)
    return "Success"

def authenticate(email, password):
    users = load_users()
    row   = users[users["email"] == email]
    if row.empty: return None
    return row.iloc[0]["role"] if row.iloc[0]["password"] == hash_pw(password) else None

# ─────────────────────────────────────────────
# SESSION
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role      = None
    st.session_state.email     = ""

def logout():
    st.session_state.logged_in = False
    st.session_state.role      = None
    st.session_state.email     = ""
    st.rerun()

# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def login_page():
    _, col_m, _ = st.columns([1, 1.4, 1])
    with col_m:
        tab1, tab2 = st.tabs(["🔐  Login", "📝  Register"])
        with tab1:
            email    = st.text_input("Gmail Address", placeholder="you@gmail.com", key="li_email")
            password = st.text_input("Password", type="password", key="li_pass")
            if st.button("Login →", use_container_width=True, key="login_btn"):
                role = authenticate(email, password)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.role      = role
                    st.session_state.email     = email
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        with tab2:
            email    = st.text_input("Gmail Address", placeholder="you@gmail.com", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            role     = st.selectbox("I am a...", ["student", "admin"])
            if st.button("Create Account →", use_container_width=True, key="reg_btn"):
                res = register_user(email, password, role)
                st.success("Account created! Please login.") if res == "Success" else st.error(res)

if not st.session_state.logged_in:
    login_page()
    st.markdown("""
    <div class="footer">
        <h4>🎓 Sona College of Technology</h4>
        <p>Autonomous &nbsp;·&nbsp; NAAC A++ &nbsp;·&nbsp; AICTE Approved</p>
        <p style="margin-top:8px;font-size:0.72rem;">© 2026 Department of Training &amp; Placement</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="sidebar-logo-title">🎓 Placement Portal</div>
        <div class="sidebar-logo-sub">SONA COLLEGE OF TECHNOLOGY</div>
    </div>
    <div class="role-badge">
        {'👨‍💼 Admin Panel' if st.session_state.role == 'admin' else '🎓 Student Panel'}
    </div>
    <div class="sidebar-email">{st.session_state.email}</div>
    """, unsafe_allow_html=True)
    if st.button("🚪  Logout", use_container_width=True):
        logout()

# ═══════════════════════════════════════════════════════
# ADMIN PANEL
# ═══════════════════════════════════════════════════════
if st.session_state.role == "admin":

    st.markdown('<div class="section-title">📂 Import Data</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        stu_up = st.file_uploader("Upload **students.csv**", type=["csv"], key="stu_up")
        if stu_up:
            df = pd.read_csv(stu_up)
            df.columns = df.columns.str.strip()
            df.to_csv(STUDENTS_FILE, index=False)
            st.success(f"✅ {len(df)} students imported.")

    with c2:
        com_up = st.file_uploader("Upload **newcompany.csv** (any format)", type=["csv"], key="com_up")
        if com_up:
            df = pd.read_csv(com_up)
            df = normalise_companies(df)
            df.to_csv(COMPANY_FILE, index=False)
            st.success(f"✅ {len(df)} companies imported.")
            st.info(f"Columns saved: {list(df.columns)}")

    # ── Company Directory ──────────────────────────────
    if os.path.exists(COMPANY_FILE):
        companies = load_companies(COMPANY_FILE)

        if "Company" not in companies.columns:
            st.error(f"Could not normalise company file. Columns found: {list(companies.columns)}")
            st.stop()

        st.markdown('<div class="section-title">🏢 Company Directory</div>', unsafe_allow_html=True)
        st.dataframe(companies, use_container_width=True, height=260)

        # ── Eligibility Analysis ───────────────────────
        if os.path.exists(STUDENTS_FILE):
            students = load_csv(STUDENTS_FILE)

            st.markdown('<div class="section-title">📊 Eligibility Analysis</div>', unsafe_allow_html=True)
            selected = st.selectbox("Select a company", companies["Company"].dropna().unique())

            if selected:
                comp = companies[companies["Company"] == selected].iloc[0]

                st.markdown(f"""
                <div class="info-card">
                    <div style="font-size:1.05rem;font-weight:800;color:var(--text-1);margin-bottom:14px;font-family:'Sora',sans-serif;">
                        🏢 {comp['Company']}
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;">
                        <span class="pill">📍 {comp.get('Job Location','N/A')}</span>
                        <span class="pill">💰 {comp.get('CTC (LPA)','N/A')} LPA</span>
                        <span class="pill">🎓 Min CGPA: {comp['Eligibility CGPA']}</span>
                        <span class="pill">🔄 {comp.get('Number of Rounds','N/A')} Rounds</span>
                    </div>
                    <div style="font-size:0.82rem;color:var(--text-2);line-height:1.7;">
                        <b>Departments:</b> {comp['Departments']}<br>
                        <b>Roles:</b> {comp['Job Roles']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                eligible_names = [
                    s["Name"] for _, s in students.iterrows()
                    if is_eligible(s.get("Department",""), s.get("CGPA", 0), comp)
                ]

                total = len(students)
                ec    = len(eligible_names)
                pct   = round((ec / total * 100), 2) if total > 0 else 0.0

                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-card">
                        <div class="metric-label">Total Students</div>
                        <div class="metric-value">{total}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Eligible Students</div>
                        <div class="metric-value green">{ec}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Eligibility %</div>
                        <div class="metric-value blue">{pct}%</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.bar_chart(
                    pd.DataFrame({"Category":["Eligible","Not Eligible"],"Count":[ec,total-ec]})
                    .set_index("Category"), color="#4f8ef7", height=260
                )

                # ── Eligible Students (Clickable) ──────────────
                st.markdown('<div class="section-title">✅ Eligible Students</div>', unsafe_allow_html=True)
                if eligible_names:
                    # Initialise selected_student in session state if not present
                    if "selected_student" not in st.session_state:
                        st.session_state["selected_student"] = None

                    # Render one button per eligible student in a responsive grid
                    cols = st.columns(6)
                    for i, stu_name in enumerate(eligible_names):
                        with cols[i % 6]:
                            # Highlight the active selection with a different label
                            is_active = st.session_state["selected_student"] == stu_name
                            btn_label = f"✅ {stu_name}" if is_active else f"👤 {stu_name}"
                            if st.button(btn_label, key=f"pill_{selected}_{stu_name}"):
                                # Toggle: click same name again to close panel
                                if is_active:
                                    st.session_state["selected_student"] = None
                                else:
                                    st.session_state["selected_student"] = stu_name
                                st.rerun()

                    # ── Student Detail Panel ───────────────────
                    sel_name = st.session_state.get("selected_student")
                    if sel_name and sel_name in eligible_names:
                        sel_row = students[students["Name"] == sel_name]
                        if not sel_row.empty:
                            sv = sel_row.iloc[0]

                            # Build skill pills
                            skill_pills_detail = "".join(
                                f'<span class="pill">🛠️ {sk.strip()}</span>'
                                for sk in str(sv.get("Skills", "N/A")).split(",")
                                if sk.strip()
                            )

                            # Try multiple possible column names for certification
                            cert_val = "N/A"
                            for cert_col in ["Certification", "Certifications",
                                             "certification", "certifications"]:
                                if cert_col in sv.index and str(sv[cert_col]).strip() not in ("", "nan"):
                                    cert_val = sv[cert_col]
                                    break

                            st.markdown(f"""
                            <div class="info-card" style="border-left:3px solid var(--accent-1);
                                                          margin-top:16px;">
                                <div style="font-size:1.05rem;font-weight:800;color:var(--text-1);
                                            margin-bottom:14px;font-family:'Sora',sans-serif;">
                                    👤 {sv['Name']} — Student Details
                                </div>
                                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;
                                            font-size:0.85rem;color:var(--text-2);margin-bottom:12px;">
                                    <div>
                                        <b style="color:var(--text-1);">Student ID:</b>
                                        &nbsp;{sv.get('Student_ID', 'N/A')}
                                    </div>
                                    <div>
                                        <b style="color:var(--text-1);">Department:</b>
                                        &nbsp;{sv.get('Department', 'N/A')}
                                    </div>
                                    <div>
                                        <b style="color:var(--text-1);">CGPA:</b>
                                        &nbsp;{sv.get('CGPA', 'N/A')}
                                    </div>
                                    <div>
                                        <b style="color:var(--text-1);">Certification:</b>
                                        &nbsp;{cert_val}
                                    </div>
                                </div>
                                <div style="margin-top:8px;">
                                    <b style="color:var(--text-1);font-size:0.85rem;">Skills:</b>
                                    &nbsp;
                                    <span style="display:inline-flex;flex-wrap:wrap;gap:4px;">
                                        {skill_pills_detail}
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.warning("No eligible students for this company.")

    else:
        st.info("📤 Upload newcompany.csv to begin.")

    # ── Ask Balaji Admin ───────────────────────────────
    st.markdown('<div class="section-title">🤖 Ask Balaji – Admin Mode</div>', unsafe_allow_html=True)

    if "admin_chat_history" not in st.session_state:
        st.session_state.admin_chat_history = []

    st.markdown("""
    <div class="chat-container-box">
        <div class="chat-topbar">
            <div class="chat-topbar-avatar">🤖</div>
            <div>
                <div class="chat-topbar-name">Balaji AI</div>
                <div class="chat-topbar-sub">PLACEMENT ASSISTANT · ADMIN MODE</div>
            </div>
            <div class="chat-topbar-status">
                <div class="chat-topbar-dot"></div>
                <div class="chat-topbar-status-txt">ONLINE</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.admin_chat_history:
        st.markdown("""
        <div class="chat-empty">
            <div class="chat-empty-icon">💬</div>
            <div class="chat-empty-title">No messages yet</div>
            <div class="chat-empty-sub">Ask about student eligibility, company requirements,<br>placement statistics and more…</div>
        </div>""", unsafe_allow_html=True)

    for msg in st.session_state.admin_chat_history:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

    col_clr, _ = st.columns([1, 5])
    with col_clr:
        if st.button("🗑️ Clear Chat", key="clear_admin"):
            st.session_state.admin_chat_history = []
            st.rerun()

    if admin_q := st.chat_input("Ask Balaji anything about students or companies…", key="admin_chat_input"):
        if not os.path.exists(STUDENTS_FILE) or not os.path.exists(COMPANY_FILE):
            st.error("Upload both CSV files first.")
        else:
            s_df = load_csv(STUDENTS_FILE)
            c_df = load_companies(COMPANY_FILE)
            system = (
                "You are Balaji, an AI placement assistant for Sona College of Technology (Admin Mode). "
                "You are NOT Claude, NOT ChatGPT, NOT any other AI. You are Balaji, a custom AI built "
                "for Sona College of Technology's placement portal. If asked who you are or what model "
                "powers you, always say you are Balaji. "
                "You have access to student and company data. Answer ONLY using the data provided. "
                "Be concise and precise. Format answers clearly.\n\n"
                f"STUDENTS DATA:\n{s_df.to_string(index=False)}\n\n"
                f"COMPANIES DATA:\n{c_df.to_string(index=False)}"
            )
            st.session_state.admin_chat_history.append({"role": "user", "content": admin_q})
            with st.chat_message("user", avatar="👤"):
                st.markdown(admin_q)
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner(""):
                    try:
                        reply = ask_llama_chat(system, st.session_state.admin_chat_history)
                        st.markdown(reply)
                        st.session_state.admin_chat_history.append({"role": "assistant", "content": reply})
                    except Exception as e:
                        st.session_state.admin_chat_history.pop()
                        st.error(f"❌ Ollama error: {str(e)}")

# ═══════════════════════════════════════════════════════
# STUDENT PANEL
# ═══════════════════════════════════════════════════════
elif st.session_state.role == "student":

    st.markdown('<div class="section-title">🎓 Student Dashboard</div>', unsafe_allow_html=True)
    reg_no = st.text_input("Enter your Student ID", placeholder="e.g. S001", key="reg_no")

    if reg_no:
        if not os.path.exists(STUDENTS_FILE):
            st.warning("Student data not loaded yet. Contact admin.")
            st.stop()

        students = load_csv(STUDENTS_FILE)

        if "Student_ID" not in students.columns:
            st.error(f"'Student_ID' column missing. Found: {list(students.columns)}")
            st.stop()

        row = students[students["Student_ID"].astype(str).str.upper() == reg_no.strip().upper()]

        if row.empty:
            st.error("Invalid Student ID.")
        else:
            s          = row.iloc[0]
            name       = s["Name"]
            department = s["Department"]
            cgpa       = float(s["CGPA"])
            skills     = str(s.get("Skills", ""))

            skill_pills = "".join(
                f'<span class="pill">🛠️ {sk.strip()}</span>'
                for sk in skills.split(",") if sk.strip()
            )
            st.markdown(f"""
            <div class="info-card" style="border-left:3px solid var(--accent-1);">
                <div style="font-size:1.3rem;font-weight:800;color:var(--text-1);margin-bottom:14px;font-family:'Sora',sans-serif;">
                    👋 Welcome back, {name}
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    <span class="pill">🏛️ {department}</span>
                    <span class="pill">📊 CGPA: {cgpa}</span>
                    {skill_pills}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # ── Placement Prediction ──────────────────
            st.markdown('<div class="section-title">📊 Placement Prediction</div>', unsafe_allow_html=True)
            if st.button("🔮 Predict My Placement Chance", key="predict_btn"):
                if model is None:
                    st.error("placement_model.pkl not found. Contact admin.")
                else:
                    feats  = pd.DataFrame([{"CGPA":cgpa,"Internship":1,"Projects":2,"Communication":3}])
                    prob   = model.predict_proba(feats)[0][1] * 100
                    prob_r = round(prob, 2)
                    colour  = "#34d399" if prob >= 70 else ("#fbbf24" if prob >= 40 else "#f87171")
                    verdict = ("High Chance ✅" if prob >= 70
                               else "Moderate Chance ⚠️" if prob >= 40
                               else "Needs Improvement 📈")
                    st.markdown(f"""
                    <div class="metric-row">
                        <div class="metric-card" style="border-top-color:{colour};">
                            <div class="metric-label">Placement Probability</div>
                            <div class="metric-value" style="color:{colour};">{prob_r}%</div>
                            <div style="font-size:0.82rem;color:{colour};font-weight:700;margin-top:8px;font-family:'IBM Plex Mono',monospace;">{verdict}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    st.progress(int(prob))

            # ── Company Matches ───────────────────────
            st.markdown('<div class="section-title">🏆 Best Company Matches</div>', unsafe_allow_html=True)
            if not os.path.exists(COMPANY_FILE):
                st.info("Company data not available. Contact admin.")
            else:
                companies = load_companies(COMPANY_FILE)
                if "Company" not in companies.columns:
                    st.error(f"Company column missing after normalisation. Found: {list(companies.columns)}")
                else:
                    scored = []
                    for _, comp in companies.iterrows():
                        sc = match_score(department, cgpa, skills, comp)
                        if sc > 0:
                            scored.append({
                                "Company":   comp["Company"],
                                "Job Roles": comp["Job Roles"],
                                "CTC (LPA)": comp.get("CTC (LPA)","N/A"),
                                "Location":  comp.get("Job Location","N/A"),
                                "Min CGPA":  comp["Eligibility CGPA"],
                                "Rounds":    comp.get("Number of Rounds","N/A"),
                                "Match %":   sc
                            })
                    if scored:
                        scored_df = (pd.DataFrame(scored)
                                       .sort_values("Match %", ascending=False)
                                       .reset_index(drop=True))
                        scored_df.index += 1
                        st.dataframe(scored_df, use_container_width=True, height=280)
                        top = scored[0]
                        st.markdown(f"""
                        <div class="info-card" style="border-left:3px solid var(--accent-green);">
                            <b style="color:var(--accent-green);">🥇 Best Match:</b>&nbsp;
                            <span style="color:var(--text-1);">{top['Company']}</span>
                            &nbsp;·&nbsp; <span style="color:var(--text-2);">{top['CTC (LPA)']} LPA</span>
                            &nbsp;·&nbsp; <span style="color:var(--text-2);">{top['Location']}</span>
                            &nbsp;·&nbsp; <b style="color:var(--accent-green);">{top['Match %']}% match</b>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.warning("No matching companies for your profile.")

            # ── Resume Analyser ───────────────────────
            st.markdown('<div class="section-title">📄 Resume Analyser</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_up")
            if uploaded:
                reader      = PdfReader(uploaded)
                resume_text = "".join(p.extract_text() or "" for p in reader.pages)
                if not resume_text.strip():
                    st.warning("Could not extract text. Use a text-based PDF.")
                else:
                    with st.spinner("🔍 Analysing resume..."):
                        try:
                            system = (
                                "You are Balaji, an expert placement counsellor at Sona College of Technology. "
                                "You are NOT Claude, NOT ChatGPT, NOT any other AI. You are Balaji. "
                                "Analyse resumes for tech company placements using these sections: "
                                "1. **Strengths**  2. **Gaps & Improvements**  "
                                "3. **Skills to Add**  4. **Overall Score /10**"
                            )
                            reply = ask_llama(system, f"Resume:\n{resume_text}")
                            st.markdown("**🤖 Balaji's Resume Review:**")
                            st.markdown(reply)
                        except Exception as e:
                            st.error(f"❌ Ollama error: {str(e)}")

            # ── Ask Balaji Student ────────────────────
            st.markdown('<div class="section-title">🤖 Ask Balaji</div>', unsafe_allow_html=True)

            if "student_chat_history" not in st.session_state:
                st.session_state.student_chat_history = []

            st.markdown("""
            <div class="chat-container-box">
                <div class="chat-topbar">
                    <div class="chat-topbar-avatar">🎯</div>
                    <div>
                        <div class="chat-topbar-name">Balaji AI</div>
                        <div class="chat-topbar-sub">YOUR PERSONAL PLACEMENT GUIDE</div>
                    </div>
                    <div class="chat-topbar-status">
                        <div class="chat-topbar-dot"></div>
                        <div class="chat-topbar-status-txt">ONLINE</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

            if not st.session_state.student_chat_history:
                st.markdown("""
                <div class="chat-empty">
                    <div class="chat-empty-icon">🎓</div>
                    <div class="chat-empty-title">Hi! I'm Balaji, your placement guide</div>
                    <div class="chat-empty-sub">Ask about interview prep, companies,<br>resume tips, or anything about placements</div>
                </div>""", unsafe_allow_html=True)

            for msg in st.session_state.student_chat_history:
                with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
                    st.markdown(msg["content"])

            col_clrs, _ = st.columns([1, 5])
            with col_clrs:
                if st.button("🗑️ Clear Chat", key="clear_stu"):
                    st.session_state.student_chat_history = []
                    st.rerun()

            if stu_q := st.chat_input("Ask Balaji about interviews, companies, career tips…", key="student_chat_input"):
                comp_ctx = (load_companies(COMPANY_FILE).to_string(index=False)
                            if os.path.exists(COMPANY_FILE) else "No company data.")
                system = (
                    "You are Balaji, a friendly AI placement assistant at Sona College of Technology. "
                    "You are NOT Claude, NOT ChatGPT, NOT any other AI. You are Balaji, a custom AI "
                    "built for Sona College of Technology's placement portal. If asked who you are or "
                    "what model powers you, always say you are Balaji. "
                    "Give practical, specific, encouraging advice based on the student's profile.\n\n"
                    f"Student Profile: Name={name} | Dept={department} | CGPA={cgpa} | Skills={skills}\n"
                    f"Available Companies:\n{comp_ctx}"
                )
                st.session_state.student_chat_history.append({"role": "user", "content": stu_q})
                with st.chat_message("user", avatar="👤"):
                    st.markdown(stu_q)
                with st.chat_message("assistant", avatar="🤖"):
                    with st.spinner(""):
                        try:
                            reply = ask_llama_chat(system, st.session_state.student_chat_history)
                            st.markdown(reply)
                            st.session_state.student_chat_history.append({"role": "assistant", "content": reply})
                        except Exception as e:
                            st.session_state.student_chat_history.pop()
                            st.error(f"❌ Ollama error: {str(e)}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <h4>🎓 Sona College of Technology</h4>
    <p>Autonomous &nbsp;·&nbsp; NAAC A++ &nbsp;·&nbsp; AICTE Approved</p>
    <p style="margin-top:10px;font-size:0.7rem;color:var(--text-3);">
        © 2026 Department of Training &amp; Placement &nbsp;·&nbsp; AI Placement Portal v2.0
    </p>
</div>
""", unsafe_allow_html=True)
