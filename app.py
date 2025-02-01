import streamlit as st
import json

try:
    creds_str = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
    st.write("✅ Successfully loaded secrets.")
    st.write("First 400 characters of credentials:", creds_str[:400])
except Exception as e:
    st.error(f"❌ Error loading secrets: {e}")
