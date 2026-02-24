import pandas as pd
import joblib
import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Initialize Gemini client
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Load student and company data
students = pd.read_csv("students.csv")
companies = pd.read_csv("companies.csv")

# Load trained ML model
model = joblib.load("placement_model.pkl")

for _, student in students.iterrows():

    print("\n============================")
    print(f"Student: {student['Name']}")

    # ML Prediction
    input_features = [[
        student["CGPA"],
        1,
        2,
        3
    ]]

    probability = model.predict_proba(input_features)[0][1] * 100
    print(f"Placement Probability: {round(probability, 2)}%")

    print("Eligible Companies:")

    eligible_list = []

    for _, company in companies.iterrows():

        eligible = True

        if student["Department"] != company["Required_Department"]:
            eligible = False

        if student["CGPA"] < company["Minimum_CGPA"]:
            eligible = False

        if company["Required_Skill"] not in str(student["Skills"]):
            eligible = False

        if eligible:
            eligible_list.append(f"{company['Company_Name']} ({company['Job_Role']})")

    if eligible_list:
        for comp in eligible_list:
            print("  -", comp)
    else:
        print("  No matching companies")

    # 🤖 Gemini AI Career Analysis
    prompt = f"""
    Student Profile:
    Name: {student['Name']}
    Department: {student['Department']}
    CGPA: {student['CGPA']}
    Skills: {student['Skills']}
    Certifications: {student['Certifications']}
    Placement Probability: {round(probability,2)}%

    Provide:
    1. Strengths
    2. Weaknesses
    3. Skills to improve
    4. 3-month preparation roadmap
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print("\nAI Career Analysis:")
    print(response.text)