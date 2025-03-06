import streamlit as st
import os
import shutil
import requests
import json

# Set the specific directory for uploads
UPLOAD_DIR = "/data/documents"
API_URL = os.environ.get("LLAMAINDEX_API_URL", "http://localhost:8000") + "/api/"

# Check if directory exists and create it if it doesn't
if not os.path.exists(UPLOAD_DIR):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    except PermissionError:
        st.error(f"Permission denied: Cannot create directory at {UPLOAD_DIR}. Please check permissions.")
        st.stop()

st.title("Project Document Generator")

# Check if documents exist in directory
existing_documents = os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else []
has_documents = len(existing_documents) > 0

# Step 1 & 2: Show clear button if documents exist
if has_documents:
    st.warning(f"There are {len(existing_documents)} documents in the directory.")
    if st.button("Clear All Documents"):
        try:
            url = API_URL + "clear"
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
    st.write("Please clear the documents before continuing.")
else:
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
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload Project Files",
            type=["pdf", "docx", "xlsx", "csv", "txt"],
            accept_multiple_files=True
        )
        
        # Step 4: Generate button
        generate_button = st.form_submit_button(label="Generate")
        
        # Process the form data when submitted
        if generate_button:
            if not project_name:
                st.error("Please enter a project name.")
            elif not uploaded_files:
                st.warning("Please upload at least one file.")
            else:
                try:
                    # Save uploaded files to the directory
                    saved_files = []
                    for uploaded_file in uploaded_files:
                        # Create file path
                        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                        # Save the file
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        saved_files.append(file_path)
                    
                    # Print to console for debugging
                    print(f"Generating document for: {project_name}, Industry: {industry}, Type: {document_type}")
                    
                    # Display the submitted information
                    st.write("### Files Uploaded")
                    st.write(f"**Files saved to:** {UPLOAD_DIR}")
                    for file_path in saved_files:
                        st.write(f"- {os.path.basename(file_path)}")
                    
                    # First step: Process/index the documents
                    with st.spinner("Processing documents..."):
                        try:
                            process_url = API_URL + "process"
                            st.write(f"Processing URL: {process_url}")
                            process_response = requests.post(process_url)
                            process_response.raise_for_status()
                            st.success("Documents processed successfully!")
                            
                            # Show processing results
                            process_result = process_response.json()
                            st.write(f"Processed {process_result.get('document_count', 0)} documents")
                            
                        except requests.exceptions.RequestException as e:
                            st.error(f"Failed to process documents: {str(e)}")
                            st.stop()
                    
                    # Second step: Generate the document
                    with st.spinner(f"Generating {document_type}..."):
                        try:
                            # Prepare form data for document generation
                            generate_url = API_URL + "generate-document"
                            st.write(f"Generation URL: {generate_url}")
                            
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
                    
                except PermissionError:
                    st.error(f"Permission denied: Cannot write to {UPLOAD_DIR}. Please check permissions.")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")