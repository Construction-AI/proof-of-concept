import streamlit as st
import requests
import os
import time

# Configuration
LLAMAINDEX_SERVICE_URL = os.getenv("LLAMAINDEX_SERVICE_URL", "http://llamaindex-service:8000")

st.set_page_config(
    page_title="RAG Document Chat",
    page_icon="📚",
    layout="wide"
)

def check_service_health():
    """Check if LlamaIndex service is healthy"""
    try:
        response = requests.get(f"{LLAMAINDEX_SERVICE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_index_status():
    """Check if index is ready"""
    try:
        response = requests.get(f"{LLAMAINDEX_SERVICE_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
        return {"index_ready": False, "query_engine_ready": False}
    except:
        return {"index_ready": False, "query_engine_ready": False}

def create_index(directory_path):
    """Create index from documents"""
    try:
        response = requests.post(
            f"{LLAMAINDEX_SERVICE_URL}/index",
            json={"directory_path": directory_path},
            timeout=300
        )
        if response.status_code == 200:
            return True, response.json()["message"]
        else:
            return False, response.json().get("detail", "Unknown error")
    except Exception as e:
        return False, str(e)

def query_documents(query):
    """Query the indexed documents"""
    try:
        response = requests.post(
            f"{LLAMAINDEX_SERVICE_URL}/query",
            json={"query": query},
            timeout=60
        )
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json().get("detail", "Unknown error")
    except Exception as e:
        return False, str(e)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "index_created" not in st.session_state:
    st.session_state.index_created = False

# Main UI
st.title("📚 RAG Document Chat")
st.markdown("Talk to your documents using AI")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Service status
    if check_service_health():
        st.success("✅ LlamaIndex service is running")
    else:
        st.error("❌ LlamaIndex service is not available")
        st.info("Waiting for service to start...")
        time.sleep(2)
        st.rerun()
    
    # Check index status
    status = check_index_status()
    if status["index_ready"]:
        st.success("✅ Index is ready")
        st.session_state.index_created = True
    else:
        st.warning("⚠️ No index created yet")
    
    st.divider()
    
    # Document indexing section
    st.header("📁 Index Documents")
    st.markdown("Documents should be placed in the `/documents` directory")
    
    directory_path = st.text_input(
        "Directory path (relative to /app)",
        value="/app/documents",
        help="Path to the directory containing your documents"
    )
    
    if st.button("🔄 Create Index", type="primary", use_container_width=True):
        with st.spinner("Creating embeddings... This may take a while."):
            success, message = create_index(directory_path)
            if success:
                st.success(message)
                st.session_state.index_created = True
                st.session_state.messages = []  # Clear chat history
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"Failed to create index: {message}")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.markdown("### 📖 Instructions")
    st.markdown("""
    1. Place your documents in the `documents` folder
    2. Click **Create Index** to process them
    3. Start asking questions about your documents
    """)

# Main chat area
if not st.session_state.index_created:
    st.info("👈 Please create an index from your documents using the sidebar to get started.")
else:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("📄 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}** (Score: {source['score']:.3f})")
                        st.text(source["text"])
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from LlamaIndex service
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                success, result = query_documents(prompt)
                
                if success:
                    response_text = result["response"]
                    sources = result.get("source_nodes", [])
                    
                    st.markdown(response_text)
                    
                    if sources:
                        with st.expander("📄 View Sources"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**Source {i}** (Score: {source['score']:.3f})")
                                st.text(source["text"])
                                st.divider()
                    
                    # Add assistant response to chat
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "sources": sources
                    })
                else:
                    error_message = f"❌ Error: {result}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })