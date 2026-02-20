import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.page_link("app.py", label="Home", icon="🏠")
        st.page_link("pages/projects.py", label="Projects", icon="📂")
        # st.page_link("pages/2_Documents.py", label="Documents", icon="📄")
        st.page_link("pages/rag.py", label="AI Assistant", icon="🤖")
        st.divider()