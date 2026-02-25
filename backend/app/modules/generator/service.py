import markdown
import asyncio
from weasyprint import HTML #, CSS
from jinja2 import Template
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.modules.templates.models import TemplateNodes
from app.modules.rag.service import RagService

class DocumentGenerator:
    def __init__(self, db_session: Session):
        self.db = db_session

    # --- FAZA 1: Rekonstrukcja (Z płaskiej tablicy w zagnieżdżone drzewo) ---
    def _build_tree(self, flat_nodes: List[TemplateNodes]):
        """Zamienia płaską listę z bazy na strukturę drzewiastą O(N)"""
        nodes_by_id: Dict[str, Any] = {node.id: {**node.__dict__, "data": node.data, "children": []} for node in flat_nodes}
        roots: List[TemplateNodes] = []
        
        for node in flat_nodes:
            if node.parent_id:
                # Dodajemy węzeł jako dziecko jego rodzica
                nodes_by_id[node.parent_id]["children"].append(nodes_by_id[node.id])
            else:
                # Jeśli nie ma rodzica, to jest korzeń (np. główna sekcja)
                roots.append(nodes_by_id[node.id])
                
        return roots

    # --- FAZA 2: Rezolucja (Przechodzenie po drzewie i pytanie AI) ---
    async def _resolve_node(self, node: Dict[str, Any], project_id: int, user_id: int) -> str:
        """Przetwarza pojedynczy węzeł i jego dzieci na czysty HTML"""
        node_type = node["type"]
        node_data = node["data"]
        
        content_html = ""

        # 1. RAG EXTRACTION - Uderzamy do LLM / Qdranta
        if node_type == "rag_extraction":
            try:
                # Wywołanie Twojego LLM-a!
                response = await RagService.query_with_dynamic_type(
                    db=self.db,
                    instruction=node_data["prompt"],
                    output_type=str, # TODO: Change dynamically
                    project_id=project_id,
                    user_id=user_id
                    )
                # LLM często zwraca Markdown, konwertujemy to na HTML
                content_html = markdown.markdown(response["answer"])
            except Exception:
                # W razie awarii AI lub braku dokumentów, wstawiamy Fallback
                content_html = f"<p class='text-gray'><em>{node_data.get('fallback_text', 'Brak danych')}</em></p>"

        # 2. STATIC TEXT
        elif node_type == "static_text":
            content_html = markdown.markdown(node_data["text"])

        # 3. KONTENERY (SEKCJE / LISTY) - Przetwarzamy dzieci rekurencyjnie
        elif node_type in ["section", "list"]:
            # Równoległe wywołanie AI dla wszystkich dzieci! 
            # (Dzięki asyncio.gather wygenerowanie 10 paragrafów przez RAG trwa tyle samo co 1)
            children_tasks = [self._resolve_node(child, project_id, user_id) for child in node["children"]]
            children_results = await asyncio.gather(*children_tasks)
            children_html = "".join(children_results)

            if node_type == "section":
                # Dodajemy nagłówek, jeśli włączono w kreatorze
                heading = ""
                if node_data.get("show_title", True):
                    h_level = node_data.get("heading_level", 2)
                    heading = f"<h{h_level}>{node_data['title']}</h{h_level}>"
                
                # Opcjonalny podział strony (Page Break) zdefiniowany w kreatorze
                page_break = "page-break-before: always;" if node_data.get("page_before_break") else ""
                
                content_html = f"<div style='{page_break} margin-bottom: 2rem;'>{heading}{children_html}</div>"
            
            elif node_type == "list":
                # Zwijamy dzieci w listę HTML (ul = punktowana, ol = numerowana)
                tag = "ol" if node_data.get("list_type") == "numbered" else "ul"
                content_html = f"<{tag} class='spacing-{node_data.get('spacing', 'normal')}'>{children_html}</{tag}>"

        return content_html

    # --- FAZA 3: Kompilacja (Złożenie w całość i generacja PDF) ---
    async def generate_pdf(self, project_id: int, template_nodes: List[TemplateNodes], project_name: str, user_id: int) -> bytes:
        # 1. Budowa drzewa
        tree = self._build_tree(template_nodes)
        
        # 2. Odpytanie sztucznej inteligencji dla całego dokumentu
        resolved_tasks = [self._resolve_node(root, project_id, user_id) for root in tree]
        resolved_sections = await asyncio.gather(*resolved_tasks)
        body_html = "".join(resolved_sections)

        # 3. Wrzucenie do szablonu Jinja2 (To jest nasz główny "szkielet" dokumentu)
        # Zdefiniujemy w nim podstawowy CSS (np. fonty, marginesy)
        html_template = """
        <!DOCTYPE html>
        <html lang="pl">
        <head>
            <meta charset="UTF-8">
            <style>
                @page {
                    size: A4;
                    margin: 2.5cm 2cm;
                    @bottom-right {
                        content: "Strona " counter(page) " z " counter(pages);
                        font-size: 10pt;
                        color: gray;
                    }
                }
                body { font-family: 'Helvetica', 'Arial', sans-serif; color: #333; line-height: 1.6; }
                h1 { color: #1e3a8a; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px; }
                h2 { color: #2563eb; margin-top: 1.5em; }
                .text-gray { color: #6b7280; }
                ul.spacing-relaxed li { margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <div style="text-align: center; margin-bottom: 50px;">
                <h1>Raport z Bazy Wiedzy RAG</h1>
                <h3>Projekt: {{ project_name }}</h3>
                <p>Wygenerowano automatycznie przez AI.</p>
            </div>
            
            {{ body_content }}
        </body>
        </html>
        """
        
        # Kompilujemy HTML
        template = Template(html_template)
        final_html_string = template.render(
            project_name=project_name, 
            body_content=body_html
        )

        # 4. Magia WeasyPrint: Zamiana HTML na fizyczny plik PDF w pamięci RAM
        pdf_bytes = HTML(string=final_html_string).write_pdf() # type: ignore
        
        return pdf_bytes # type: ignore