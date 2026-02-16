from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from app.api.services.database_service import DatabaseService

router = APIRouter()

@router.post("/create_user", status_code=status.HTTP_201_CREATED)
def route_create_user(first_name: str, last_name: str, email: str):
    """
    Creates a new user.
    """
    db = DatabaseService()
    try:
        # 🔧 CHANGE: database method already handles commits/rollbacks
        if not db.create_user(first_name=first_name, last_name=last_name, email=email):
            raise Exception(f"Failed to create user '{full_name}'")

        # 🔧 CHANGE: return proper HTTP response without raw Response object
        full_name = first_name + " " + last_name
        return {"message": f"User '{full_name}' created successfully"}

    except Exception as e:
        # 🔧 CHANGE: surface error as HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        # 🔧 CHANGE: always close the DB connection
        db.close()


@router.get("/read_user/{user_id}")
def route_read_user(user_id: int):
    """
    Reads a single user by ID.
    """
    db = DatabaseService()
    try:
        # 🔧 CHANGE: correct parameter name
        user = db.read_user(user_id=user_id)

        # 🔧 CHANGE: handle not-found case explicitly
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # 🔧 CHANGE: sqlite3.Row is not JSON serializable → convert to dict
        return dict(user)

    finally:
        # 🔧 CHANGE: ensure connection cleanup
        db.close()


@router.get("/read_all_users")
def route_read_all_users():
    """
    Reads all users.
    """
    db = DatabaseService()
    try:
        users = db.read_all_users()

        # 🔧 CHANGE: convert sqlite3.Row objects to dictionaries
        return [dict(user) for user in users]

    finally:
        # 🔧 CHANGE: ensure connection cleanup
        db.close()
        
@router.post("/create_project", status_code=status.HTTP_201_CREATED)
def route_create_project(project_name: str, user_id: int):
    db = DatabaseService()
    try:
        if not db.create_project(project_name=project_name, user_id=user_id):
            raise Exception(f"Failed to create project '{project_name}'")

        return {"message": f"Project '{project_name}' created successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        db.close()


@router.get("/read_project/{project_id}")
def route_read_project(project_id: int):
    db = DatabaseService()
    try:
        project = db.read_project(project_id=project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return dict(project)

    finally:
        db.close()


@router.get("/read_all_projects")
def route_read_all_projects():
    db = DatabaseService()
    try:
        projects = db.read_all_projects()
        return [dict(project) for project in projects]

    finally:
        db.close()
        
@router.post("/create_document", status_code=status.HTTP_201_CREATED)
def route_create_document(user_id: int, project_id: int, document_title: str):
    db = DatabaseService()
    try:
        if not db.create_document(user_id=user_id, project_id=project_id, document_title=document_title):
            raise Exception(f"Failed to create document '{document_title}'")
        return {"message": f"Document '{document_title}' created successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        db.close()


@router.get("/read_document/{document_id}")
def route_read_document(document_id: int):
    db = DatabaseService()
    try:
        document = db.read_document(document_id=document_id)
        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        return dict(document)

    finally:
        db.close()


@router.get("/read_all_documents")
def route_read_all_documents():
    db = DatabaseService()
    try:
        documents = db.read_all_documents()
        return [dict(document) for document in documents]

    finally:
        db.close()

@router.get("/read_documents_by_project/{project_id}")
def route_read_documents_by_project(project_id: int):
    """
    Reads all documents associated with a specific project ID.
    """
    db = DatabaseService()
    try:
        # You will need to ensure your DatabaseService has a matching method
        documents = db.read_documents_by_project(project_id=project_id) 
        
        # If the DB service returns None or empty list, return empty list
        if not documents:
            return []
            
        return [dict(doc) for doc in documents]

    finally:
        db.close()