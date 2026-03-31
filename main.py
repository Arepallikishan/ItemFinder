import streamlit as st
from auth import login_user, register_user
from report_missing import report_missing_item
from report_found import report_found_item
from admin_dashboard import admin_dashboard

st.set_page_config(page_title="Lost & Found AI", layout="centered")

# ---------- SESSION INITIALIZATION ----------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "home"


# ---------- HOME PAGE ----------

def home_page():

    st.title("🔎 Lost & Found AI")
    st.caption("AI powered system to reconnect lost items with their owners")

    st.divider()

    st.subheader("Welcome")

    st.write(
        "This platform helps people report missing items and allows others "
        "to upload found items. Our AI compares images and identifies possible matches."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔐 Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

    with col2:
        if st.button("📝 Register", use_container_width=True):
            st.session_state.page = "register"
            st.rerun()

    st.write("")

    if st.button("📦 Report Found Item", use_container_width=True):
        st.session_state.page = "report_found"
        st.rerun()


# ---------- USER DASHBOARD ----------

def user_dashboard():

    st.title("📊 User Dashboard")

    st.write(f"Welcome **{st.session_state.username}** 👋")

    st.divider()

    menu = st.sidebar.selectbox(
        "Menu",
        ["Report Missing Item", "Report Found Item"]
    )

    if menu == "Report Missing Item":
        report_missing_item()

    elif menu == "Report Found Item":
        report_found_item()

    st.write("")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.session_state.page = "home"
        st.rerun()
def back_button():

    if st.button("⬅ Back"):
        st.session_state.page = "home"
        st.rerun()
def logout_button():

    if st.button("🚪 Logout"):
        st.session_state.page = "home"
        st.rerun()


# ---------- MAIN ROUTER ----------

if st.session_state.page == "home":
    home_page()

elif st.session_state.page == "login":
    login_user()
    back_button()

elif st.session_state.page == "register":
    register_user()
    back_button()

elif st.session_state.page == "report_found":
    report_found_item()
    back_button()

elif st.session_state.page == "report_missing":
    report_missing_item()
    back_button()

elif st.session_state.logged_in:

    # ADMIN LOGIN
    if st.session_state.user_email == "arepallikishan06@gmail.com":
        admin_dashboard()
        logout_button()

    # NORMAL USER
    else:
        user_dashboard()
