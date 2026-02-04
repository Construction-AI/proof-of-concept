from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse

from app.api.services.database_service import DatabaseService

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
def route_create_user(first_name: str, last_name: str, email: str):
    """
    Creates a new user.
    """
    db = DatabaseService()
    try:
        # 🔧 CHANGE: database method already handles commits/rollbacks
        db.create_user(first_name=first_name, last_name=last_name, email=email)

        # 🔧 CHANGE: return proper HTTP response without raw Response object
        return {"message": "User created successfully"}

    except Exception as e:
        # 🔧 CHANGE: surface error as HTTP exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    finally:
        # 🔧 CHANGE: always close the DB connection
        db.close()


@router.get("/read/{user_id}")
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


@router.get("/read_all")
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
