import streamlit as st
import uuid
from supabase import create_client, Client

# Set page config
st.set_page_config(page_title="Icebreaker Game", layout="centered")

# Banner with overlay text
st.markdown("""
    <style>
        .banner-container {
            position: relative;
            text-align: center;
        }
        .banner-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 3vw;  /* Responsive font size */
            font-weight: bold;
            text-shadow: 2px 2px 4px #000;
        }
    </style>
    <div class="banner-container">
        <img src="https://res.cloudinary.com/startup-grind/image/upload/c_scale,w_2560/c_crop,h_640,w_2560,y_0.0_mul_h_sub_0.0_mul_640/c_crop,h_640,w_2560/c_fill,dpr_2.0,f_auto,g_center,q_auto:good/v1/gcs/platform-data-snowflake/event_banners/User%20Groups%20Filler%20Banner_yAwMUPz.png" style="width: 100%;">
        <div class="banner-text">Boston Snowflake User Group</div>
    </div>
""", unsafe_allow_html=True)

# Load Supabase credentials
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ------------------ Player View ------------------
def player_view():
    st.title("❄️ Break the Ice & Win!")
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

        # Fetch all available questions
        question_data = supabase.table("game").select("*").execute().data

        if question_data:
            # Track progress through session state
            if "question_index" not in st.session_state:
                st.session_state["question_index"] = 0

            current_question = question_data[st.session_state["question_index"]]
            st.subheader(current_question["question"])
            correct_answer = current_question.get("correct_answer", "").lower().strip()
            answer = st.text_input("Your answer:")

            if st.button("Submit Answer"):
                answer_clean = answer.lower().strip()
                is_correct = answer_clean == correct_answer

                # Save the answer
                supabase.table("answers").insert({
                    "user_id": user_id,
                    "username": username,
                    "answer": answer,
                    "question_id": current_question["id"],
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

                # Move to the next question
                if st.session_state["question_index"] < len(question_data) - 1:
                    st.session_state["question_index"] += 1
                else:
                    st.success("You've answered all available questions. Great job! 🎉")

# ------------------ Admin View ------------------
def admin_view():
    st.title("🛠 Host Control Panel")
    question = st.text_input("Enter a new question:")
    correct_answer = st.text_input("Enter the correct answer:")

    if st.button("Push Question"):
        if question and correct_answer:
            supabase.table("game").insert({
                "id": str(uuid.uuid4()),  # Generate unique question IDs
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

# Password-protected admin view
if "admin_authenticated" not in st.session_state:
    st.session_state["admin_authenticated"] = False

if not st.session_state["admin_authenticated"]:
    password_input = st.sidebar.text_input("Enter admin password to unlock admin view:", type="password")
    if password_input == "password":
        st.session_state["admin_authenticated"] = True
        st.sidebar.success("Admin view unlocked!")

pages = ["Player View", "Leaderboard"]
if st.session_state["admin_authenticated"]:
    pages.insert(1, "Admin View")

page = st.sidebar.radio("Go to", pages)

if page == "Player View":
    player_view()
elif page == "Admin View":
    admin_view()
elif page == "Leaderboard":
    leaderboard_view()
