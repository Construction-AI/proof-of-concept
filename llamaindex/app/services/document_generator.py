from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path
import uuid
import asyncio

# Import your IndexingService
from indexing_service import IndexingService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Document type templates and prompts
DOCUMENT_TEMPLATES = {
    "Plany BIOZ": {
        "prompt_template": """
        Utwórz Plan Bezpieczeństwa i Ochrony Zdrowia (BIOZ) dla projektu budowlanego "{project_name}".
        Plan powinien zawierać następujące sekcje:
        1. Zakres robót budowlanych
        2. Wykaz istniejących obiektów
        3. Elementy zagospodarowania terenu, które mogą stwarzać zagrożenie
        4. Przewidywane zagrożenia podczas realizacji robót
        5. Sposób instruktażu pracowników
        6. Środki techniczne i organizacyjne zapobiegające niebezpieczeństwom
        
        Użyj wiedzy o projektach budowlanych, uwzględniając informacje z dostarczonych dokumentów.
        """,
        "output_format": "docx",
        "sections": ["Wstęp", "Zakres robót", "Wykaz obiektów", "Zagrożenia", "Instruktaż", "Środki bezpieczeństwa"]
    },
    "Opisy techniczne (dla projektów budowlanych i wykonawczych)": {
        "prompt_template": """
        Opracuj opis techniczny dla projektu "{project_name}".
        Opis powinien zawierać:
        1. Podstawa opracowania
        2. Zakres opracowania
        3. Charakterystyka obiektu
        4. Rozwiązania materiałowe
        5. Instalacje
        6. Ochrona przeciwpożarowa
        
        Bazuj na informacjach zawartych w załączonych dokumentach projektu.
        """,
        "output_format": "docx",
        "sections": ["Podstawa opracowania", "Zakres", "Charakterystyka", "Materiały", "Instalacje", "Ochrona ppoż."]
    },
    "Karty materiałowe": {
        "prompt_template": """
        Przygotuj karty materiałowe dla projektu "{project_name}".
        Dla każdego kluczowego materiału podaj:
        1. Nazwa materiału
        2. Producent/dostawca
        3. Parametry techniczne
        4. Certyfikaty i atesty
        5. Warunki stosowania
        6. Metody montażu/wykonania
        
        Uwzględnij informacje z dostarczonych dokumentów projektowych.
        """,
        "output_format": "xlsx",
        "sections": ["Materiał", "Producent", "Parametry", "Certyfikaty", "Warunki", "Montaż"]
    },
    "Specyfikacje techniczne wykonania i odbioru robót budowlanych (STWiORB)": {
        "prompt_template": """
        Opracuj Specyfikację Techniczną Wykonania i Odbioru Robót Budowlanych dla projektu "{project_name}".
        Specyfikacja powinna zawierać:
        1. Wymagania ogólne
        2. Materiały
        3. Sprzęt
        4. Transport
        5. Wykonanie robót
        6. Kontrola jakości
        7. Obmiar robót
        8. Odbiór robót
        9. Podstawa płatności
        
        Uwzględnij informacje z dostarczonych dokumentów.
        """,
        "output_format": "docx",
        "sections": ["Wymagania", "Materiały", "Sprzęt", "Transport", "Wykonanie", "Kontrola", "Obmiar", "Odbiór", "Płatności"]
    },
    "Zestawienia materiałowe i harmonogramy robót": {
        "prompt_template": """
        Przygotuj zestawienie materiałowe i harmonogram robót dla projektu "{project_name}".
        Zestawienie powinno zawierać:
        1. Wykaz wszystkich materiałów z jednostkami i ilościami
        2. Harmonogram robót z podziałem na etapy
        3. Czasy realizacji poszczególnych zadań
        4. Kolejność wykonywania prac
        5. Kamienie milowe projektu
        
        Bazuj na informacjach z dostarczonych dokumentów projektowych.
        """,
        "output_format": "xlsx",
        "sections": ["Zestawienie", "Harmonogram", "Czasy", "Kolejność", "Kamienie milowe"]
    }
}

# Create a storage for tracking generation jobs
job_status = {}

class DocumentGenerator:
    def __init__(self, indexing_service: IndexingService):
        """Initialize document generator with the indexing service"""
        self.indexing_service = indexing_service
        
    async def generate_document(self, project_name: str, industry: str, document_type: str) -> Dict[str, Any]:
        """
        Generate document based on indexed content
        
        Args:
            project_name: Name of the project
            industry: Industry of the project
            document_type: Type of document to generate
            
        Returns:
            Dict with generation results
        """
        try:
            # Check if document type exists in templates
            if document_type not in DOCUMENT_TEMPLATES:
                return {
                    "status": "error",
                    "message": f"Unknown document type: {document_type}"
                }
            
            template = DOCUMENT_TEMPLATES[document_type]
            
            # Format the prompt with project details
            prompt = template["prompt_template"].format(project_name=project_name)
            
            # Query the index to generate document content
            result = self.indexing_service.query_index(prompt)
            
            if "status" in result and result["status"] == "error":
                return result
                
            # Process the result into sections based on the template
            sections = template["sections"]
            document_structure = {}
            
            # For simplicity, we'll just use the source nodes and result text
            # In a real implementation, you'd process the result into structured sections
            document_structure["content"] = result["result"]
            document_structure["source_nodes"] = result["source_nodes"]
            document_structure["sections"] = sections
            document_structure["format"] = template["output_format"]
            
            return {
                "status": "completed",
                "document_structure": document_structure,
                "message": f"Successfully generated {document_type}"
            }
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating document: {str(e)}"
            }

app = FastAPI(title="Document Generator API", version="1.0.0")

# Base directory for document storage
DOCUMENTS_BASE_DIR = "/data/documents"

@app.on_event("startup")
async def startup_event():
    """Create necessary directories on startup"""
    os.makedirs(DOCUMENTS_BASE_DIR, exist_ok=True)

@app.post("/api/projects")
async def create_project(
    project_name: str = Form(...),
    industry: str = Form(...),
    document_type: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Create a new project with documents and initiate document generation
    
    Args:
        project_name: Name of the project
        industry: Industry of the project
        document_type: Type of document to generate
        files: List of files to upload
        
    Returns:
        JSON response with job ID for status tracking
    """
    try:
        # Generate unique project ID
        project_id = str(uuid.uuid4())
        
        # Create project directory
        project_dir = os.path.join(DOCUMENTS_BASE_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        # Save uploaded files
        saved_files = []
        for file in files:
            file_path = os.path.join(project_dir, file.filename)
            
            # Save the file
            with open(file_path, "wb") as f:
                contents = await file.read()
                f.write(contents)
            
            saved_files.append(file.filename)
        
        # Create job and set initial status
        job_id = str(uuid.uuid4())
        job_status[job_id] = {
            "status": "processing",
            "project_id": project_id,
            "project_name": project_name,
            "industry": industry,
            "document_type": document_type,
            "files": saved_files,
            "message": "Job created, processing documents..."
        }
        
        # Start background task for document generation
        background_tasks = BackgroundTasks()
        background_tasks.add_task(
            process_generation_job,
            job_id,
            project_id,
            project_name,
            industry,
            document_type
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "job_id": job_id,
                "status": "processing",
                "message": "Document generation job has been submitted"
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Get the status of a document generation job
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        JSON response with current job status
    """
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    return job_status[job_id]

@app.get("/api/projects/{project_id}/document")
async def get_document(project_id: str):
    """
    Get the generated document for a project
    
    Args:
        project_id: ID of the project
        
    Returns:
        JSON response with document structure
    """
    # Find job by project ID
    matching_jobs = [job for job_id, job in job_status.items() if job.get("project_id") == project_id]
    
    if not matching_jobs:
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    job = matching_jobs[0]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Document generation not completed: {job['status']}")
    
    return {
        "project_id": project_id,
        "project_name": job["project_name"],
        "document_type": job["document_type"],
        "document": job.get("document", {})
    }

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project and its files
    
    Args:
        project_id: ID of the project to delete
        
    Returns:
        JSON response confirming deletion
    """
    project_dir = os.path.join(DOCUMENTS_BASE_DIR, project_id)
    
    if not os.path.exists(project_dir):
        raise HTTPException(status_code=404, detail=f"Project not found: {project_id}")
    
    try:
        # Delete project directory
        shutil.rmtree(project_dir)
        
        # Update job statuses
        for job_id, job in job_status.items():
            if job.get("project_id") == project_id:
                job["status"] = "deleted"
                job["message"] = "Project has been deleted"
        
        return {"status": "success", "message": f"Project {project_id} deleted successfully"}
    
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")

async def process_generation_job(
    job_id: str,
    project_id: str,
    project_name: str,
    industry: str,
    document_type: str
):
    """
    Process a document generation job in the background
    
    Args:
        job_id: ID of the job
        project_id: ID of the project
        project_name: Name of the project
        industry: Industry of the project
        document_type: Type of document to generate
    """
    try:
        # Update job status
        job_status[job_id]["status"] = "indexing"
        job_status[job_id]["message"] = "Indexing documents..."
        
        # Initialize indexing service
        project_dir = os.path.join(DOCUMENTS_BASE_DIR, project_id)
        
        indexing_service = IndexingService(
            documents_dir=project_dir,
            collection_name=f"project_{project_id}"
        )
        
        # Process documents
        indexing_result = indexing_service.process_directory()
        
        if indexing_result["status"] == "error":
            job_status[job_id]["status"] = "error"
            job_status[job_id]["message"] = indexing_result["message"]
            return
        
        # Update job status
        job_status[job_id]["status"] = "generating"
        job_status[job_id]["message"] = "Generating document..."
        
        # Generate document
        document_generator = DocumentGenerator(indexing_service)
        generation_result = await document_generator.generate_document(
            project_name=project_name,
            industry=industry,
            document_type=document_type
        )
        
        if generation_result["status"] == "error":
            job_status[job_id]["status"] = "error"
            job_status[job_id]["message"] = generation_result["message"]
            return
        
        # Update job status with final result
        job_status[job_id]["status"] = "completed"
        job_status[job_id]["message"] = "Document generation completed"
        job_status[job_id]["document"] = generation_result["document_structure"]
        
    except Exception as e:
        logger.error(f"Error in job processing: {str(e)}")
        job_status[job_id]["status"] = "error"
        job_status[job_id]["message"] = f"Error in job processing: {str(e)}"

