import streamlit as st
import uuid
from supabase import create_client, Client

# Load Supabase credentials from secrets
url = st.secrets["https://cmdneldiaexqzyztcsch.supabase.co"]
key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtZG5lbGRpYWV4cXp5enRjc2NoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc3NjEwNDMsImV4cCI6MjA2MzMzNzA0M30.rOTFpXMCp1c-nuyXw0k15S5xUP3eKvR_Exw0k14LkpM"]
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Icebreaker Game", layout="centered")

def player_view():
    st.title("🎉 Break the Ice & Win!")
    username = st.text_input("Enter your name to join the game:")

    if username:
        user_id = str(uuid.uuid4())
        st.session_state["user_id"] = user_id
        st.session_state["username"] = username
        supabase.table("players").insert({"id": user_id, "name": username, "score": 0}).execute()
        st.success(f"Welcome, {username}! Get ready to play.")

        question_data = supabase.table("game").select("*").eq("id", "current_question").execute().data
        if question_data:
            question = question_data[0]["question"]
            st.subheader(question)
            answer = st.text_input("Your answer:")

            if st.button("Submit Answer"):
                supabase.table("answers").insert({
                    "user_id": user_id,
                    "username": username,
                    "answer": answer,
                    "question_id": "current_question"
                }).execute()
                st.success("Answer submitted!")
        else:
            st.info("Waiting for the host to start the game...")

def admin_view():
    st.title("🛠 Host Control Panel")
    question = st.text_input("Enter a new question:")
    if st.button("Push Question"):
        supabase.table("game").upsert({"id": "current_question", "question": question}).execute()
        st.success("Question pushed to players!")

def leaderboard_view():
    st.title("🏆 Leaderboard")
    players_data = supabase.table("players").select("*").execute().data
    leaderboard = sorted([(p["name"], p["score"]) for p in players_data], key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(leaderboard):
        st.write(f"{i+1}. {name} - {score} points")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Player View", "Admin View", "Leaderboard"])

if page == "Player View":
    player_view()
elif page == "Admin View":
    admin_view()
elif page == "Leaderboard":
    leaderboard_view()
