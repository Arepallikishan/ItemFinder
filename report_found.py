import streamlit as st
import os
from db_connection import get_connection
from datetime import datetime
from module4_auto_match import auto_match_engine


def report_found_item():

    st.title("📦 Report Found Item")

    st.caption("Upload a clear front-view image of the item")

    st.divider()

    # -------- FORM INPUT --------

    item_name = st.text_input("Item Name")

    category = st.text_input("Category")

    desc = st.text_input("Description")

    color = st.text_input("Color")

    location = st.text_input("Location Found")

    finder_email = st.text_input("Your Email (for contact)")

    image = st.file_uploader(
        "Upload Item Image (Front View Preferred)",
        type=["jpg", "jpeg", "png"]
    )

    # -------- SUBMIT BUTTON --------

    if st.button("Submit Found Item", use_container_width=True):

        if not item_name or not category or not color or not location or not finder_email or image is None:
            st.warning("Please fill all fields and upload image")
            return

        # -------- SAVE IMAGE --------

        upload_folder = "uploads/found"

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        image_path = os.path.join(upload_folder, image.name)

        with open(image_path, "wb") as f:
            f.write(image.getbuffer())

        # -------- INSERT INTO DATABASE --------

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO Found_Items
            (item_name, category, description, color, location_found, image_path, finder_email, status, date_found)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)
            """,
            (
                item_name,
                category,
                desc,
                color,
                location,
                image_path,
                finder_email,
                "Found",
                datetime.now()
            )
        )

        conn.commit()
        conn.close()
        st.success("Item reported successfully!")
    # Trigger AI matching
    auto_match_engine()

