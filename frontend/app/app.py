import streamlit as st
import os
import shutil
import requests
import json

# Set the specific directory for uploads
UPLOAD_DIR = "/data/documents"
API_URL = os.environ.get("API_GATEWAY_BASE_URL", "http://localhost:8080") + "/api"

# Check if directory exists and create it if it doesn't
if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except PermissionError:
        st.error(f"Permission denied: Cannot create directory at {UPLOAD_DIR}. Please check permissions.")
        st.stop()

st.title("Project Document Generator")

# Check if documents exist in directory
existing_documents = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f))] if os.path.exists(UPLOAD_DIR) else []
has_documents = len(existing_documents) > 0

# Create tabs for different actions
tab1, tab2 = st.tabs(["Generate Document", "Manage Files"])

with tab2:
    st.header("Manage Uploaded Files")
    
    if not has_documents:
        st.info("No files have been uploaded yet.")
    else:
        st.write(f"**Currently uploaded files:** {len(existing_documents)}")
        
        # Display file list with checkboxes for selection
        st.write("### Files in Directory")
        files_to_remove = []
        
        # Create columns for better layout
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write("**Filename**")
        with col2:
            st.write("**Size**")
        with col3:
            st.write("**Remove**")
            
        for file in existing_documents:
            file_path = os.path.join(UPLOAD_DIR, file)
            file_size = os.path.getsize(file_path)
            
            # Format file size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(file)
            with col2:
                st.write(size_str)
            with col3:
                if st.checkbox("", key=f"remove_{file}"):
                    files_to_remove.append(file)
        
        # Add buttons for file actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Remove Selected Files"):
                if files_to_remove:
                    for file in files_to_remove:
                        file_path = os.path.join(UPLOAD_DIR, file)
                        os.remove(file_path)
                    st.success(f"Removed {len(files_to_remove)} files")
                    # Process documents after removal
                    try:
                        with st.spinner("Processing remaining documents..."):
                            process_url = API_URL + "/indexes/process"
                            process_response = requests.post(process_url)
                            process_response.raise_for_status()
                            st.success("Documents reindexed successfully!")
                    except Exception as e:
                        st.error(f"Error reindexing documents: {str(e)}")
                    st.rerun()
                else:
                    st.info("No files selected for removal")
        
        with col2:
            if st.button("Clear All Files"):
                try:
                    url = API_URL + "/documents/clear"
                    response = requests.delete(url)
                    response.raise_for_status()

                    # Remove all files from the directory
                    for file in existing_documents:
                        file_path = os.path.join(UPLOAD_DIR, file)
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    st.success("All documents have been cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing documents: {str(e)}")
    
    # Allow uploading more files
    st.write("### Upload Additional Files")
    uploaded_files = st.file_uploader(
        "Select files to upload",
        type=["pdf", "docx", "xlsx", "csv", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("Upload Files"):
        with st.spinner("Uploading files..."):
            saved_files = []
            for uploaded_file in uploaded_files:
                # Create file path
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                # Save the file
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_files.append(file_path)
            
            st.success(f"Successfully uploaded {len(saved_files)} files")
            
            # Process documents immediately after upload
            try:
                with st.spinner("Processing uploaded documents..."):
                    process_url = API_URL + "/indexes/process"
                    process_response = requests.post(process_url)
                    process_response.raise_for_status()
                    
                    # Show processing results
                    process_result = process_response.json()
                    st.success(f"Documents processed successfully! Indexed {process_result.get('document_count', 0)} documents")
            except Exception as e:
                st.error(f"Error processing documents: {str(e)}")
                
            st.rerun()

with tab1:
    st.header("Generate Document")
    
    if not has_documents:
        st.warning("No files are currently uploaded. Please upload files in the 'Manage Files' tab first.")
    else:
        st.write(f"Using {len(existing_documents)} uploaded files for document generation.")
        with st.expander("View files"):
            for file in existing_documents:
                st.write(f"- {file}")
    
        # Step 3: Show form with required fields
        with st.form(key="project_form"):
            st.subheader("Project Details")
            
            # Project name input
            project_name = st.text_input("Project Name")
            
            # Project industry dropdown
            industry = st.selectbox(
                "Project Industry",
                options=["Construction"]
            )
            
            # Document type selection
            document_type = st.selectbox(
                "Typ dokumentu do wygenerowania",
                options=[
                    "Plany BIOZ",
                    "Opisy techniczne (dla projektów budowlanych i wykonawczych)",
                    "Karty materiałowe",
                    "Specyfikacje techniczne wykonania i odbioru robót budowlanych (STWiORB)",
                    "Zestawienia materiałowe i harmonogramy robót"
                ]
            )
            
            # Generate button
            generate_button = st.form_submit_button(label="Generate")
            
            # Process the form data when submitted
            if generate_button:
                if not project_name:
                    st.error("Please enter a project name.")
                else:
                    # Generate the document directly without reprocessing
                    with st.spinner(f"Generating {document_type}..."):
                        try:
                            # Prepare form data for document generation
                            generate_url = API_URL + "/documents/generate"
                            
                            generate_data = {
                                "project_name": project_name,
                                "industry": industry,
                                "document_type": document_type
                            }
                            
                            generate_response = requests.post(
                                generate_url,
                                data=generate_data
                            )
                            generate_response.raise_for_status()
                            
                            # Display the generation results
                            generation_result = generate_response.json()
                            st.success(f"Document generated successfully: {document_type}")
                            
                            # Display summary
                            st.write("### Generation Summary")
                            st.write(f"**Project Name:** {project_name}")
                            st.write(f"**Industry:** {industry}")
                            st.write(f"**Document Type:** {document_type}")
                            
                            # Display raw JSON result in an expandable section
                            with st.expander("Raw JSON Response"):
                                st.json(generation_result)
                            
                            # Display the generated content in a more readable format
                            st.write("### Generated Content")
                            try:
                                content = generation_result.get("content", {}).get("result", "No content available")
                                st.write(content)
                            except Exception as content_error:
                                st.error(f"Error displaying content: {str(content_error)}")
                                st.write("Raw content:")
                                st.write(str(generation_result.get("content", "No content available")))
                                
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to generate document: {str(e)}")