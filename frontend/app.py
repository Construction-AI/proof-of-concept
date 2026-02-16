import streamlit as st
import pandas as pd
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="Project Dashboard", layout="wide")

# The internal docker DNS name provided in your prompt
API_BASE_URL = "http://llamaindex-service:8000/api/v1/db"

# --- API CLIENT FUNCTIONS ---
# We use 'params' for POST requests because your FastAPI endpoints 
# are defined with query parameters, not Pydantic bodies.

def api_create_user(first, last, email):
    try:
        resp = requests.post(f"{API_BASE_URL}/create_user", 
                             params={"first_name": first, "last_name": last, "email": email})
        return resp.status_code == 201
    except: return False

def api_get_users():
    try:
        resp = requests.get(f"{API_BASE_URL}/read_all_users")
        return resp.json() if resp.status_code == 200 else []
    except: return []

def api_get_user(user_id):
    try:
        resp = requests.get(f"{API_BASE_URL}/read_user/{user_id}")
        return resp.json() if resp.status_code == 200 else None
    except: return None

def api_create_project(name, user_id):
    try:
        resp = requests.post(f"{API_BASE_URL}/create_project", 
                             params={"project_name": name, "user_id": user_id})
        return resp.status_code == 201
    except: return False

def api_get_projects():
    try:
        resp = requests.get(f"{API_BASE_URL}/read_all_projects")
        return resp.json() if resp.status_code == 200 else []
    except: return []

def api_create_document(user_id, project_id, title, file_obj=None):
    try:
        # Query parameters (metadata)
        params = {
            "user_id": user_id, 
            "project_id": project_id, 
            "document_title": title
        }
        
        # File payload (if a file was uploaded)
        files = None
        if file_obj is not None:
            # The key 'file' must match the parameter name in your FastAPI backend
            files = {"file": (file_obj.name, file_obj, file_obj.type)}

        # We send params in the URL query string, and files in the multipart body
        resp = requests.post(
            f"{API_BASE_URL}/create_document", 
            params=params,
            files=files
        )
        return resp.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def api_get_doc(doc_id):
    try:
        resp = requests.get(f"{API_BASE_URL}/read_document/{doc_id}")
        return resp.json() if resp.status_code == 200 else None
    except: return None

def api_get_project_docs(project_id):
    # This calls the NEW endpoint added above
    try:
        resp = requests.get(f"{API_BASE_URL}/read_documents_by_project/{project_id}")
        return resp.json() if resp.status_code == 200 else []
    except: return []

# --- HELPER ---
def get_user_name_map():
    users = api_get_users()
    # Returns a dict: {"John Doe": 1, "Jane Smith": 2}
    return {f"{u['first_name']} {u['last_name']}": u['id'] for u in users}

# --- STATE MANAGEMENT ---
if 'active_project_id' not in st.session_state:
    st.session_state['active_project_id'] = None

# --- UI PAGES ---

def page_users():
    st.header("👥 User Management")
    tab1, tab2, tab3 = st.tabs(["Create User", "Find User", "All Users"])
    
    # 1a.1 Create
    with tab1:
        with st.form("new_user"):
            c1, c2 = st.columns(2)
            first = c1.text_input("First Name")
            last = c2.text_input("Last Name")
            email = st.text_input("Email")
            if st.form_submit_button("Create"):
                if api_create_user(first, last, email):
                    st.success("User created!")
                else:
                    st.error("Failed to create user.")

    # 1a.2 Read Single
    with tab2:
        uid = st.number_input("User ID", min_value=1, step=1)
        if st.button("Search User"):
            user = api_get_user(uid)
            if user:
                st.json(user)
            else:
                st.error("User not found")

    # 1a.3 Read All
    with tab3:
        users = api_get_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
        else:
            st.info("No users found.")

def page_specific_project(project_id):
    # Fetch project details
    all_projs = api_get_projects()
    project = next((p for p in all_projs if p['id'] == project_id), None)

    if not project:
        st.error("Project not found.")
        if st.button("Back"):
            st.session_state['active_project_id'] = None
            st.rerun()
        return

    col1, col2 = st.columns([1, 6])
    with col1:
        if st.button("← Back"):
            st.session_state['active_project_id'] = None
            st.rerun()
    with col2:
        # Note: Ensure your API returns 'name' or 'project_name' consistently. 
        # Your last snippet used 'name', previous used 'project_name'.
        p_name = project.get('name', project.get('project_name', 'Unnamed Project'))
        st.title(f"📂 {p_name}")
        st.caption(f"Project ID: {project['id']} | User ID: {project['user_id']}")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["Add Document", "Read Document", "Project Documents"])

    # --- 1b.4.1 Add Document (UPDATED WITH FILE UPLOAD) ---
    with tab1:
        with st.form("add_doc"):
            title = st.text_input("Document Title")
            
            # New File Uploader
            uploaded_file = st.file_uploader("Upload File (Optional)", type=['txt', 'pdf', 'docx', 'md'])
            
            if st.form_submit_button("Add Document"):
                if api_create_document(project['user_id'], project_id, title, uploaded_file):
                    st.success("Document added successfully!")
                    # Optional: Rerun to refresh the list if needed
                else:
                    st.error("Failed to add document.")

    # 1b.4.2 Read Doc
    with tab2:
        did = st.number_input("Document ID", min_value=1, step=1)
        if st.button("Find Document"):
            doc = api_get_doc(did)
            if doc and doc.get('project_id') == project_id:
                st.json(doc)
            elif doc:
                st.warning("Document exists but belongs to a different project.")
            else:
                st.error("Document not found.")

    # 1b.4.3 Read All for Project
    with tab3:
        docs = api_get_project_docs(project_id)
        if docs:
            st.dataframe(pd.DataFrame(docs), use_container_width=True)
        else:
            st.info("No documents in this project.")

def page_projects_menu():
    if st.session_state['active_project_id']:
        page_specific_project(st.session_state['active_project_id'])
        return

    st.header("🏗️ Projects Menu")
    tab1, tab2, tab3 = st.tabs(["Create Project", "Find Project", "All Projects"])

    # 1b.1 Create Project
    with tab1:
        user_map = get_user_name_map()
        if not user_map:
            st.warning("No users found. Create a user first.")
        else:
            with st.form("new_proj"):
                p_name = st.text_input("Project Name")
                u_name = st.selectbox("Assign to User", options=list(user_map.keys()))
                if st.form_submit_button("Create Project"):
                    if api_create_project(p_name, user_map[u_name]):
                        st.success("Project created!")
                    else:
                        st.error("Failed.")

    # 1b.2 Read Single
    with tab2:
        pid = st.number_input("Enter Project ID", min_value=1, step=1)
        # Note: We don't have a direct 'read_project' API wrapper above, 
        # but we can add one or filter the list.
        # Let's filter the list for simplicity in this snippet.
        if st.button("Search"):
            all_p = api_get_projects()
            target = next((p for p in all_p if p['id'] == pid), None)
            if target:
                st.json(target)
            else:
                st.error("Project not found.")

    # 1b.3 List All
    with tab3:
        projects = api_get_projects()
        if projects:
            for p in projects:
                with st.container(border=True):
                    c1, c2 = st.columns([5, 1])
                    c1.subheader(p['name'])
                    c1.text(f"ID: {p['id']} | User ID: {p['user_id']}")
                    if c2.button("Open", key=f"btn_{p['id']}"):
                        st.session_state['active_project_id'] = p['id']
                        st.rerun()
        else:
            st.info("No projects found.")

# --- MAIN ---
def main():
    st.sidebar.title("Dashboard")
    menu = st.sidebar.radio("Go to:", ["Users Menu", "Projects Menu"])

    if menu == "Users Menu":
        st.session_state['active_project_id'] = None
        page_users()
    elif menu == "Projects Menu":
        page_projects_menu()

if __name__ == "__main__":
    main()