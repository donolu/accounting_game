import streamlit as st
import json

try:
    creds_str = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
    st.write("✅ Successfully loaded secrets.")
    st.write("First 200 characters of credentials:", creds_str[:200])
except KeyError:
    st.error("❌ GOOGLE_SHEETS_CREDENTIALS not found in secrets.")
except json.JSONDecodeError as e:
    st.error(f"❌ JSON Parsing Error: {e}")
