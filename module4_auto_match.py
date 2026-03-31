import os
from db_connection import get_connection
from module1_image_match import compare_images
from module3_ai_match_test import (
    get_latest_found_item,
    get_filtered_missing_items
)

SIMILARITY_THRESHOLD = 85


def auto_match_engine():

    found_item = get_latest_found_item()

    if not found_item:
        return

    found_id, category, color, location, found_image, finder_email = found_item

    if not os.path.exists(found_image):
        return

    missing_items = get_filtered_missing_items(category, color)

    if not missing_items:
        return

    conn = get_connection()
    cursor = conn.cursor()

    for missing_id, item_name, missing_image, owner_email in missing_items:

        if os.path.isdir(missing_image):
            continue

        if not os.path.exists(missing_image):
            continue

        similarity = compare_images(found_image, missing_image)

        if similarity >= SIMILARITY_THRESHOLD:

            cursor.execute(
                """
                INSERT INTO MatchTable
                (missing_id, found_id, similarity_percentage, match_status, matched_date)
                VALUES (?,?, ?, ?, GETDATE())
                """,
                (
                    missing_id,
                    found_id,
                    similarity,
                    "Matched"
                )
            )
            cursor.execute(
                """
                UPDATE Found_Items
                SET status = 'pending'
                WHERE found_id = ?
                """,
                (found_id,)
            )
            cursor.execute(
                """
                UPDATE Missing_Items
                SET status = 'pending'
                WHERE missing_id = ?
                """,
                (missing_id,)
            )
            

    conn.commit()
    conn.close()