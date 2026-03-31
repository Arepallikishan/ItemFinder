import streamlit as st
import pandas as pd
from db_connection import get_connection
from module5_email_alert import send_thank_you_email, send_match_email


def admin_dashboard():

    st.title("🛠 Admin Control Panel")
    st.caption("AI Match Verification System")

    conn = get_connection()
    cursor = conn.cursor()

    # ---------- DASHBOARD STATISTICS ----------

    cursor.execute("SELECT COUNT(*) FROM Missing_Items WHERE status='Missing'")
    total_missing = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM Found_Items WHERE status='found'")
    total_found = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM MatchTable WHERE match_status='Matched'")
    pending_matches = cursor.fetchone()[0]

    col1, col2, col3 = st.columns(3)

    col1.metric("Missing Items", total_missing)
    col2.metric("Found Items", total_found)
    col3.metric("Pending Matches", pending_matches)

    st.divider()

    table_viewer(conn, cursor)
    manual_match_section(conn, cursor)

    # ---------- AI MATCHES ----------

    st.subheader("🤖 AI Detected Matches")

    cursor.execute("""
        SELECT 
            m.match_id,
            m.similarity_percentage,
            mi.missing_id,
            mi.item_name,
            mi.image_path,
            mi.owner_email,
            fi.found_id,
            fi.image_path,
            fi.finder_email
        FROM MatchTable m
        JOIN Missing_Items mi ON m.missing_id = mi.missing_id
        JOIN Found_Items fi ON m.found_id = fi.found_id
        WHERE m.match_status = 'Matched'
    """)

    matches = cursor.fetchall()

    if not matches:
        st.info("No pending AI matches available.")
        conn.close()
        return

    for match in matches:

        match_id = match[0]
        similarity = match[1]
        missing_id = match[2]
        item_name = match[3]
        missing_image = match[4]
        owner_email = match[5]
        found_id = match[6]
        found_image = match[7]
        finder_email = match[8]

        st.divider()

        st.write(f"Match ID: {match_id}")
        st.write(f"Item: {item_name}")
        st.write(f"Similarity: {similarity:.2f}%")

        st.progress(int(similarity))

        img1, img2 = st.columns(2)

        img1.image(missing_image, use_column_width=True)
        img2.image(found_image, use_column_width=True)

        btn1, btn2 = st.columns(2)

        with btn1:

            if st.button("Verify Match", key=f"verify_{match_id}"):

                cursor.execute(
                    "UPDATE MatchTable SET match_status='Resolved' WHERE match_id=?",
                    (match_id,)
                )

                cursor.execute(
                    "UPDATE Found_Items SET status='Resolved' WHERE found_id=?",
                    (found_id,)
                )

                cursor.execute(
                    "UPDATE Missing_Items SET status='Resolved' WHERE missing_id=?",
                    (missing_id,)
                )

                conn.commit()

                send_match_email(owner_email, item_name, similarity)
                send_thank_you_email(finder_email)

                st.success("Match Verified")

        with btn2:

            if st.button("Reject Match", key=f"reject_{match_id}"):

                cursor.execute(
                    "DELETE FROM MatchTable WHERE match_id=?",
                    (match_id,)
                )

                conn.commit()

                st.warning("Match Rejected")

    conn.close()
def manual_match_section(conn, cursor):

    st.subheader("🤝 Manual Match Creation")

    # SEARCH INPUTS
    missing_search = st.text_input("Search Missing Item Category")
    found_search = st.text_input("Search Found Item Category")

    missing_df = pd.DataFrame()
    found_df = pd.DataFrame()

    # LOAD ONLY SEARCHED DATA
    if missing_search:

        missing_df = pd.read_sql(
            """
            SELECT missing_id, item_name, category, image_path
            FROM Missing_Items
            WHERE status='Missing'
            AND category LIKE ?
            AND missing_id NOT IN (
                SELECT missing_id FROM MatchTable
            )
            """,
            conn,
            params=[f"%{missing_search}%"]
        )

    if found_search:

        found_df = pd.read_sql(
            """
            SELECT found_id, item_name, category, image_path
            FROM Found_Items
            WHERE status='Found'
            AND category LIKE ?
            AND found_id NOT IN (
                SELECT found_id FROM MatchTable
            )
            """,
            conn,
            params=[f"%{found_search}%"]
        )

    col1, col2 = st.columns(2)

    missing_id = None
    found_id = None


    # -------- MISSING ITEMS --------
    with col1:

        st.markdown("### Missing Item")

        if not missing_df.empty:

            missing_option = st.selectbox(
                "Select Missing Item",
                missing_df["item_name"]
            )

            row = missing_df[
                missing_df["item_name"] == missing_option
            ].iloc[0]

            missing_id = int(row["missing_id"])

            st.image(row["image_path"], width=600)

        elif missing_search:
            st.warning("No Missing Items Found")


    # -------- FOUND ITEMS --------
    with col2:

        st.markdown("### Found Item")

        if not found_df.empty:

            found_option = st.selectbox(
                "Select Found Item",
                found_df["item_name"]
            )

            row = found_df[
                found_df["item_name"] == found_option
            ].iloc[0]

            found_id = int(row["found_id"])

            st.image(row["image_path"], width=600)

        elif found_search:
            st.warning("No Found Items Found")


    # -------- CREATE MATCH --------
    if missing_id and found_id:

        if st.button("Create Manual Match"):

            cursor.execute(
                """
                INSERT INTO MatchTable
                (missing_id, found_id, similarity_percentage, match_status)
                VALUES (?, ?, ?, 'Pending')
                """,
                (missing_id, found_id, 100)
            )
            cursor.execute(
                    "UPDATE Found_Items SET status='Resolved' WHERE found_id=?",
                    (found_id,)
                )

            cursor.execute(
                "UPDATE Missing_Items SET status='Resolved' WHERE missing_id=?",
                (missing_id,)
            )
            cursor.execute("select owner_email,item_name from Missing_Items where missing_id = ?",
                (missing_id,)
            )
            item = cursor.fetchone()
            owner_email = item[0]
            item_name = item[1]

            cursor.execute("select finder_email from Found_Items where found_id = ?",
                (found_id,)
            )
            item = cursor.fetchone()
            finder_email = item[0]

            conn.commit()
            send_match_email(owner_email, item_name,100)
            send_thank_you_email(finder_email)

            st.success("Manual Match Created")

    st.divider()
def table_viewer(conn, cursor):

    # ---------- TABLE VIEWER ----------

    st.subheader("📂 Table Viewer")

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Missing", "Resolved", "Found"]
    )

    if "table_view" not in st.session_state:
        st.session_state.table_view = None

    colA, colB = st.columns(2)

    with colA:
        if st.button("📦 View Missing Items", use_container_width=True):
            st.session_state.table_view = "missing"

    with colB:
        if st.button("🔎 View Found Items", use_container_width=True):
            st.session_state.table_view = "found"


    # ---------- MISSING TABLE ----------

    if st.session_state.table_view == "missing":

        st.subheader("Missing Items Table")

        df = pd.read_sql("SELECT * FROM Missing_Items", conn)

        if status_filter != "All":
            df = df[df["status"] == status_filter]

        st.dataframe(df, use_container_width=True, height=400)

        st.write("Select rows to delete")

        df["Select"] = False

        edited_df = st.data_editor(df, use_container_width=True)

        selected_rows = edited_df[edited_df["Select"] == True]

        if st.button("🗑 Delete Selected Missing Items"):

            for _, row in selected_rows.iterrows():
                cursor.execute(
                    "DELETE FROM Missing_Items WHERE missing_id=?",
                    (row["missing_id"],)
                )

            conn.commit()
            st.success("Selected rows deleted")


    # ---------- FOUND TABLE ----------

    elif st.session_state.table_view == "found":

        st.subheader("Found Items Table")

        df = pd.read_sql("SELECT * FROM Found_Items", conn)

        if status_filter != "All":
            df = df[df["status"] == status_filter]

        st.dataframe(df, use_container_width=True, height=400)

        st.write("Select rows to delete")

        df["Select"] = False

        edited_df = st.data_editor(df, use_container_width=True)

        selected_rows = edited_df[edited_df["Select"] == True]

        if st.button("🗑 Delete Selected Found Items"):

            for _, row in selected_rows.iterrows():
                cursor.execute(
                    "DELETE FROM Found_Items WHERE found_id=?",
                    (row["found_id"],)
                )

            conn.commit()
            st.success("Selected rows deleted")

    st.divider()
    return 