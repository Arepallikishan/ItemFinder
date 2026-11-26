
import streamlit as st
import bcrypt
from db_connection import get_connection


# ---------------- PASSWORD FUNCTIONS ----------------

def hash_password(password):
    """Convert password into a secure bcrypt hash."""
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password must not exceed 72 bytes.")

    hashed = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(rounds=12)
    )

    return hashed.decode("utf-8")


def verify_password(password, stored_password):
    """Verify entered password against stored hash."""
    if isinstance(stored_password, bytes):
        stored_password = stored_password.decode("utf-8")

    # Check whether the stored value is a bcrypt hash
    if stored_password.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            )
        except ValueError:
            return False

    # Backward compatibility for old plaintext passwords
    if password == stored_password:
        return True

    return False


# ---------------- REGISTER USER ----------------

def register_user():

    st.title("📝 User Registration")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register", use_container_width=True):

        if not name.strip() or not email.strip() or not password:
            st.warning("Please fill all fields")
            return

        try:
            hashed_password = hash_password(password)

            conn = get_connection()
            cursor = conn.cursor()

            # Check existing user
            cursor.execute(
                "SELECT email FROM Users WHERE email = ?",
                (email.strip(),)
            )

            user = cursor.fetchone()

            if user:
                st.error("User already exists")
                return

            # Store HASH instead of raw password
            cursor.execute(
                """
                INSERT INTO Users (username, email, password)
                VALUES (?, ?, ?)
                """,
                (name.strip(), email.strip(), hashed_password)
            )

            conn.commit()

            st.success("Registration successful. Please login.")
            st.session_state.page = "login"

        except Exception as e:
            st.error(f"Registration failed: {e}")

        finally:
            if 'conn' in locals():
                conn.close()


# ---------------- LOGIN USER ----------------

def login_user():

    st.title("🔐 User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        if not email.strip() or not password:
            st.warning("Please enter email and password")
            return

        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Retrieve user using email only
            cursor.execute(
                """
                SELECT username, email, password
                FROM Users
                WHERE email = ?
                """,
                (email.strip(),)
            )

            user = cursor.fetchone()

            if user and verify_password(password, user[2]):

                # Automatically upgrade old plaintext passwords
                stored_password = user[2]

                if isinstance(stored_password, bytes):
                    stored_password = stored_password.decode("utf-8")

                if not stored_password.startswith(
                    ("$2a$", "$2b$", "$2y$")
                ):
                    new_hash = hash_password(password)

                    cursor.execute(
                        """
                        UPDATE Users
                        SET password = ?
                        WHERE email = ?
                        """,
                        (new_hash, user[1])
                    )

                    conn.commit()

                st.session_state.logged_in = True
                st.session_state.username = user[0]
                st.session_state.user_email = user[1]

                st.success("Login successful")
                st.session_state.page = "dashboard"
                st.rerun()

            else:
                st.error("Invalid email or password")

        except Exception as e:
            st.error(f"Login failed: {e}")

        finally:
            if conn:
                conn.close()
