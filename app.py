import streamlit as st
import json
import random
import time


# Load questions from JSON file
@st.cache_data
def load_questions():
    with open("questions.json", "r") as file:
        return json.load(file)


# Initialize session state
if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.current_question = None
    st.session_state.round = 1
    st.session_state.streak = 0
    st.session_state.questions = load_questions()


# Function to get a new question
def get_new_question():
    if st.session_state.questions:
        st.session_state.current_question = random.choice(st.session_state.questions)
        st.session_state.questions.remove(st.session_state.current_question)
    else:
        st.session_state.current_question = None


# Initialize the first question
if st.session_state.current_question is None:
    get_new_question()

# UI Layout
st.title("💰 Debit or Credit Challenge")

# Show round and score
st.write(
    f"**Round:** {st.session_state.round}/10 | **Score:** {st.session_state.score} | **Streak:** {st.session_state.streak}"
)

# Show question
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

            # Move to next round
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
                st.rerun()

else:
    st.write("🎉 Game Over! No more questions left.")
    if st.button("Play Again"):
        st.session_state.score = 0
        st.session_state.round = 1
        st.session_state.streak = 0
        st.session_state.questions = load_questions()
        get_new_question()
        st.rerun()
