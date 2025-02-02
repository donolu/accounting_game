import streamlit as st
import json

try:
    creds_str = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
    creds_dict = json.loads(creds_str)  # Ensure JSON parsing works
    st.write("✅ Successfully loaded Google credentials from Secrets.")
    st.json(creds_dict)  # Print the full parsed JSON for debugging
except KeyError:
    st.error("❌ GOOGLE_SHEETS_CREDENTIALS not found in secrets.")
except json.JSONDecodeError as e:
    st.error(f"❌ JSON Parsing Error: {e}")
