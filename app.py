import streamlit as st
import base64
import json


def fix_base64_padding(b64_string):
    """Fix Base64 padding issues by adding missing `=` characters."""
    missing_padding = len(b64_string) % 4
    if missing_padding:
        b64_string += "=" * (4 - missing_padding)
    return b64_string


try:
    # Decode Base64 from Secrets
    creds_b64 = st.secrets["GOOGLE_SHEETS_CREDENTIALS_B64"]
    creds_b64 = fix_base64_padding(creds_b64)  # Fix padding
    creds_json = base64.b64decode(creds_b64).decode("utf-8")  # Decode Base64 to JSON
    creds_dict = json.loads(creds_json)  # Convert to Python dictionary

    # ✅ Fix private key formatting (convert "\\n" to actual newlines)
    if "private_key" in creds_dict:
        creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Debugging: Print the first 200 characters
    st.write("✅ Successfully loaded and fixed credentials.")
    st.write("First 200 characters of fixed JSON:", json.dumps(creds_dict)[:200])

except json.JSONDecodeError as e:
    st.error(f"❌ JSON Parsing Error: {e}")
except base64.binascii.Error as e:
    st.error(f"❌ Base64 Decoding Error: {e}")
except Exception as e:
    st.error(f"❌ Other Error: {e}")
