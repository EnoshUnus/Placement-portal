import streamlit as st
import pandas as pd
import joblib
import os
import hashlib
from dotenv import load_dotenv
from google import genai
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
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; background: #f4f6fb; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a1628 0%, #0f2347 60%, #0a1628 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
section[data-testid="stSidebar"] * { color: #e8edf5 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #ffffff !important;
    border-radius: 10px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 500 !important;
    width: 100%;
    transition: all 0.2s ease;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.14) !important;
}

.main .block-container { padding: 2rem 2.5rem 4rem; max-width: 1300px; }

.hero {
    background: linear-gradient(135deg, #0a1628 0%, #0f2d5c 50%, #1a3a6e 100%);
    border-radius: 18px; padding: 42px 48px;
    margin-bottom: 32px; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(59,130,246,0.25) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title  { font-size: 2.2rem; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1.2; }
.hero-sub    { font-size: 1.05rem; color: rgba(255,255,255,0.65); margin-top: 8px; }
.hero-badge  {
    display: inline-block;
    background: rgba(59,130,246,0.25); border: 1px solid rgba(59,130,246,0.4);
    color: #93c5fd; font-size: 0.75rem; font-weight: 600;
    letter-spacing: 1px; text-transform: uppercase;
    padding: 4px 12px; border-radius: 20px; margin-bottom: 14px;
}

.section-title {
    font-size: 1.3rem; font-weight: 700; color: #0f2347;
    margin: 28px 0 16px; display: flex; align-items: center; gap: 10px;
}
.section-title::after {
    content: ''; flex: 1; height: 2px;
    background: linear-gradient(90deg, #e2e8f0, transparent); border-radius: 1px;
}

.info-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 20px 24px;
    margin-bottom: 16px; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
    color: #1a1a1a !important;
}
.info-card * { color: #1a1a1a !important; }
.info-card b { font-weight: 700; }

.metric-row { display: flex; gap: 16px; margin: 20px 0; flex-wrap: wrap; }
.metric-card {
    flex: 1; min-width: 160px; background: #ffffff;
    border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 20px 22px; box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.metric-label { font-size: 0.78rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.8px; }
.metric-value { font-size: 2rem; font-weight: 800; color: #0f2347; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }
.metric-value.green { color: #059669; }
.metric-value.blue  { color: #2563eb; }

.student-pill {
    display: inline-flex; align-items: center; gap: 8px;
    background: #ecfdf5; border: 1px solid #a7f3d0;
    color: #065f46; border-radius: 30px;
    padding: 6px 16px; font-weight: 600; font-size: 0.9rem; margin: 4px;
}

.stButton > button {
    background: linear-gradient(135deg, #1e3a8a, #2563eb) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; font-size: 0.95rem !important;
    padding: 0.55rem 1.5rem !important; transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.4) !important;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, #2563eb, #7c3aed) !important;
    border-radius: 10px !important;
}

.footer {
    background: linear-gradient(135deg, #0a1628, #0f2347);
    color: rgba(255,255,255,0.7); padding: 28px 36px;
    border-radius: 16px; text-align: center; margin-top: 48px;
}
.footer h4 { color: #ffffff; font-size: 1.1rem; font-weight: 700; margin-bottom: 6px; }
.footer p  { font-size: 0.85rem; margin: 2px 0; }

.sidebar-logo {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 18px 16px; margin-bottom: 20px; text-align: center;
}
.role-badge {
    background: rgba(59,130,246,0.2); border: 1px solid rgba(59,130,246,0.35);
    border-radius: 8px; padding: 6px 12px;
    font-size: 0.8rem; font-weight: 600; text-align: center; margin-bottom: 16px;
}
.pill {
    display: inline-block; background: #eff6ff; border: 1px solid #bfdbfe;
    color: #1e40af; border-radius: 20px;
    padding: 3px 12px; font-size: 0.78rem; font-weight: 600; margin: 2px;
}
.career-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    margin-bottom: 20px;
}
.career-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(37,99,235,0.08);
    border-color: #3b82f6;
}
.badge-high {
    background: #d1fae5 !important;
    color: #065f46 !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 4px 10px !important;
    border-radius: 20px !important;
    border: 1px solid #a7f3d0 !important;
    display: inline-block !important;
}
.badge-good {
    background: #dbeafe !important;
    color: #1e40af !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 4px 10px !important;
    border-radius: 20px !important;
    border: 1px solid #bfdbfe !important;
    display: inline-block !important;
}
.badge-potential {
    background: #fef3c7 !important;
    color: #92400e !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 4px 10px !important;
    border-radius: 20px !important;
    border: 1px solid #fde68a !important;
    display: inline-block !important;
}
.linkedin-btn {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    background: linear-gradient(135deg, #0077b5, #005987) !important;
    color: #ffffff !important;
    text-decoration: none !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 10px 16px !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    width: 100% !important;
    text-align: center !important;
    box-shadow: 0 4px 10px rgba(0, 119, 181, 0.25) !important;
}
.linkedin-btn:hover {
    background: linear-gradient(135deg, #005987, #003e5e) !important;
    box-shadow: 0 6px 14px rgba(0, 119, 181, 0.35) !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-badge">🎓 Sona College of Technology</div>
    <div class="hero-title">AI Powered Smart Placement<br>Management System</div>
    <div class="hero-sub">Intelligent eligibility analysis · ML placement prediction · AI career guidance</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENV & MODEL
# ─────────────────────────────────────────────
load_dotenv(override=True)

# File paths
USERS_FILE = "users.csv"
STUDENTS_FILE = "students.csv"
COMPANY_FILE = "newcompany.csv"

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

model = joblib.load("placement_model.pkl") if os.path.exists("placement_model.pkl") else None

# ─────────────────────────────────────────────
# HELPER: Call Gemini (Streaming)
# ─────────────────────────────────────────────
def ask_gemini_stream(system_prompt: str, user_message: str):
    """Send a message to Gemini 2.5 Flash and yield content stream chunks."""
    if not client:
        yield "❌ Gemini Client is not configured. Please ensure GEMINI_API_KEY is present in your .env file."
        return
    try:
        full_prompt = f"System Instruction: {system_prompt}\n\nUser Query: {user_message}"
        response = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"❌ Error: {str(e)}"

# ─────────────────────────────────────────────
# HELPER: Get Job Suggestions (JSON)
# ─────────────────────────────────────────────
def get_job_suggestions(department, cgpa, skills, extra_skills, extra_knowledge, certifications):
    """Call Gemini to get job suggestions based on candidate profile."""
    import json
    if not client:
        return []
    
    prompt = f"""
    You are an expert career advisor. Based on the student's profile, suggest EXACTLY 3 job roles they should target.
    
    Profile:
    - Department: {department}
    - CGPA: {cgpa} (academic performance indicator)
    - Primary Skills: {skills}
    - Extra Skills: {extra_skills}
    - Extra Knowledge Areas: {extra_knowledge}
    - Certifications: {certifications}
    
    Provide your output as a VALID JSON array of objects. Do not include markdown code fences (like ```json). Return ONLY the raw JSON string.
    Each object in the array must have the following keys:
    1. "role" - Title of the job role (e.g. "React Developer", "Machine Learning Engineer").
    2. "fit_reason" - Explain in 1-2 sentences why this fits their skills and performance (mention CGPA or department if relevant).
    3. "match_level" - One of "High Match", "Good Match", "Potential Match".
    4. "skills_to_acquire" - A list of 2-3 specific skills they should acquire or focus on next to secure this role.
    5. "linkedin_query" - A short search query string suitable for LinkedIn jobs search (e.g. "software engineer" or "data analyst").
    
    Ensure the JSON is strictly compliant and contains only the array.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        # Clean markdown formatting if model returned any
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()
        
        # Parse JSON
        suggestions = json.loads(text)
        return suggestions
    except Exception as e:
        # Return fallback roles based on department & skills
        fallback = [
            {
                "role": "Software Developer",
                "fit_reason": f"Matches your background in {department} and interest in technology.",
                "match_level": "Good Match",
                "skills_to_acquire": ["System Design", "Cloud Infrastructure"],
                "linkedin_query": "software engineer"
            },
            {
                "role": "Data Analyst",
                "fit_reason": "Analytical role suitable for leveraging problem-solving skills.",
                "match_level": "Good Match",
                "skills_to_acquire": ["SQL", "Power BI"],
                "linkedin_query": "data analyst"
            },
            {
                "role": "Associate Engineer",
                "fit_reason": "General engineering entry-level role aligned with your academic qualification.",
                "match_level": "Potential Match",
                "skills_to_acquire": ["Core CS Concepts", "Data Structures"],
                "linkedin_query": "associate engineer"
            }
        ]
        return fallback

# ─────────────────────────────────────────────
# CSV NORMALISER
# Handles BOTH column formats:
#   Format A (newcompany.csv): Company, Job Roles, Job Location,
#                              CTC (LPA), Eligibility CGPA, Departments, Number of Rounds
#   Format B (old format):     Company_ID, Company_Name, Domain,
#                              Required_Department, Minimum_CGPA,
#                              Required_Skill, Preferred_Certification, Job_Role
# After normalisation all code uses Format A column names.
# ─────────────────────────────────────────────
def normalise_companies(df: pd.DataFrame) -> pd.DataFrame:
    """Rename old-format columns to match the canonical column set."""
    df = df.copy()
    df.columns = df.columns.str.strip()

    # Already in new format?
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

    # Old format — rename
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
    <div class="footer"><h4>Sona College of Technology</h4>
    <p>Autonomous | NAAC A++ | AICTE Approved</p>
    <p>© 2026 Department of Training &amp; Placement</p></div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-logo">
        <div style="font-size:1rem;font-weight:700;">🎓 Placement Portal</div>
        <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);">Sona College of Technology</div>
    </div>
    <div class="role-badge">
        {'👨‍💼 Admin Panel' if st.session_state.role == 'admin' else '🎓 Student Panel'}
    </div>
    <div style="font-size:0.8rem;color:rgba(255,255,255,0.45);margin-bottom:20px;text-align:center;">
        {st.session_state.email}
    </div>
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
                    <div style="font-size:1.1rem;font-weight:700;color:#0f2347;margin-bottom:12px;">
                        🏢 {comp['Company']}
                    </div>
                    <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:10px;">
                        <span class="pill">📍 {comp.get('Job Location','N/A')}</span>
                        <span class="pill">💰 {comp.get('CTC (LPA)','N/A')} LPA</span>
                        <span class="pill">🎓 Min CGPA: {comp['Eligibility CGPA']}</span>
                        <span class="pill">🔄 {comp.get('Number of Rounds','N/A')} Rounds</span>
                    </div>
                    <div style="font-size:0.85rem;color:#475569;">
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
                    .set_index("Category"), color="#2563eb", height=260
                )

                st.markdown('<div class="section-title">✅ Eligible Students</div>', unsafe_allow_html=True)
                if eligible_names:
                    pills = "".join(f'<span class="student-pill">👤 {n}</span>' for n in eligible_names)
                    st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{pills}</div>',
                                unsafe_allow_html=True)
                else:
                    st.warning("No eligible students for this company.")

    else:
        st.info("📤 Upload newcompany.csv to begin.")

    # ── Ask Balaji Admin ───────────────────────────────
    st.markdown('<div class="section-title">🤖 Ask Balaji – Admin Mode</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card" style="background:#f0f9ff;border-color:#bae6fd;">
    <span style="color:#0369a1;font-size:0.88rem;">
    💡 Ask about eligibility, student counts, company requirements — Balaji answers from your CSV data only.
    </span></div>
    """, unsafe_allow_html=True)

    admin_q = st.text_input("Question", placeholder="e.g. Which students qualify for Accenture?", key="admin_q")
    if st.button("Ask Balaji 🤖", key="ask_admin"):
        if not os.path.exists(STUDENTS_FILE) or not os.path.exists(COMPANY_FILE):
            st.error("Upload both CSV files first.")
        elif not admin_q.strip():
            st.warning("Please enter a question.")
        else:
            s_df = load_csv(STUDENTS_FILE)
            c_df = load_companies(COMPANY_FILE)
            system = (
                "You are Balaji, an AI placement assistant for Sona College of Technology. "
                "Answer ONLY using the data provided. Be concise and precise."
            )
            user_msg = (
                f"STUDENTS:\n{s_df.to_string(index=False)}\n\n"
                f"COMPANIES:\n{c_df.to_string(index=False)}\n\n"
                f"Question: {admin_q}"
            )
            try:
                st.markdown("**🤖 Balaji says:**")
                st.write_stream(ask_gemini_stream(system, user_msg))
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

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
            extra_skills    = str(s.get("Extra_Skills", ""))
            extra_knowledge = str(s.get("Extra_Knowledge", ""))
            certifications  = str(s.get("Certifications", ""))

            all_skills = [sk.strip() for sk in skills.split(",") if sk.strip()]
            all_extra_skills = [sk.strip() for sk in extra_skills.split(",") if sk.strip()]
            all_extra_knowledge = [sk.strip() for sk in extra_knowledge.split(",") if sk.strip()]
            all_certs = [c.strip() for c in certifications.split(",") if c.strip()]

            skill_pills = "".join(f'<span class="pill">🛠️ {sk}</span>' for sk in all_skills)
            extra_skill_pills = "".join(f'<span class="pill" style="background:#f0fdf4;border-color:#bbf7d0;color:#166534;">🌟 {sk}</span>' for sk in all_extra_skills)
            knowledge_pills = "".join(f'<span class="pill" style="background:#faf5ff;border-color:#e9d5ff;color:#6b21a8;">🧠 {sk}</span>' for sk in all_extra_knowledge)
            cert_pills = "".join(f'<span class="pill" style="background:#fff7ed;border-color:#ffedd5;color:#9a3412;">🎓 {sk}</span>' for sk in all_certs)

            st.markdown(f"""
            <div class="info-card" style="background:linear-gradient(135deg,#eff6ff,#f0f9ff);border-color:#bfdbfe;">
                <div style="font-size:1.4rem;font-weight:800;color:#1e3a8a;margin-bottom:12px;">
                    👋 Welcome, {name}!
                </div>
                <div style="display:flex;flex-wrap:wrap;gap:8px;">
                    <span class="pill">🏛️ {department}</span>
                    <span class="pill">📊 CGPA: {cgpa}</span>
                    {skill_pills}
                    {extra_skill_pills}
                    {knowledge_pills}
                    {cert_pills}
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
                    colour  = "#059669" if prob >= 70 else ("#d97706" if prob >= 40 else "#dc2626")
                    verdict = ("High Chance ✅" if prob >= 70
                               else "Moderate Chance ⚠️" if prob >= 40
                               else "Needs Improvement 📈")
                    st.markdown(f"""
                    <div class="metric-row">
                        <div class="metric-card" style="border-left:4px solid {colour};">
                            <div class="metric-label">Placement Probability</div>
                            <div class="metric-value" style="color:{colour};">{prob_r}%</div>
                            <div style="font-size:0.85rem;color:{colour};font-weight:600;margin-top:6px;">{verdict}</div>
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
                        <div class="info-card" style="background:#f0fdf4;border-color:#86efac;">
                            <b style="color:#166534;">🥇 Best Match:</b>&nbsp;
                            {top['Company']} &nbsp;·&nbsp; {top['CTC (LPA)']} LPA
                            &nbsp;·&nbsp; {top['Location']}
                            &nbsp;·&nbsp; <b>{top['Match %']}% match</b>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.warning("No matching companies for your profile.")

            # ── Career Guidance & LinkedIn Jobs ──────
            st.markdown('<div class="section-title">🎯 AI Career Guidance & LinkedIn Jobs</div>', unsafe_allow_html=True)
            
            cache_key = f"job_suggestions_{reg_no.strip().upper()}"
            
            if cache_key not in st.session_state:
                st.info("💡 Let Balaji analyze your academic performance and skills to suggest career roles and find live LinkedIn opportunities.")
                if st.button("🔍 Suggest Job Roles & LinkedIn Jobs", key="gen_career_btn"):
                    with st.spinner("Analyzing profile and generating recommendations..."):
                        st.session_state[cache_key] = get_job_suggestions(
                            department, cgpa, skills, extra_skills, extra_knowledge, certifications
                        )
                        st.rerun()
            else:
                suggestions = st.session_state[cache_key]
                
                cols_hdr = st.columns([8, 2])
                with cols_hdr[0]:
                     st.write("Here are the top career paths recommended for you based on your academic performance and skills:")
                with cols_hdr[1]:
                     if st.button("🔄 Refresh Suggestions", key="regen_career_btn"):
                         del st.session_state[cache_key]
                         st.rerun()
                
                cols = st.columns(3)
                for idx, sug in enumerate(suggestions):
                    role = sug.get("role", "N/A")
                    fit_reason = sug.get("fit_reason", "N/A")
                    match_level = sug.get("match_level", "Good Match")
                    skills_to_acquire = sug.get("skills_to_acquire", [])
                    query = sug.get("linkedin_query", role)
                    
                    import urllib.parse
                    encoded_query = urllib.parse.quote(query)
                    linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_query}"
                    
                    badge_class = "badge-good"
                    if "high" in match_level.lower():
                        badge_class = "badge-high"
                    elif "potential" in match_level.lower() or "medium" in match_level.lower():
                        badge_class = "badge-potential"
                    
                    skills_list_html = "".join(f'<span class="pill" style="margin:2px; font-size:0.75rem;">📚 {sk}</span>' for sk in skills_to_acquire)
                    
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="career-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                                <b style="font-size:1.1rem; color:#0f2347; line-height:1.2;">{role}</b>
                            </div>
                            <div style="margin-bottom:12px;">
                                <span class="{badge_class}">{match_level}</span>
                            </div>
                            <p style="font-size:0.85rem; color:#475569; margin-bottom:14px; line-height:1.4; min-height:60px;">
                                {fit_reason}
                            </p>
                            <div style="margin-top:auto; margin-bottom:12px;">
                                <div style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">
                                    Skills to Focus:
                                </div>
                                <div style="display:flex; flex-wrap:wrap; gap:4px;">
                                    {skills_list_html}
                                </div>
                            </div>
                            <a href="{linkedin_url}" target="_blank" class="linkedin-btn">
                                <svg style="width:14px;height:14px;fill:currentColor;margin-right:6px;" viewBox="0 0 24 24">
                                    <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                                </svg>
                                Find Jobs on LinkedIn
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Custom LinkedIn job finder
                st.markdown("""
                <div style="margin-top:16px; margin-bottom:8px; padding:16px; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px;">
                    <div style="font-weight:700; color:#0f2347; margin-bottom:4px; font-size:0.9rem;">
                        🔍 Custom LinkedIn Job Search
                    </div>
                    <div style="font-size:0.78rem; color:#64748b;">
                        Looking for something else? Enter any job title, company name, or technology to search directly on LinkedIn.
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                custom_query = st.text_input("Job Title / Skill to Search", placeholder="e.g. AWS Engineer, React Developer", key="custom_job_query")
                if st.button("Search on LinkedIn ↗", key="search_linkedin_custom"):
                    if custom_query.strip():
                        import urllib.parse
                        encoded_custom = urllib.parse.quote(custom_query.strip())
                        custom_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_custom}"
                        st.markdown(f"""
                        <div style="margin-top: 8px;">
                            <a href="{custom_url}" target="_blank" class="linkedin-btn" style="max-width: 280px;">
                                Open LinkedIn Search for "{custom_query}" ↗
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("Please enter a search term.")

            st.markdown("---")

            # ── Resume Analyser ───────────────────────
            st.markdown('<div class="section-title">📄 Resume Analyser</div>', unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload Resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], key="resume_up")
            if uploaded:
                name = uploaded.name.lower()
                resume_text = ""
                if name.endswith(".pdf"):
                    reader = PdfReader(uploaded)
                    resume_text = "".join(p.extract_text() or "" for p in reader.pages)
                elif name.endswith(".docx"):
                    import zipfile
                    import xml.etree.ElementTree as ET
                    try:
                        with zipfile.ZipFile(uploaded) as z:
                            xml_content = z.read('word/document.xml')
                        root = ET.fromstring(xml_content)
                        paragraphs = []
                        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                        for p in root.findall('.//w:p', ns):
                            p_text = "".join(t.text for t in p.findall('.//w:t', ns) if t.text)
                            if p_text:
                                paragraphs.append(p_text)
                        resume_text = "\n".join(paragraphs)
                    except Exception as e:
                        st.error(f"Error reading DOCX file: {e}")
                elif name.endswith(".txt"):
                    try:
                        resume_text = uploaded.getvalue().decode("utf-8", errors="ignore")
                    except Exception as e:
                        st.error(f"Error reading TXT file: {e}")

                if not resume_text.strip():
                    st.warning("Could not extract text. Please ensure the file contains extractable text content.")
                else:
                    try:
                        system = (
                            "You are an expert placement counsellor. "
                            "Analyse resumes for tech company placements using these sections: "
                            "1. **Strengths**  2. **Gaps & Improvements**  "
                            "3. **Skills to Add**  4. **Overall Score /10**"
                        )
                        st.markdown("**🤖 Balaji's Resume Review:**")
                        st.write_stream(ask_gemini_stream(system, f"Resume:\n{resume_text}"))
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

            # ── Ask Balaji Student ────────────────────
            st.markdown('<div class="section-title">🤖 Ask Balaji</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="info-card" style="background:#fffbeb;border-color:#fcd34d;">
            <span style="color:#92400e;font-size:0.88rem;">
            💡 Ask about interview prep, company details, profile improvement, or any placement doubt.
            </span></div>""", unsafe_allow_html=True)

            stu_q = st.text_input("Your question", placeholder="e.g. How do I prepare for Accenture?", key="stu_q")
            if st.button("Ask Balaji 🤖", key="ask_stu"):
                if not stu_q.strip():
                    st.warning("Please enter a question.")
                else:
                    comp_ctx = (load_companies(COMPANY_FILE).to_string(index=False)
                                if os.path.exists(COMPANY_FILE) else "No company data.")
                    system = (
                        "You are Balaji, a friendly AI placement assistant at Sona College of Technology. "
                        "Give practical, specific, encouraging advice."
                    )
                    user_msg = (
                        f"Student: Name={name} | Dept={department} | CGPA={cgpa} | Skills={skills}\n\n"
                        f"Companies:\n{comp_ctx}\n\nQuestion: {stu_q}"
                    )
                    try:
                        st.markdown("**🤖 Balaji says:**")
                        st.write_stream(ask_gemini_stream(system, user_msg))
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <h4>🎓 Sona College of Technology</h4>
    <p>Autonomous | NAAC A++ | AICTE Approved</p>
    <p style="margin-top:8px;color:rgba(255,255,255,0.4);font-size:0.78rem;">
        © 2026 Department of Training &amp; Placement &nbsp;·&nbsp; AI Placement Portal v2.0
    </p>
</div>
""", unsafe_allow_html=True)
