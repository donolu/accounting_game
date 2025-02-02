import base64
import json
import os
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials


def fix_base64_padding(b64_string):
    """Fix Base64 padding issues by adding missing `=` characters."""
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)
    return b64_string


def load_credentials():
    """Load Google Sheets credentials from secrets (Base64-encoded) or a local file."""
    try:
        # ✅ Running on `streamlit.app`
        if "GOOGLE_SHEETS_CREDENTIALS_B64" in st.secrets:
            creds_b64 = st.secrets["GOOGLE_SHEETS_CREDENTIALS_B64"]
            creds_b64 = fix_base64_padding(creds_b64)  # Fix padding
            creds_json = base64.b64decode(creds_b64).decode(
                "utf-8"
            )  # Decode Base64 to JSON
            creds_dict = json.loads(creds_json)  # Convert to Python dictionary

            # ✅ Fix private key formatting
            if "private_key" in creds_dict:
                creds_dict["private_key"] = creds_dict["private_key"].replace(
                    "\\n", "\n"
                )

            return Credentials.from_service_account_info(
                creds_dict,
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )

        # ✅ Running Locally (Only if `streamlit-sheets-key.json` Exists)
        elif os.path.exists("streamlit-sheets-key.json"):
            return Credentials.from_service_account_file(
                "streamlit-sheets-key.json",
                scopes=[
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )

        else:
            st.error(
                "❌ No Google Sheets credentials found. Ensure `GOOGLE_SHEETS_CREDENTIALS_B64` is set in Streamlit Secrets."
            )
            return None

    except json.JSONDecodeError as e:
        st.error(f"❌ JSON Parsing Error: {e}")
        return None
    except base64.binascii.Error as e:
        st.error(f"❌ Base64 Decoding Error: {e}")
        return None


def connect_to_gsheets():
    """Establish connection to Google Sheets using loaded credentials."""
    creds = load_credentials()  # Load credentials using the updated function
    if creds is None:
        st.error("❌ Failed to authenticate Google Sheets.")
        return None

    client = gspread.authorize(creds)

    try:
        sheet = client.open(
            "StudentScores"
        ).sheet1  # Ensure this matches your Google Sheet name
        st.write("✅ Successfully connected to Google Sheets!")
        return sheet
    except Exception as e:
        st.error(f"⚠️ Error connecting to Google Sheets: {e}")
        return None


sheet = connect_to_gsheets()
if sheet:
    st.write("✅ Google Sheets is ready to use!")
