import streamlit as st
import pandas as pd
import joblib
import os
import hashlib
from dotenv import load_dotenv
from google import genai
from PyPDF2 import PdfReader

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="AI Placement Portal",
    layout="wide",
    page_icon="🎓"
)

# ==============================
# PROFESSIONAL SONA UI
# ==============================
st.markdown("""
<style>
.main {
    background-color: #ffffff;
}
.sona-header {
    background: linear-gradient(90deg,#002147,#0b3d91);
    padding: 30px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 30px;
}
.sona-header h1 {
    color: white;
    font-size: 34px;
    font-weight: 700;
    margin-bottom: 5px;
}
.sona-header p {
    color: #e6e6e6;
    font-size: 18px;
    margin: 0;
}
section[data-testid="stSidebar"] {
    background-color: #002147;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
.stButton>button {
    background-color: #0b3d91;
    color: white;
    border-radius: 8px;
    height: 42px;
    font-weight: 600;
}
.stButton>button:hover {
    background-color: #061f4a;
}
.sona-footer {
    background-color: #002147;
    color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    margin-top: 40px;
}
</style>

<div class="sona-header">
    <h1>Sona College of Technology</h1>
    <p>AI Powered Smart Placement Management System</p>
</div>
""", unsafe_allow_html=True)

# ==============================
# LOAD ENV
# ==============================
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

# ==============================
# LOAD MODEL
# ==============================
model = joblib.load("placement_model.pkl")

# ==============================
# SAFE STRING
# ==============================
def safe_str(val):
    if pd.isna(val):
        return ""
    return str(val).strip().lower()

# ==============================
# PASSWORD HASH
# ==============================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ==============================
# USER SYSTEM
# ==============================
users_file = "users.csv"

def load_users():
    if not os.path.exists(users_file):
        df = pd.DataFrame(columns=["email","password","role"])
        df.to_csv(users_file,index=False)
        return df
    return pd.read_csv(users_file)

def register_user(email,password,role):
    users = load_users()

    if not email.endswith("@gmail.com"):
        return "Invalid college email"

    if "email" in users.columns and email in users["email"].values:
        return "User already exists"

    new_user = pd.DataFrame([{
        "email": email,
        "password": hash_password(password),
        "role": role
    }])

    users = pd.concat([users,new_user],ignore_index=True)
    users.to_csv(users_file,index=False)
    return "Success"

def authenticate(email,password):
    users = load_users()
    if "email" not in users.columns:
        return None

    user = users[users["email"]==email]
    if user.empty:
        return None

    if user.iloc[0]["password"] == hash_password(password):
        return user.iloc[0]["role"]

    return None

# ==============================
# SESSION
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
    st.session_state.role=None

def logout():
    st.session_state.logged_in=False
    st.session_state.role=None
    st.rerun()

# ==============================
# LOGIN
# ==============================
def login_page():
    st.subheader("🔐 Login to Placement Portal")

    tab1,tab2 = st.tabs(["Login","Register"])

    with tab1:
        email = st.text_input("College Gmail")
        password = st.text_input("Password",type="password")
        if st.button("Login"):
            role = authenticate(email,password)
            if role:
                st.session_state.logged_in=True
                st.session_state.role=role
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        email = st.text_input("New Gmail")
        password = st.text_input("New Password",type="password")
        role = st.selectbox("Role",["student","admin"])
        if st.button("Register"):
            result = register_user(email,password,role)
            if result=="Success":
                st.success("Registered Successfully")
            else:
                st.error(result)

if not st.session_state.logged_in:
    login_page()
    st.stop()

# =====================================================
# ADMIN PANEL
# =====================================================
if st.session_state.role=="admin":

    st.sidebar.success("Admin Panel")
    if st.sidebar.button("Logout"):
        logout()

    st.header("📂 Import Data")

    students_file = st.file_uploader("Upload students.csv", type=["csv"])
    if students_file:
        pd.read_csv(students_file).to_csv("students.csv", index=False)
        st.success("Students imported successfully")

    companies_file = st.file_uploader("Upload companies.csv", type=["csv"])
    if companies_file:
        pd.read_csv(companies_file).to_csv("companies.csv", index=False)
        st.success("Companies imported successfully")

    if os.path.exists("students.csv") and os.path.exists("companies.csv"):

        students = pd.read_csv("students.csv")
        companies = pd.read_csv("companies.csv")

        st.divider()
        st.header("🏢 Company Eligibility Analysis")

        selected_company = st.selectbox(
            "Select Company",
            companies["Company_Name"].dropna().unique()
        )

        if selected_company:
            company = companies[companies["Company_Name"]==selected_company].iloc[0]

            eligible=[]
            for _,student in students.iterrows():
                if (
                    safe_str(student["Department"])==safe_str(company["Required_Department"])
                    and student["CGPA"]>=company["Minimum_CGPA"]
                    and safe_str(company["Required_Skill"]) in safe_str(student["Skills"])
                ):
                    eligible.append(student["Name"])

            total=len(students)
            eligible_count=len(eligible)
            percent=(eligible_count/total)*100 if total>0 else 0

            col1,col2,col3=st.columns(3)
            col1.metric("Total Students",total)
            col2.metric("Eligible Students",eligible_count)
            col3.metric("Eligibility %",f"{round(percent,2)}%")

            chart=pd.DataFrame({
                "Category":["Eligible","Not Eligible"],
                "Count":[eligible_count,total-eligible_count]
            })
            st.bar_chart(chart.set_index("Category"))

            st.subheader("Eligible Students")
            for s in eligible:
                st.success(s)

    st.divider()
    st.header("🤖 Ask Balaji (Admin Mode)")

    question = st.text_input("Ask about students or companies")
    if st.button("Ask Balaji Admin") and client:
        students=pd.read_csv("students.csv")
        companies=pd.read_csv("companies.csv")

        context=f"""
        Students:
        {students.to_string()}

        Companies:
        {companies.to_string()}

        Answer ONLY using above data.
        """

        response=client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context+"\nQuestion:\n"+question
        )

        st.markdown(response.text)

# =====================================================
# STUDENT PANEL
# =====================================================
elif st.session_state.role=="student":

    st.sidebar.success("Student Panel")
    if st.sidebar.button("Logout"):
        logout()

    st.header("🎓 Student Panel")

    register_no = st.text_input("Enter Student_ID (Example: S001)")

    if register_no and os.path.exists("students.csv"):

        students = pd.read_csv("students.csv")

        if "Student_ID" not in students.columns:
            st.error("Student_ID column not found in CSV")
            st.stop()

        student = students[
            students["Student_ID"].astype(str).str.upper()==register_no.upper()
        ]

        if not student.empty:

            student=student.iloc[0]
            name=student["Name"]
            department=student["Department"]
            cgpa=student["CGPA"]
            skills=student["Skills"]

            st.success(f"Welcome {name}")

            if st.button("Predict Placement"):

                input_features=pd.DataFrame([{
                    "CGPA":cgpa,
                    "Internship":1,
                    "Projects":2,
                    "Communication":3
                }])

                probability=model.predict_proba(input_features)[0][1]*100

                col1,col2=st.columns(2)

                with col1:
                    st.subheader("📊 Placement Probability")
                    st.success(f"{round(probability,2)}%")
                    st.progress(int(probability))

                with col2:
                    st.subheader("🏆 Best Company Match")
                    companies=pd.read_csv("companies.csv")

                    best=None
                    best_score=0

                    for _,company in companies.iterrows():
                        score=0
                        if safe_str(department)==safe_str(company["Required_Department"]):
                            score+=40
                        if cgpa>=company["Minimum_CGPA"]:
                            score+=30
                        if safe_str(company["Required_Skill"]) in safe_str(skills):
                            score+=30
                        if score>best_score:
                            best_score=score
                            best=company["Company_Name"]

                    st.success(f"{best} ({best_score}% match)")

            st.divider()
            st.subheader("📄 Upload Resume")

            uploaded=st.file_uploader("Upload Resume (PDF)",type=["pdf"])
            if uploaded and client:
                reader=PdfReader(uploaded)
                text=""
                for page in reader.pages:
                    text+=page.extract_text()

                response=client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents="Analyze resume and suggest improvements."
                )
                st.markdown(response.text)

            st.divider()
            st.header("🤖 Ask Balaji")

            student_question=st.text_input("Ask your placement doubts")

            if st.button("Ask Balaji Student") and client:
                companies=pd.read_csv("companies.csv")

                context=f"""
                Student:
                Name:{name}
                Department:{department}
                CGPA:{cgpa}
                Skills:{skills}

                Companies:
                {companies.to_string()}
                """

                response=client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=context+"\nQuestion:\n"+student_question
                )
                st.markdown(response.text)

        else:
            st.error("Invalid Student_ID")

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div class="sona-footer">
    <h4>Sona College of Technology</h4>
    <p>Autonomous | NAAC A++ | AICTE Approved</p>
    <p>© 2026 Department of Training & Placement</p>
</div>
""", unsafe_allow_html=True)