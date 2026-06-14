# Placement Portal

This repository contains an AI-powered placement management system for Sona College of Technology.  The core application is written using Streamlit (`app.py`), and there are several supporting scripts (`train_model.py`, `main_system.py`, etc.).

## New HTML Chat Interface

A simple chat‑style front‑end has been added that synchronizes with the same CSV/AI backend used by the Streamlit application.  It uses Flask to expose a REST API and an accompanying HTML/JavaScript user interface.

### Running the chat UI

1. Install dependencies (add to your `requirements.txt` or `pip install` manually):

   ```bash
   pip install flask pandas python-dotenv google-genai
   ```

2. Ensure your `.env` contains the `GEMINI_API_KEY` environment variable.
3. Place your `students.csv` and `companies.csv` files in the project root (or upload via the Streamlit admin panel).
4. Start the server:

   ```bash
   python web_ui.py
   ```

5. In your browser navigate to `http://localhost:5000/`.

The chat page lets you choose between **Student** and **Admin** modes.  When you send a question the backend reads the CSVs, builds context and forwards it to the Gemini model; the answer is displayed in chat bubbles.

### Extending the interface

- You can refactor shared functionality (e.g. data loading, authentication) into a common module if you want to avoid duplication between `app.py` and `web_ui.py`.
- Additional API endpoints (eligibility checks, prediction, resume analysis) can be added under `/api/...` and hooked into the JavaScript in `templates/chat.html`.

## Existing Streamlit App

The `app.py` file continues to provide the original Streamlit‑based UI with login, data import, analysis and the ‘Ask Balaji’ chatbot sections.

## License

(Include your license here.)
