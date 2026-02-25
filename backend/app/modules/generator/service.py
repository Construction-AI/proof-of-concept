import markdown
import asyncio
from weasyprint import HTML
from jinja2 import Template
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.modules.templates.models import TemplateNodes

from app.modules.rag.service import RagService

class DocumentGenerator:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.semaphore = asyncio.Semaphore(3)
        
    def _build_tree(self, flat_nodes: List[TemplateNodes]) -> List[TemplateNodes]:
        nodes_by_id: Dict[str, Any] = {node.id: {**node.__dict__, "data": node.data, "children": []} for node in flat_nodes}
        roots: List[TemplateNodes] = []
        
        for node in flat_nodes:
            if node.parent_id:
                nodes_by_id[node.parent_id]["children"].append(nodes_by_id[node.id])
            else:
                roots.append(nodes_by_id[node.id])

        return roots

    async def _resolve_node(self, node: Dict[str, Any], project_id: int, user_id: int, parent_type: Optional[str] = None) -> str:
        node_type = node["type"]
        node_data = node["data"]
        
        content_html = ""

        if node_type == "rag_extraction":
            try:
                is_in_list = (parent_type == "list")
                response = None
                
                # Prosty system Retry (maksymalnie 3 próby)
                for attempt in range(3):
                    try:
                        # Semafor kolejkuje zapytania do OpenAI
                        async with self.semaphore:
                            response = await RagService.query_with_dynamic_type(
                                db=self.db,
                                instruction=node_data["prompt"],
                                output_type=List[str] if is_in_list else str,
                                project_id=project_id,
                                user_id=user_id
                            )
                        break  # Jeśli się udało, przerywamy pętlę prób
                    except Exception as e:
                        if "429" in str(e) and attempt < 2:
                            # Exponential backoff: czeka 1s, potem 2s
                            await asyncio.sleep(2 ** attempt) 
                        else:
                            raise e # Przekazujemy błąd dalej, jeśli to nie 429 lub wyczerpano próby
                
                if is_in_list:
                    items_html = "".join([f"<li>{item}</li>" for item in response["answer"]]) # type: ignore
                    content_html = items_html
                else:
                    content_html = markdown.markdown(response["answer"]) # type: ignore
                    
            except Exception as e:
                print(f"Błąd węzła RAG: {e}")
                content_html = f"<p class='text-gray'><em>{node_data.get('fallback_text', 'Brak danych')}</em></p>"

        # 2. STATIC TEXT
        elif node_type == "static_text":
            content_html = markdown.markdown(node_data["text"])

        # 3. KONTENERY (SEKCJE / LISTY) - Przetwarzamy dzieci rekurencyjnie
        elif node_type in ["section", "list"]:
            # Równoległe wywołanie AI dla wszystkich dzieci! 
            # (Dzięki asyncio.gather wygenerowanie 10 paragrafów przez RAG trwa tyle samo co 1)
            children_tasks = [self._resolve_node(child, project_id, user_id, node_type) for child in node["children"]]
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
    async def generate_pdf(self, project_id: int, template_nodes: List[TemplateNodes], project_name: str, template_name: str, user_id: int) -> bytes:
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
                /* Ustawienia strony i marginesów */
                @page {
                    size: A4;
                    margin: 25mm 20mm 25mm 20mm;
                    
                    /* Nagłówek i stopka dla każdej strony */
                    @top-left {
                        content: "Projekt: {{ project_name }}";
                        font-size: 9pt;
                        color: #64748b;
                        border-bottom: 1px solid #e2e8f0;
                        padding-bottom: 5px;
                    }
                    @top-right {
                        content: "Dokumentacja Techniczna";
                        font-size: 9pt;
                        color: #64748b;
                        border-bottom: 1px solid #e2e8f0;
                        padding-bottom: 5px;
                    }
                    @bottom-left {
                        content: "Wygenerowano automatycznie przez system RAG AI";
                        font-size: 8pt;
                        color: #94a3b8;
                        border-top: 1px solid #e2e8f0;
                        padding-top: 5px;
                    }
                    @bottom-right {
                        content: "Strona " counter(page) " z " counter(pages);
                        font-size: 9pt;
                        color: #64748b;
                        border-top: 1px solid #e2e8f0;
                        padding-top: 5px;
                    }
                }

                /* Usunięcie nagłówków i stopek ze strony tytułowej */
                @page :first {
                    @top-left { content: none; border: none; }
                    @top-right { content: none; border: none; }
                    @bottom-left { content: none; border: none; }
                    @bottom-right { content: none; border: none; }
                }

                /* Główne style typograficzne */
                body { 
                    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
                    color: #1e293b; 
                    line-height: 1.6; 
                    font-size: 11pt;
                    text-align: justify;
                }

                /* Strona tytułowa */
                .cover-page {
                    text-align: center;
                    margin-top: 30vh;
                    page-break-after: always;
                }
                .cover-title {
                    font-size: 28pt;
                    color: #0f172a;
                    margin-bottom: 10px;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                .cover-subtitle {
                    font-size: 16pt;
                    color: #3b82f6;
                    margin-bottom: 40px;
                }
                .cover-meta {
                    font-size: 12pt;
                    color: #64748b;
                    border-top: 2px solid #e2e8f0;
                    padding-top: 20px;
                    width: 60%;
                    margin: 0 auto;
                }

                /* Nagłówki w treści */
                h1 { 
                    color: #0f172a; 
                    border-bottom: 2px solid #2563eb; 
                    padding-bottom: 8px; 
                    font-size: 18pt; 
                    margin-top: 1.5em; 
                    page-break-after: avoid; /* Zapobiega zostawianiu nagłówka na końcu strony */
                }
                h2 { 
                    color: #1e293b; 
                    font-size: 14pt; 
                    margin-top: 1.2em; 
                    page-break-after: avoid; 
                }
                
                /* Elementy list i tekstu */
                /* Precyzyjna kontrola wcięcia list */
                ul, ol { 
                    padding-left: 18px; 
                    margin-left: 0; 
                    margin-bottom: 1em; 
                }
                li { margin-bottom: 6px; }
                .text-gray { color: #64748b; font-style: italic; }
                
                /* Różne warianty odstępów dla list z kreatora */
                ul.spacing-compact li, ol.spacing-compact li { margin-bottom: 2px; }
                ul.spacing-relaxed li, ol.spacing-relaxed li { margin-bottom: 12px; }
            </style>
        </head>
        <body>
            <div class="cover-page">
                <div class="cover-title">{{ template_name }}</div>
                <div class="cover-subtitle">Baza Wiedzy Projektu</div>
                <div class="cover-meta">
                    <p><strong>Projekt:</strong> {{ project_name }}</p>
                    <p><strong>Data wygenerowania:</strong> {{ date }}</p>
                </div>
            </div>
            
            {{ body_content }}
        </body>
        </html>
        """
        
        # Kompilujemy HTML
        from datetime import datetime
        template = Template(html_template)
        final_html_string = template.render(
            project_name=project_name, 
            body_content=body_html,
            template_name=template_name,
            date=datetime.now().strftime("%d/%m/%Y")
        )

        # 4. Magia WeasyPrint: Zamiana HTML na fizyczny plik PDF w pamięci RAM
        pdf_bytes = HTML(string=final_html_string).write_pdf() # type: ignore
        
        return pdf_bytes # type: ignore