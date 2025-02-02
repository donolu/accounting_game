import streamlit as st
import base64
import json
import os
import random
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


# ---------------------------------------------
# Utility Functions
# ---------------------------------------------
def fix_base64_padding(b64_string):
    """Fix Base64 padding issues by adding missing '=' characters."""
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)
    return b64_string


def load_credentials():
    """Load Google Sheets credentials from Streamlit Secrets or a local file."""
    try:
        if "GOOGLE_SHEETS_CREDENTIALS_B64" in st.secrets:
            creds_b64 = st.secrets["GOOGLE_SHEETS_CREDENTIALS_B64"]
            creds_b64 = fix_base64_padding(creds_b64)
            creds_json = base64.b64decode(creds_b64).decode("utf-8")
            creds_dict = json.loads(creds_json)
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace(
                    "\\n", "\n"
                )
            return Credentials.from_service_account_info(
                creds_dict,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        elif os.path.exists("streamlit-sheets-key.json"):
            return Credentials.from_service_account_file(
                "streamlit-sheets-key.json",
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        else:
            st.error(
                "❌ No Google Sheets credentials found. Ensure GOOGLE_SHEETS_CREDENTIALS_B64 is set in Streamlit Secrets."
            )
            return None
    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Parsing Error: {e}")
        return None
    except base64.binascii.Error as e:
        st.error(f"❌ Base64 Decoding Error: {e}")
        return None


# ---------------------------------------------
# Data Loading & Caching
# ---------------------------------------------
@st.cache_data
def load_questions():
    """Load questions from a local JSON file."""
    try:
        with open("questions.json", "r") as file:
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading questions: {e}")
        return []


@st.cache_resource
def connect_to_gsheets():
    """Connect to Google Sheets using cached credentials."""
    creds = load_credentials()
    if creds is None:
        st.error("❌ Failed to authenticate Google Sheets.")
        return None
    client = gspread.authorize(creds)
    try:
        sheet = client.open(
            "StudentScores"
        ).sheet1  # Ensure the sheet name matches your Google Sheet name
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error connecting to Google Sheets: {e}")
        return None


# ---------------------------------------------
# Score Saving and Leaderboard Functions
# ---------------------------------------------
def save_score(name, score, attempt):
    """Save the student score to Google Sheets."""
    try:
        sheet = connect_to_gsheets()
        if sheet is None:
            st.error("⚠️ Google Sheets connection failed. Cannot save score.")
            return

        # Add headers if the sheet is empty
        existing_data = sheet.get_all_values()
        if not existing_data:
            sheet.append_row(["Name", "Score", "Attempt Number", "Timestamp"])

        sheet.append_row(
            [name, score, attempt, datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        )
        st.success(f"✅ Score for {name} saved successfully!")
    except Exception as e:
        st.error(f"⚠️ Error saving score: {e}")


def get_leaderboard():
    """Fetch and display the top scores with ranking numbers (index hidden)."""
    st.subheader("🏆 Leaderboard (Top 10)")
    sheet = connect_to_gsheets()
    if sheet is None:
        st.error("⚠️ Cannot fetch leaderboard. Google Sheets connection failed.")
        return

    try:
        data = sheet.get_all_values()
        if len(data) < 2:
            st.info("📊 No scores available yet.")
            return

        df = pd.DataFrame(data[1:], columns=data[0])
        df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
        df.dropna(subset=["Score"], inplace=True)
        df_sorted = (
            df.sort_values(by="Score", ascending=False).head(10).reset_index(drop=True)
        )
        df_sorted.insert(0, "Rank", range(1, len(df_sorted) + 1))
        html_table = df_sorted.to_html(index=False)
        st.markdown(html_table, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Error retrieving leaderboard: {e}")


# ---------------------------------------------
# Session State Initialization
# ---------------------------------------------
if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.question_number = 1
    st.session_state.streak = 0
    # Load the complete question bank.
    st.session_state.questions = load_questions()
    st.session_state.total_questions = len(st.session_state.questions)
    # Shuffle the questions and create a list for remaining questions (to avoid repeats)
    random.shuffle(st.session_state.questions)
    st.session_state.remaining_questions = st.session_state.questions.copy()
    st.session_state.username = ""
    st.session_state.attempt = 1  # First game attempt
    # Initialize the review list for storing answered question details.
    st.session_state.review = []
    # Initialize a flag to track if the score has been saved already.
    st.session_state.score_saved = False


# ---------------------------------------------
# Student Login Form (Name must be entered before any question is shown)
# ---------------------------------------------
if not st.session_state.username:
    st.markdown(
        "<h2 style='text-align: center;'>🎓 Enter Your Name</h2>",
        unsafe_allow_html=True,
    )
    username = st.text_input(
        "Enter Your Name",
        placeholder="Your Name",
        key="username_input",
        label_visibility="collapsed",
    )
    if st.button("Start Game", use_container_width=True):
        if username.strip():
            st.session_state.username = username.strip()
            st.success(f"Welcome, {st.session_state.username}!")
            st.rerun()
        else:
            st.warning("Please enter your name.")
    st.stop()


# ---------------------------------------------
# Main Game Logic
# ---------------------------------------------
# Branch between Game Over and Game In Progress:
if st.session_state.question_number > st.session_state.total_questions:
    # --- Game Over Screen ---
    st.title("💷 Debit or Credit Challenge - Game Over!")
    st.write(
        f"**Name:** {st.session_state.username}  |  "
        f"**Attempt:** {st.session_state.attempt}  |  "
        f"**Final Score:** {st.session_state.score}  |  "
        f"**Final Streak:** {st.session_state.streak}"
    )
    # Only save the score once per attempt.
    if not st.session_state.score_saved:
        save_score(
            st.session_state.username, st.session_state.score, st.session_state.attempt
        )
        st.session_state.score_saved = True

    st.write("📊 Leaderboard:")
    get_leaderboard()

    # Button to review answers.
    if st.button("Review Answers", use_container_width=True):
        st.subheader("Review Answers")
        if st.session_state.review:
            df_review = pd.DataFrame(st.session_state.review)
            html_review = df_review.to_html(index=False)  # Hide the DataFrame index
            st.markdown(html_review, unsafe_allow_html=True)
        else:
            st.info("No review data available.")

    if st.button("Play Again", use_container_width=True):
        st.session_state.attempt += 1  # Increment attempt counter
        st.session_state.score = 0
        st.session_state.question_number = 1
        st.session_state.streak = 0
        st.session_state.questions = load_questions()
        st.session_state.total_questions = len(st.session_state.questions)
        random.shuffle(st.session_state.questions)
        st.session_state.remaining_questions = st.session_state.questions.copy()
        st.session_state.review = []  # Reset review data for the new attempt
        st.session_state.score_saved = False  # Reset the score-saved flag
        st.rerun()
else:
    # --- Game In Progress ---
    st.title("💷 Debit or Credit Challenge")
    st.write(
        f"**Name:** {st.session_state.username}  |  "
        f"**Attempt:** {st.session_state.attempt}  |  "
        f"**Question:** {st.session_state.question_number}/{st.session_state.total_questions}  |  "
        f"**Score:** {st.session_state.score}  |  "
        f"**Streak:** {st.session_state.streak}"
    )

    # Get the current question (first in the remaining list)
    current_question = st.session_state.remaining_questions[0]
    st.subheader(current_question["transaction"])

    # Set prompt and determine correct answer based on question_type.
    question_type = current_question.get("question_type", "debit").lower()
    if question_type == "credit":
        prompt_text = "**Which account should be credited?**"
        correct_answer = current_question["correct_credit"]
    else:
        prompt_text = "**Which account should be debited?**"
        correct_answer = current_question["correct_debit"]

    st.write(prompt_text)

    # Shuffle answer options so their positions vary.
    accounts = current_question["accounts"].copy()
    random.shuffle(accounts)
    for account in accounts:
        if st.button(account):
            points_awarded = 0
            if account == correct_answer:
                points_awarded = 10 * (1 + st.session_state.streak // 3)
                st.session_state.score += points_awarded
                st.session_state.streak += 1
                feedback = f"✅ Correct! {current_question['explanation']}"
            else:
                st.session_state.streak = 0
                feedback = f"❌ Incorrect! {current_question['explanation']}"
            st.write(feedback)

            # Save this question's review details.
            review_item = {
                "Transaction": current_question["transaction"],
                "Question Type": question_type.capitalize(),
                "Your Answer": account,
                "Correct Answer": correct_answer,
                "Explanation": current_question["explanation"],
                "Points Awarded": points_awarded,
            }
            st.session_state.review.append(review_item)

            # Remove the question so it isn’t repeated.
            st.session_state.remaining_questions.pop(0)
            st.session_state.question_number += 1

            st.rerun()
