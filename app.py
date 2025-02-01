import streamlit as st
import json

try:
    creds_str = st.secrets["GOOGLE_SHEETS_CREDENTIALS"]
    st.write("✅ Successfully loaded secrets.")
    st.write("First 1000 characters of credentials:", creds_str[:1000])
except Exception as e:
    st.error(f"❌ Error loading secrets: {e}")
