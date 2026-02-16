from typing import Optional

from app.modules.projects.models import Project

def project_check_user_access(user_id: int, project: Optional[Project] = None):
    if not project:
        raise Exception("Project was not found.")
    if not user_id == project.owner_id:
        raise Exception("Project does not belong to user")