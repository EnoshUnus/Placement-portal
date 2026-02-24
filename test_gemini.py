from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("Loaded key:", api_key)

client = genai.Client(api_key=api_key)

# PRINT MODEL NAME TO CONFIRM
model_name = "gemini-1.5-flash-latest"
print("Using model:", model_name)

response = client.models.generate_content(
    model=model_name,
    contents="Say hello. Confirm Gemini API is working."
)

print(response.text)
