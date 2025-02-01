import streamlit as st
import json
import random
import time

import qrcode
from io import BytesIO

st.write("Streamlit version:", st.__version__)

# App URL (replace with actual deployed app link)
app_url = "https://accountinggame.streamlit.app"

# Generate QR code
qr = qrcode.make(app_url)
qr_bytes = BytesIO()
qr.save(qr_bytes, format="PNG")

# Display QR code in the sidebar
st.sidebar.image(qr_bytes.getvalue(), caption="Scan to Play!", use_container_width=True)

# -------------------------
# PLAYER NAME FORM SECTION
# -------------------------
if "player_name" not in st.session_state:
    with st.form(key="player_info"):
        st.write("## Enter Your Name to Start")
        player_name = st.text_input("Player Name")
        submit_button = st.form_submit_button(label="Start Game")
        if submit_button:
            if player_name.strip() != "":
                st.session_state.player_name = player_name.strip()
                # Optionally initialize other session state variables here
            else:
                st.error("Please enter a valid name.")

    # Stop further execution until the name is provided.
    st.stop()

# -------------------------
# GAME LOGIC BELOW
# -------------------------


# Load questions from JSON file
@st.cache_data
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


# Initialize session state for game variables
if "score" not in st.session_state:
    st.session_state.score = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "round" not in st.session_state:
    st.session_state.round = 1
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "questions" not in st.session_state:
    st.session_state.questions = load_questions()


# Function to get a new question
def get_new_question():
    if st.session_state.questions:
        st.session_state.current_question = random.choice(st.session_state.questions)
        st.session_state.questions.remove(st.session_state.current_question)
    else:
        st.session_state.current_question = None


# Initialize the first question if not already set
if st.session_state.current_question is None:
    get_new_question()

# UI Layout
st.title("💰 Debit or Credit Challenge")
st.write(f"**Welcome, {st.session_state.player_name}!**")

# Show round, score, and streak
st.write(
    f"**Round:** {st.session_state.round}/10 | **Score:** {st.session_state.score} | **Streak:** {st.session_state.streak}"
)

# Display the current question if available
if st.session_state.current_question:
    st.subheader(st.session_state.current_question["transaction"])
    st.write("**Which account should be debited?**")

    # Answer buttons
    for account in st.session_state.current_question["accounts"]:
        if st.button(account):
            if account == st.session_state.current_question["correct_debit"]:
                st.session_state.score += 10 * (1 + st.session_state.streak // 3)
                st.session_state.streak += 1
                feedback = (
                    f"✅ Correct! {st.session_state.current_question['explanation']}"
                )
            else:
                st.session_state.streak = 0
                feedback = (
                    f"❌ Incorrect! {st.session_state.current_question['explanation']}"
                )

            st.write(feedback)
            time.sleep(1)

            # Move to next round or finish game
            if st.session_state.round >= 10:
                st.write(f"🎉 Game Over! Final Score: {st.session_state.score}")
                if st.button("Play Again"):
                    st.session_state.score = 0
                    st.session_state.round = 1
                    st.session_state.streak = 0
                    st.session_state.questions = load_questions()
                    get_new_question()
            else:
                st.session_state.round += 1
                get_new_question()
                st.experimental_rerun()

else:
    st.write("🎉 Game Over! No more questions left.")
    if st.button("Play Again"):
        st.session_state.score = 0
        st.session_state.round = 1
        st.session_state.streak = 0
        st.session_state.questions = load_questions()
        get_new_question()
        st.experimental_rerun()
