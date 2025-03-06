import streamlit as st
import os
import datetime

# Set the specific directory for uploads
UPLOAD_DIR = "/data/documents"

# Check if directory exists and create it if it doesn't
if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except PermissionError:
        st.error(f"Permission denied: Cannot create directory at {UPLOAD_DIR}. Please check permissions.")
        st.stop()

st.title("Project Submission Form")

with st.form(key="project_form"):
    st.subheader("Project Details")
    
    # Project name input
    project_name = st.text_input("Project Name")
    
    # Project industry dropdown
    industry = st.selectbox(
        "Project Industry",
        options=["Construction"]
    )
    
    # File uploader
    uploaded_files = st.file_uploader("Upload Project Files", 
                                     type=["pdf", "docx", "xlsx", "csv", "txt"],
                                     accept_multiple_files=True)
    
    # Submit button
    submit_button = st.form_submit_button(label="Submit Project")

# Process the form data when submitted
if submit_button:
    if not project_name:
        st.error("Please enter a project name.")
    elif not uploaded_files:
        st.warning("Please upload at least one file.")
    else:
        try:
            # Save uploaded files directly to the main directory
            saved_files = []
            for uploaded_file in uploaded_files:
                # Create file path (add timestamp to prevent overwriting files with same name)
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"{timestamp}_{uploaded_file.name}"
                file_path = os.path.join(UPLOAD_DIR, file_name)
                
                # Save the file
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                saved_files.append(file_path)
            
            # Success message
            st.success(f"Project '{project_name}' submitted successfully!")
            
            # Display the submitted information
            st.write("### Submission Summary")
            st.write(f"**Project Name:** {project_name}")
            st.write(f"**Industry:** {industry}")
            
            # List saved files
            st.write(f"**Files saved to:** {UPLOAD_DIR}")
            for file_path in saved_files:
                st.write(f"- {os.path.basename(file_path)}")
                
        except PermissionError:
            st.error(f"Permission denied: Cannot write to {UPLOAD_DIR}. Please check permissions.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")