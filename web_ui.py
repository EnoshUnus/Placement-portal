from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import pandas as pd
import os
from dotenv import load_dotenv
from google import genai
import joblib
from datetime import datetime
import uuid
import secrets

# load environment and initialize Gemini client
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# In-memory user store (use database in production)
users_db = {}
user_sessions = {}
user_history = {}


# In-memory user store (use database in production)
users_db = {}
user_sessions = {}
user_history = {}


# keep track of any extra CSVs uploaded at runtime
extra_files = []

def _load_csv(name):
    return pd.read_csv(name) if os.path.exists(name) else pd.DataFrame()


@app.route("/")
def index():
    """Redirect to login if not authenticated."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('chat'))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login page."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        if not email or not password:
            return render_template("login.html", error="Email and password required")
        
        # Verify credentials
        if email in users_db and users_db[email]["password"] == password:
            user_id = users_db[email]["user_id"]
            session['user_id'] = user_id
            session['email'] = email
            return redirect(url_for('chat'))
        else:
            return render_template("login.html", error="Invalid email or password")
    
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page for new users."""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        role = request.form.get("role", "student").strip()
        name = request.form.get("name", "").strip()
        password = request.form.get("password", "").strip()
        
        if not email or not role or not name or not password:
            return render_template("register.html", error="All fields required")
        
        if email in users_db:
            return render_template("register.html", error="Email already registered")
        
        user_id = str(uuid.uuid4())
        
        users_db[email] = {
            "user_id": user_id,
            "password": password,
            "role": role,
            "name": name,
            "created_at": datetime.now().isoformat()
        }
        
        user_history[user_id] = []
        
        return render_template("register.html", 
                             success=True,
                             email=email)
    
    return render_template("register.html")


@app.route("/logout")
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for('login'))


@app.route("/chat")
def chat():
    """Render the chat interface."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("chat.html")


# keep track of any extra CSVs uploaded at runtime
extra_files = []

def _load_csv(name):
    return pd.read_csv(name) if os.path.exists(name) else pd.DataFrame()


def _load_all_context_data():
    """Return a tuple (students, companies, extras_list).

    extras_list is a list of (filename, df) for any uploaded CSVs.
    """
    students = _load_csv("students.csv")
    companies = _load_csv("companies.csv")
    extras = []
    for path in extra_files:
        try:
            df = pd.read_csv(path)
            extras.append((os.path.basename(path), df))
        except Exception:
            pass
    return students, companies, extras


@app.route("/api/history")
def api_history():
    """Get user's chat history."""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = session['user_id']
    history = user_history.get(user_id, [])
    return jsonify({"history": history})


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """REST endpoint that handles chat queries with authentication."""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    payload = request.get_json() or {}
    role = payload.get("role", "student")
    question = payload.get("question", "")
    student_id = payload.get("student_id", "")

    if not client:
        return jsonify({"answer": "Gemini client not configured (API key missing)"}), 500

    # load data and any uploaded extras
    students, companies, extras = _load_all_context_data()

    if role == "admin":
        context = f"""
Students:
{students.to_string()}

Companies:
{companies.to_string()}
"""
        for name, df in extras:
            context += f"\n\nExtra file {name}:\n" + df.to_string()
    elif role == "student":
        if students.empty:
            return jsonify({"answer": "students.csv not found"}), 500

        if student_id:
            student = students[students["Student_ID"].astype(str).str.upper() == student_id.upper()]
        else:
            student = pd.DataFrame()

        if student_id and student.empty:
            return jsonify({"answer": "Invalid Student ID"})

        context = ""
        if not student.empty:
            s = student.iloc[0]
            name = s.get("Name", "")
            department = s.get("Department", "")
            cgpa = s.get("CGPA", "")
            skills = s.get("Skills", "")
            extra_skills = s.get("Extra_Skills", "")
            extra_knowledge = s.get("Extra_Knowledge", "")
            certifications = s.get("Certifications", "")
            context += f"""
Student:
Name:{name}
Department:{department}
CGPA:{cgpa}
Skills:{skills}
Extra Skills:{extra_skills}
Extra Knowledge:{extra_knowledge}
Certifications:{certifications}

"""
        context += f"""
Companies:
{companies.to_string()}
"""
        for name, df in extras:
            context += f"\n\nExtra file {name}:\n" + df.to_string()
    else:
        return jsonify({"answer": "`role` must be either 'student' or 'admin'"}), 400

    # ask the model to return machine-readable JSON and then parse it
    core_instruction = (
        "\n\nINSTRUCTION: Answer ONLY using the data provided above (Students and Companies). "
        "Keep responses short and concise—one or two sentences maximum when possible. "
        "Do NOT invent, assume, or hallucinate any facts that are not present in the data. "
        "If the requested information is not available in the data, return empty fields or include a 'note' field with value 'insufficient data'."
    )

    json_instruction = (
        "\n\nIMPORTANT: Reply with a VALID JSON object ONLY (no explanatory text) using this schema:\n"
        "{\"summary\":\"short summary\",\"eligible_companies\":[{\"company\":\"name\",\"eligible\":true,\"reason\":\"...\"}],\"best_match\":{\"company\":\"\",\"score\":0},\"suggestions\":[\"...\"],\"note\":\"...\"}"
        "\nIf a field is not applicable, return an empty string, empty array, null, or set 'note' to 'insufficient data'."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=context + core_instruction + "\nQuestion:\n" + question + json_instruction,
    )

    text = response.text
    # remove any surrounding code fences and leading language markers
    cleaned = text.strip()
    # strip ``` and ```json or ```json\n prefixes/suffixes
    if cleaned.startswith("```") and cleaned.endswith("```"):
        cleaned = cleaned[3:-3].strip()
    if cleaned.lower().startswith("json"):
        cleaned = cleaned[4:].strip()
    # also remove single backticks
    cleaned = cleaned.strip('`').strip()

    parsed = None
    try:
        # locate the first { and last } in the cleaned text and parse
        start = cleaned.find('{')
        end = cleaned.rfind('}')
        if start != -1 and end != -1 and end > start:
            candidate = cleaned[start:end+1]
            parsed = json.loads(candidate)
    except Exception:
        parsed = None

    # use cleaned text as answer_text for display
    text = cleaned

    # compute chart data only if user explicitly asks for chart/probability
    chart = None
    if role == "student" and student_id and any(w in question.lower() for w in ("chart", "probability", "probabilities")):
        chart = compute_chart(student_id)

    result = {"answer_text": text}
    if parsed:
        result["answer_json"] = parsed
    if chart:
        result["chart"] = chart
    
    # Save to history
    user_id = session['user_id']
    if user_id not in user_history:
        user_history[user_id] = []
    
    user_history[user_id].append({
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "question": question,
        "student_id": student_id,
        "answer_preview": text[:100] if text else ""
    })
    
    return jsonify(result)




@app.route("/api/upload", methods=["POST"])
def api_upload():
    """Accept a CSV upload and keep it for future context."""
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    if 'file' not in request.files:
        return jsonify({"status": "no file"}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({"status": "empty filename"}), 400
    # store in workspace
    save_path = os.path.join(os.getcwd(), f.filename)
    f.save(save_path)
    extra_files.append(save_path)
    return jsonify({"status": "uploaded", "filename": f.filename})


def compute_chart(student_id):
    """Return labels and values for match scores per company for given student."""
    students = _load_csv("students.csv")
    companies = _load_csv("companies.csv")
    if students.empty or companies.empty:
        return None
    student = students[students["Student_ID"].astype(str).str.upper() == student_id.upper()]
    if student.empty:
        return None
    s = student.iloc[0]
    department = str(s.get("Department", "")).lower().strip()
    cgpa = float(s.get("CGPA", 0)) if s.get("CGPA") else 0
    skills = str(s.get("Skills", "")).lower()
    labels = []
    values = []
    for _, company in companies.iterrows():
        score = 0
        req_dept = str(company.get("Required_Department", "")).lower().strip()
        min_cgpa = float(company.get("Minimum_CGPA", 0)) if company.get("Minimum_CGPA") else 0
        req_skill = str(company.get("Required_Skill", "")).lower().strip()
        
        # Department match: 40%
        if department == req_dept:
            score += 40
        
        # CGPA match: 30%
        if cgpa >= min_cgpa:
            score += 30
        
        # Skill match: 30%
        if req_skill and req_skill in skills:
            score += 30
        
        labels.append(company.get("Company_Name", "Unknown"))
        values.append(score)
    
    return {"labels": labels, "values": values}


if __name__ == "__main__":
    # run on localhost; remove debug=True in production
    app.run(host="0.0.0.0", port=5000, debug=True)
