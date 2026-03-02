import os
import json
from offorte_client import OfforteAutomation
from google_service import (
    get_pending_rows,
    mark_row_done,
    upload_json_to_drive
)

PROPOSAL_ID = "344878"
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

def main():
    pending_rows = get_pending_rows(SPREADSHEET_ID, "Sheet1!A:B")

    if not pending_rows:
        print("✅ No pending rows found.")
        return

    for row in pending_rows:
        page_id = row["page_id"]
        row_number = row["row_number"]

        print(f"🚀 Processing Page: {page_id}")

        try:
            automation = OfforteAutomation(PROPOSAL_ID, page_id)
            proposal_data = automation.run()

            file_name = f"{page_id}.json"
            file_path = f"./{file_name}"

            with open(file_path, "w") as f:
                json.dump(proposal_data, f, indent=4)

            upload_json_to_drive(file_path, file_name, DRIVE_FOLDER_ID)
            mark_row_done(SPREADSHEET_ID, row_number)

            print(f"✅ Completed: {page_id}")

        except Exception as e:
            print(f"❌ Failed for {page_id}: {str(e)}")

if __name__ == "__main__":
    main()