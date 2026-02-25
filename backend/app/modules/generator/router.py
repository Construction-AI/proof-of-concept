from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.modules.generator.service import DocumentGenerator
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.projects.models import Project
from app.modules.templates.models import TemplateNodes
from app.modules.generator.schemas import GenerateRequest

from urllib.parse import quote


router = APIRouter()

@router.post("/generate")
async def generate_report_from_template(
    request: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Pobierz dane o projekcie (żeby mieć jego nazwę do nagłówka)
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nie istnieje")

    # 2. Pobierz płaską listę klocków z bazy dla tego szablonu
    nodes = db.query(TemplateNodes).filter(TemplateNodes.template_id == request.template_id).all()
    if not nodes:
        raise HTTPException(status_code=400, detail="Szablon jest pusty!")

    generator = DocumentGenerator(db)
    pdf_bytes = await generator.generate_pdf(
        project_id=request.project_id,
        template_nodes=nodes,
        project_name=project.title,
        user_id=user.id
    )

    safe_title = project.title.replace(" ", "_")
    encoded_filename = quote(f"Raport_{safe_title}.pdf")

    # Zwróć jako fizyczny plik PDF
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf",
        headers={
            # Używamy formatu filename*=utf-8'' (zwróć uwagę na dwa apostrofy)
            "Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"
        }
    )