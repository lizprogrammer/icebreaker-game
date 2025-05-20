import streamlit as st
import uuid
from supabase import create_client, Client

# ✅ Set page config FIRST before any other Streamlit commands
st.set_page_config(page_title="Icebreaker Game", layout="centered")

# Load Supabase credentials
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ------------------ Player View ------------------
def player_view():
    st.title("🎉 Break the Ice & Win!")
    username = st.text_input("Enter your name to join the game:")

    if username:
        if "user_id" not in st.session_state:
            user_id = str(uuid.uuid4())
            st.session_state["user_id"] = user_id
            st.session_state["username"] = username
            supabase.table("players").insert({
                "id": user_id,
                "name": username,
                "score": 0
            }).execute()
            st.success(f"Welcome, {username}! Get ready to play.")
        else:
            user_id = st.session_state["user_id"]
            username = st.session_state["username"]

        question_data = supabase.table("game").select("*").eq("id", "current_question").execute().data
        if question_data:
            question = question_data[0]["question"]
            correct_answer = question_data[0].get("correct_answer", "").lower().strip()
            st.subheader(question)
            answer = st.text_input("Your answer:")

            if st.button("Submit Answer"):
                answer_clean = answer.lower().strip()
                is_correct = answer_clean == correct_answer

                # Save the answer
                supabase.table("answers").insert({
                    "user_id": user_id,
                    "username": username,
                    "answer": answer,
                    "question_id": "current_question",
                    "is_correct": is_correct
                }).execute()

                if is_correct:
                    # Increment score
                    player = supabase.table("players").select("score").eq("id", user_id).execute().data[0]
                    new_score = player["score"] + 1
                    supabase.table("players").update({"score": new_score}).eq("id", user_id).execute()
                    st.success("Correct! You earned a point 🎉")
                else:
                    st.warning("Oops! That's not quite right.")
        else:
            st.info("Waiting for the host to start the game...")

# ------------------ Admin View ------------------
def admin_view():
    st.title("🛠 Host Control Panel")
    question = st.text_input("Enter a new question:")
    correct_answer = st.text_input("Enter the correct answer:")

    if st.button("Push Question"):
        if question and correct_answer:
            supabase.table("game").upsert({
                "id": "current_question",
                "question": question,
                "correct_answer": correct_answer.lower().strip()
            }).execute()
            st.success("Question and answer pushed to players!")
        else:
            st.error("Please enter both a question and a correct answer.")

# ------------------ Leaderboard View ------------------
def leaderboard_view():
    st.title("🏆 Leaderboard")
    players_data = supabase.table("players").select("*").execute().data
    leaderboard = sorted([(p["name"], p["score"]) for p in players_data], key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(leaderboard):
        st.write(f"{i+1}. {name} - {score} points")

# ------------------ Navigation ------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Player View", "Admin View", "Leaderboard"])

if page == "Player View":
    player_view()
elif page == "Admin View":
    admin_view()
elif page == "Leaderboard":
    leaderboard_view()
