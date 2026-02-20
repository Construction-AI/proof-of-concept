import streamlit as st
from src.api.client import APIClient

if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please log in on the Home page.")
    st.stop()

api = APIClient(token=st.session_state.token)

st.title("📂 Project Management")

# Fetch projects using the client
res = api.get_projects()
if res.status_code == 200:
    projects = res.json()
    for p in projects:
        with st.expander(p['title']):
            st.write(p['description']) # type: ignore
            st.caption(f"Created: {p['created_at']}")