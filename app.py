import streamlit as st
import base64
import json

try:
    # Decode Base64 from Secrets
    creds_b64 = st.secrets["GOOGLE_SHEETS_CREDENTIALS_B64"]
    creds_json = base64.b64decode(creds_b64).decode()
    creds_dict = json.loads(creds_json)

    # Print first 200 characters of decoded JSON for debugging
    st.write("✅ Successfully loaded and decoded credentials.")
    st.write(creds_json[:200])  # Print the first 200 characters

except Exception as e:
    st.error(f"❌ Error decoding credentials: {e}")
