import streamlit as st
import base64
import json
import os
import random
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


# Load Google Sheets credentials
def load_credentials():
    """Load Google Sheets credentials from environment variables or local file."""
    try:
        # ✅ Load from Streamlit Secrets (Deployed Mode)
        if "GOOGLE_SHEETS_CREDENTIALS_B64" in st.secrets:
            creds_b64 = st.secrets["GOOGLE_SHEETS_CREDENTIALS_B64"]
            creds_json = base64.b64decode(creds_b64).decode()  # Decode Base64 to JSON
            creds_dict = json.loads(creds_json)  # Convert to Python dictionary
            return Credentials.from_service_account_info(
                creds_dict,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        # ✅ Load from Local JSON File (Fallback)
        else:
            return Credentials.from_service_account_file(
                "streamlit-sheets-key.json",
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Parsing Error: {e}")
        return None


# Load questions from JSON file
@st.cache_data
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


# Google Sheets Configuration
def connect_to_gsheets():
    creds = load_credentials()
    client = gspread.authorize(creds)
    return client.open(
        "StudentScores"
    ).sheet1  # Ensure this matches your Google Sheet name


# **Function to Save Scores**
def save_score(name, score, attempt):
    """Saves student scores to Google Sheets."""
    try:
        sheet = connect_to_gsheets()
        data = sheet.get_all_values()  # Fetch all data to check if headers exist

        # If the sheet is empty, add headers first
        if len(data) == 0:
            sheet.append_row(["Name", "Score", "Attempt Number", "Timestamp"])

        # Append the new row with student data
        sheet.append_row(
            [name, score, attempt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        )
        st.success("✅ Score saved successfully!")
    except Exception as e:
        st.error(f"⚠️ Error saving score: {e}")


# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.streak = 0
    st.session_state.questions = load_questions()
    st.session_state.username = ""
    st.session_state.attempt = 1  # Track attempt number

# **Student Login Form (Centered)**
if not st.session_state.username:
    st.markdown(
        "<h2 style='text-align: center;'>🎓 Enter Your Name</h2>",
        unsafe_allow_html=True,
    )

    # Centered text input
    username = st.text_input(
        "Enter Your Name",
        placeholder="Your Name",
        key="username_input",
        label_visibility="collapsed",
    )

    if st.button("Start Game", use_container_width=True):
        if username.strip():
            st.session_state.username = username
            st.session_state.attempt += 1  # Increment attempt number
            st.success(f"Welcome, {username}!")
            st.rerun()
        else:
            st.warning("Please enter your name.")
else:
    # Game Title
    st.title("💰 Debit or Credit Challenge")

    # Show game stats
    st.write(
        f"**Name:** {st.session_state.username}  |  **Attempt:** {st.session_state.attempt}  |  **Round:** {st.session_state.round}/10  |  **Score:** {st.session_state.score}  |  **Streak:** {st.session_state.streak}"
    )

    # Load a question
    if st.session_state.round <= 10 and st.session_state.questions:
        current_question = random.choice(st.session_state.questions)
        st.subheader(current_question["transaction"])
        st.write("**Which account should be debited?**")

        for account in current_question["accounts"]:
            if st.button(account):
                if account == current_question["correct_debit"]:
                    st.session_state.score += 10 * (1 + st.session_state.streak // 3)
                    st.session_state.streak += 1
                    feedback = f"✅ Correct! {current_question['explanation']}"
                else:
                    st.session_state.streak = 0
                    feedback = f"❌ Incorrect! {current_question['explanation']}"

                st.write(feedback)
                st.session_state.round += 1

                if st.session_state.round > 10:
                    st.write(f"🎉 Game Over! Final Score: {st.session_state.score}")
                    save_score(
                        st.session_state.username,
                        st.session_state.score,
                        st.session_state.attempt,
                    )  # Save score

                    if st.button("Play Again", use_container_width=True):
                        st.session_state.score = 0
                        st.session_state.round = 1
                        st.session_state.streak = 0
                        st.session_state.questions = load_questions()
                        st.rerun()
                else:
                    st.rerun()
    else:
        st.write("🎉 No more questions.")
        if st.button("Play Again", use_container_width=True):
            st.session_state.score = 0
            st.session_state.round = 1
            st.session_state.streak = 0
            st.session_state.questions = load_questions()
            st.rerun()
