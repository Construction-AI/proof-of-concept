import streamlit as st
from src.api.client import APIClient
from typing import cast, Any, Dict

# 1. Identity & Access Check
if "token" not in st.session_state or not st.session_state.token:
    st.warning("Please log in on the Home page to access the RAG interface.")
    st.stop()

# Initialize Client safely
api = APIClient(token=cast(str, st.session_state.token))

st.title("🤖 Project AI Assistant")
st.markdown("Query your indexed documents using LlamaIndex & Qdrant.")

# --- SIDEBAR: Project Selection ---
with st.sidebar:
    st.header("Settings")
    project_res = api.get_projects()
    
    project_id = None
    if project_res.status_code == 200:
        projects = project_res.json()
        if not projects:
            st.warning("No projects found. Please create one first.")
        else:
            project_names = {p['title']: p['id'] for p in projects}
            selected_project_name = st.selectbox("Select Project Scope", options=list(project_names.keys()))
            if selected_project_name:
                project_id = project_names[selected_project_name]
    else:
        st.error(f"Could not load projects. (Status: {project_res.status_code})")
        st.stop()

    # Toggle between Simple (Faster) and Confidence (Slower/Detailed)
    use_confidence = st.toggle("Show Confidence & Reasoning", value=False)

# --- CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages: # type: ignore
    with st.chat_message(message["role"]): # type: ignore
        st.markdown(message["content"]) # type: ignore

# User Input
if prompt := st.chat_input("Ask something about your documents..."):
    
    if project_id is None:
        st.error("Please select a project from the sidebar first.")
        st.stop()

    # Add User Message to State
    st.session_state.messages.append({"role": "user", "content": prompt}) # type: ignore
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            
            # 1. Prepare Payload based on Schema: QueryProjectRequest
            payload = {
                "question": prompt, 
                "project_id": project_id
            }
            
            # 2. Select Endpoint
            # /c/project returns FinalResponse (complex)
            # /q/project returns QueryResponse (simple)
            endpoint = "/rag/c/project" if use_confidence else "/rag/q/project"
            
            try:
                response = api.post_rag(endpoint, payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer_text = ""
                    
                    if use_confidence:
                        # Handle FinalResponse
                        # Schema: { "structured_answer": { "answer": "...", "confidence_score": 0.9, ...}, "sources": [...] }
                        struct = data.get('structured_answer', {})
                        answer_text = struct.get('answer', "No answer provided.")
                        confidence = struct.get('confidence_score', 0.0)
                        reasoning = struct.get('reasoning', "No reasoning provided.")
                        sources = data.get('sources', [])
                        
                        st.markdown(answer_text)
                        
                        # Display Metadata
                        with st.expander("Confidence & Reasoning", expanded=False):
                            st.info(f"**Confidence:** {confidence*100:.1f}%")
                            st.write(f"**Reasoning:** {reasoning}")
                            if sources:
                                st.write("**Sources:**")
                                for s in sources:
                                    st.text(f"- {s}")
                                    
                    else:
                        # Handle QueryResponse
                        # Schema: { "response": "..." }
                        answer_text = data.get('response', "No response received.")
                        st.markdown(answer_text)
                    
                    # Save to History
                    st.session_state.messages.append({"role": "assistant", "content": answer_text}) # type: ignore

                else:
                    st.error(f"Server Error: {response.status_code}")
                    st.error(response.text)
                    
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")