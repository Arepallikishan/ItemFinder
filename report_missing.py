import streamlit as st
import os
from db_connection import get_connection
from datetime import datetime
from module4_auto_match import auto_match_engine



def report_missing_item():

    # Check login
    if not st.session_state.get("logged_in"):
        st.warning("Please login to report a missing item.")
        return

    st.title("📉 Report Missing Item")

    st.caption("Provide details about your lost item")

    st.divider()

    # Logged in user email
    owner_email = st.session_state.user_email

    st.write(f"Logged in as: **{owner_email}**")

    # ---------- FORM INPUT ----------

    item_name = st.text_input("Item Name")

    category = st.text_input("Category")

    desc =  st.text_input("Description")

    color = st.text_input("Color")

    location = st.text_input("Location Lost")

    image = st.file_uploader(
        "Upload Item Image",
        type=["jpg", "jpeg", "png"]
    )

    # ---------- SUBMIT ----------

    if st.button("Submit Missing Item", use_container_width=True):

        if not item_name or not category or not color or not location or image is None:
            st.warning("Please fill all fields and upload image")
            return

        # ---------- SAVE IMAGE ----------

        upload_folder = "uploads/missing"

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        image_path = os.path.join(upload_folder, image.name)

        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

        # ---------- INSERT DATABASE ----------

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Missing_Items
            (item_name, category, description, color, location_lost, image_path, owner_email, status, date_reported)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
            """,
            (
                item_name,
                category,
                desc,
                color,
                location,
                image_path,
                owner_email,
                "Missing",
                datetime.now()
            )
        )

        conn.commit()
        conn.close()

        st.success("Missing item reported successfully!")
        auto_match_engine()

        st.balloons()

    st.divider()

    # ---------- SHOW USER ITEMS ----------

    st.subheader("Your Reported Missing Items")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT item_name, category, color, location_lost, status
        FROM Missing_Items
        WHERE owner_email = ? AND status = 'Missing'
        """,
        (owner_email,)
    )

    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            st.write(
                f"Item: {row[0]} | Category: {row[1]} | Color: {row[2]} | Location: {row[3]} | Status: {row[4]}"
            )
    else:
        st.info("No missing items reported yet.")
    st.subheader("The Items We Found that you Lost")
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT item_name, category, color, location_lost, status
        FROM Missing_Items
        WHERE owner_email = ? AND status = 'Resolved'
        """,
        (owner_email,)
    )

    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            st.write(
                f"Item: {row[0]} | Category: {row[1]} | Color: {row[2]} | Location: {row[3]} | Status: {row[4]}"
            )
    else:
        st.info("Nothing has been Found Yet.")