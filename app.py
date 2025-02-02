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
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

    # Print first 200 characters of decoded JSON for debugging
    st.write("✅ Successfully loaded and decoded credentials.")
    st.write(creds_json[:200])  # Print the first 200 characters

except Exception as e:
    st.error(f"❌ Error decoding credentials: {e}")
