import streamlit as st
from db_connection import get_connection


# ---------------- REGISTER USER ----------------

def register_user():

    st.title("📝 User Registration")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register", use_container_width=True):

        if name == "" or email == "" or password == "":
            st.warning("Please fill all fields")
            return

        conn = get_connection()
        cursor = conn.cursor()

        # check existing user
        cursor.execute("SELECT * FROM Users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            st.error("User already exists")
            return

        cursor.execute(
            "INSERT INTO Users (username,email,password) VALUES (?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        st.success("Registration successful. Please login.")

        st.session_state.page = "login"


# ---------------- LOGIN USER ----------------

def login_user():

    st.title("🔐 User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT username,email FROM Users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            st.session_state.logged_in = True
            st.session_state.username = user[0]
            st.session_state.user_email = user[1]

            st.success("Login successful")

            st.session_state.page = "dashboard"
            st.rerun()

        else:
            st.error("Invalid email or password")