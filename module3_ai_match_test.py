from db_connection import get_connection
from module1_image_match import compare_images
import os

SIMILARITY_THRESHOLD = 85  # Percentage


def get_latest_found_item():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT TOP 1 found_id, category, color, location_found, image_path,finder_email
        FROM Found_Items where status = 'found'
        ORDER BY found_id DESC
    """)

    found = cursor.fetchone()
    conn.close()
    return found


def get_filtered_missing_items(found_category, found_color):
    conn = get_connection()
    cursor = conn.cursor()

    # Step 1: Fetch all missing items
    cursor.execute("""
        SELECT missing_id, item_name, category, color, image_path, owner_email
        FROM Missing_Items
        WHERE status = 'Missing'
    """)

    all_missing_items = cursor.fetchall()
    conn.close()

    filtered_items = []

    # Normalize found item details
    found_category_norm = str(found_category).strip().lower()
    found_color_norm = str(found_color).strip().lower()

    for item in all_missing_items:
        missing_id, item_name, db_category, db_color, image_path, owner_email = item

        # Normalize DB values
        db_category_norm = str(db_category).strip().lower()
        db_color_norm = str(db_color).strip().lower()

        # 🔥 SMART MATCH CONDITIONS
        category_match = (
            found_category_norm in db_category_norm
            or db_category_norm in found_category_norm
        )

        color_match = (
            found_color_norm in db_color_norm
            or db_color_norm in found_color_norm
        )

        # Smart filtering (category must match, color optional but recommended)
        if category_match and color_match:
             filtered_items.append(
                (missing_id, item_name, image_path, owner_email)
            )
    return filtered_items

#not used
def ai_compare_with_filtered_items():
    found_item = get_latest_found_item()
    print(found_item)
    if not found_item:
        print("No found items available.")
        return

    found_id, category, color, location, found_image,mail = found_item

    print(f"\nLatest Found Item ID: {found_id}")
    print(f"Category: {category}, Color: {color}, Location: {location}")
    print(f"Found Image Path: {found_image}")
    print("mail is :",mail)

    # Check if image exists
    if not os.path.exists(found_image):
        print("Found image file not found in folder!")
        return

    missing_items = get_filtered_missing_items(category, color)

    if not missing_items:
        print("No filtered missing items found.")
        return

    print(f"\nComparing with {len(missing_items)} filtered missing item(s)...\n")

    for missing_id, missing_image in missing_items:
        # Check missing image exists
        if not os.path.exists(missing_image):
            print(f"Missing image not found: {missing_image}")
            continue

        # Compare images using AI model
        similarity = compare_images(found_image, missing_image)

        print(f"Missing Item ID: {missing_id}")
        print(f"Similarity: {similarity:.2f}%")

        # Decide match status based on threshold
        if similarity >= SIMILARITY_THRESHOLD:
            match_status = "Matched"
            print(">>> HIGH MATCH FOUND (Above Threshold)")
        else:
            match_status = "Not Matched"
            print(">>> Low similarity")

        # 🔹 INSERT RESULT INTO MATCH TABLE
        insert_match_into_table(
        missing_id=missing_id,
        found_id=found_id,
        similarity=similarity,
        match_status=match_status
        )

        print("-" * 50)
#not used
def insert_match_into_table(missing_id, found_id, similarity, match_status):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Check if this match already exists (avoid duplicates)
        cursor.execute("""
            SELECT COUNT(*) FROM MatchTable
            WHERE missing_id = ? AND found_id = ?
        """, (missing_id, found_id))

        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("""
                INSERT INTO MatchTable 
                (missing_id, found_id, similarity_percentage, match_status, email_sent, matched_date)
                VALUES (?, ?, ?, ?, 0, GETDATE())
            """, (missing_id, found_id, similarity, match_status))

            conn.commit()
            print(f"Inserted into MatchTable -> Missing ID: {missing_id}, Found ID: {found_id}")
        else:
            print(f"Match already exists for Missing ID {missing_id} and Found ID {found_id}")

        conn.close()

    except Exception as e:
        print("Error inserting into MatchTable:", e)


if __name__ == "__main__":
    ai_compare_with_filtered_items()