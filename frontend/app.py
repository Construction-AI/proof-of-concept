import streamlit as st
from streamlit_cookies_controller.cookie_controller import CookieController
from src.api.client import APIClient
from typing import cast

controller = CookieController()

def main():
    st.set_page_config(page_title="Document RAG Portal", layout="wide")

    # 1. Initialize State Keys Safely
    if "token" not in st.session_state:
        st.session_state.token = cast(str | None, controller.get('auth_token'))
    if "user" not in st.session_state:
        st.session_state.user = None

    # 2. Instantiate Client
    api = APIClient(token=st.session_state.token)

    # 3. Fetch User Profile if we have a token but no user data
    if st.session_state.token and st.session_state.user is None:
        res = api.get_me()
        if res.status_code == 200:
            st.session_state.user = res.json()
        else:
            # Token is invalid or expired. Clear everything.
            st.session_state.token = None
            st.session_state.user = None
            controller.remove('auth_token')
            st.rerun()

    # 4. Authentication Gate
    if not st.session_state.token:
        show_login_page(api)
    else:
        show_dashboard(api)

def show_login_page(api: APIClient):
    st.title("🔐 Welcome")
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login"):
            u = st.text_input("Email")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In"):
                res = api.login(u, p)
                if res.status_code == 200:
                    token = res.json()["access_token"]
                    st.session_state.token = token
                    controller.set('auth_token', token) # type: ignore
                    # We don't need to fetch the user here; a rerun will trigger it in main()
                    st.rerun()
                else:
                    st.error("Invalid credentials")
                    
    with tab2:
        # Added the missing register form!
        with st.form("register"):
            email = st.text_input("Email")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Register"):
                # Make sure you have a register method in your APIClient!
                res = api.register(email, password, first_name, last_name)
                if res.status_code == 201:
                    st.success("Account created! Please switch to the Login tab.")
                else:
                    st.error("Registration failed.")

def show_dashboard(api: APIClient):
    # --- Sidebar Navigation Helpers ---
    with st.sidebar:
        st.title("Settings")
        if st.session_state.user:
            st.write(f"Logged in: **{st.session_state.user['first_name']}**")
        
        if st.button("Log Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None # Clear the user on logout
            controller.remove('auth_token')
            st.rerun()

    # --- Main Dashboard Navigation Hub ---
    st.title("🏠 Document AI Dashboard")
    st.info("Welcome back! Select a module below or use the sidebar to navigate.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📂 Projects")
        st.write("Manage your document collections and project settings.")
        if st.button("Go to Projects", key="nav_projects", use_container_width=True):
            st.switch_page("pages/projects.py")

    # with col2:
    #     st.subheader("📄 Documents")
    #     st.write("Upload new PDF or Text files to your vector store.")
    #     if st.button("Go to Documents", key="nav_docs", use_container_width=True):
    #         st.switch_page("pages/2_Documents.py")

    with col3:
        st.subheader("🤖 AI Chat")
        st.write("Query your documents using RAG and confidence scores.")
        if st.button("Go to Chat", key="nav_rag", use_container_width=True):
            st.switch_page("pages/rag.py")

    st.divider()
    
    # Optional: Quick Stats or Recent Activity
    st.write("### System Status")
    
    # Make sure your APIClient has this method mapped to /api/v1/health/
    try:
        health_res = api.get_health()
        if health_res.status_code == 200:
            st.success("API: Connected")
        else:
            st.error("API: Offline")
    except Exception:
        st.error("API: Offline or Unreachable")
        
main()