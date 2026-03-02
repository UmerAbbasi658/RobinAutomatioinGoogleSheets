import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_credentials():
    service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
    return service_account.Credentials.from_service_account_info(
        service_account_info, scopes=SCOPES
    )

def get_sheets_service():
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)

def get_drive_service():
    creds = get_credentials()
    return build("drive", "v3", credentials=creds)

def get_pending_rows(spreadsheet_id, range_name):
    service = get_sheets_service()
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get("values", [])
    pending = []

    for i, row in enumerate(values[1:], start=2):
        status = row[1].lower() if len(row) > 1 else ""

        if status != "done":
            pending.append({
                "row_number": i,
                "page_id": row[0]
            })

    return pending

def mark_row_done(spreadsheet_id, row_number):
    service = get_sheets_service()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"Sheet1!B{row_number}",
        valueInputOption="RAW",
        body={"values": [["Done"]]}
    ).execute()

def upload_json_to_drive(file_path, file_name, folder_id):
    drive_service = get_drive_service()
    file_metadata = {
        "name": file_name,
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype="application/json")
    drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()