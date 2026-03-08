import markdown
import asyncio
from weasyprint import HTML
from jinja2 import Template
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.modules.templates.models import TemplateNodes
from app.modules.rag.service import RagService


class DocumentGenerator:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.semaphore = asyncio.Semaphore(3)
        self.rag_service = RagService(db=db_session)

    # =============================
    # TREE BUILDING
    # =============================

    def _build_tree(self, flat_nodes: List[TemplateNodes]) -> List[Dict[str, Any]]:
        nodes_by_id: Dict[str, Dict[str, Any]] = {
            node.id: {
                **node.__dict__,
                "data": node.data,
                "children": []
            }
            for node in flat_nodes
        }

        roots: List[Dict[str, Any]] = []

        for node in flat_nodes:
            if node.parent_id:
                nodes_by_id[node.parent_id]["children"].append(nodes_by_id[node.id])
            else:
                roots.append(nodes_by_id[node.id])

        return roots

    # =============================
    # NODE RESOLUTION (Dispatcher)
    # =============================

    async def _resolve_node(
        self,
        node: Dict[str, Any],
        project_id: int,
        user_id: int,
        parent_type: Optional[str] = None
    ) -> str:
        node_type = node["type"]

        if node_type == "rag_extraction":
            return await self._resolve_rag_node(node, project_id, user_id, parent_type)

        if node_type == "static_text":
            return self._resolve_static_text_node(node)

        if node_type in ["section", "list"]:
            return await self._resolve_container_node(node, project_id, user_id)

        return ""

    # =============================
    # RAG NODE
    # =============================

    async def _resolve_rag_node(
        self,
        node: Dict[str, Any],
        project_id: int,
        user_id: int,
        parent_type: Optional[str]
    ) -> str:
        node_data = node["data"]
        is_in_list = parent_type == "list"

        try:
            response = await self._query_rag_with_retry(
                instruction=node_data["prompt"],
                project_id=project_id,
                user_id=user_id,
                output_type=List[str] if is_in_list else str
            )
            
            if is_in_list:
                cleaned_items = [
                    self._strip_ordinal_prefix(self._preserve_single_line_breaks(item))
                    for item in response["answer"]
                ]

                return "".join(f"<li>{item}</li>" for item in cleaned_items)

            text = self._preserve_single_line_breaks(response["answer"])
            return markdown.markdown(text)

        except Exception:
            return self._render_fallback(node_data)

    async def _query_rag_with_retry(
        self,
        instruction: str,
        project_id: int,
        user_id: int,
        output_type: Any
    ) -> Dict[str, Any]:
        for attempt in range(3):
            try:
                async with self.semaphore:
                    return await self.rag_service.query_with_dynamic_type(
                        instruction=instruction,
                        output_type=output_type,
                        project_id=project_id,
                        user_id=user_id
                    )
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        raise RuntimeError("RAG query failed after retries")

    def _render_fallback(self, node_data: Dict[str, Any]) -> str:
        fallback_text = node_data.get("fallback_text", "Brak danych")
        return f"<p class='text-gray'><em>{fallback_text}</em></p>"

    # =============================
    # STATIC TEXT NODE
    # =============================

    def _resolve_static_text_node(self, node: Dict[str, Any]) -> str:
        text = self._preserve_single_line_breaks(node["data"]["text"])
        return markdown.markdown(text)

    # =============================
    # CONTAINER NODE (SECTION / LIST)
    # =============================

    async def _resolve_container_node(
        self,
        node: Dict[str, Any],
        project_id: int,
        user_id: int
    ) -> str:
        node_type = node["type"]
        node_data = node["data"]

        children_html = await self._resolve_children(
            node["children"],
            project_id,
            user_id,
            node_type
        )

        if node_type == "section":
            return self._render_section(node_data, children_html)

        if node_type == "list":
            return self._render_list(node_data, children_html)

        return ""

    async def _resolve_children(
        self,
        children: List[Dict[str, Any]],
        project_id: int,
        user_id: int,
        parent_type: str
    ) -> str:
        tasks = [
            self._resolve_node(child, project_id, user_id, parent_type)
            for child in children
        ]
        results = await asyncio.gather(*tasks)
        return "".join(results)

    def _render_section(self, node_data: Dict[str, Any], children_html: str) -> str:
        heading = ""
        if node_data.get("show_title", True):
            level = node_data.get("heading_level", 2)
            heading = f"<h{level}>{node_data['title']}</h{level}>"

        page_break = (
            "page-break-before: always;"
            if node_data.get("page_before_break")
            else ""
        )

        return (
            f"<div style='{page_break} margin-bottom: 2rem;'>"
            f"{heading}{children_html}</div>"
        )

    def _render_list(self, node_data: Dict[str, Any], children_html: str) -> str:
        tag = "ol" if node_data.get("list_type") == "numbered" else "ul"
        spacing = node_data.get("spacing", "normal")
        return f"<{tag} class='spacing-{spacing}'>{children_html}</{tag}>"

    # =============================
    # HTML TEMPLATE + PDF
    # =============================

    async def generate_pdf(
        self,
        project_id: int,
        template_nodes: List[TemplateNodes],
        project_name: str,
        template_name: str,
        user_id: int
    ) -> bytes:
        tree = self._build_tree(template_nodes)

        body_html = await self._resolve_document_tree(
            tree, project_id, user_id
        )

        final_html = self._render_html_template(
            project_name=project_name,
            template_name=template_name,
            body_content=body_html
        )

        return HTML(string=final_html).write_pdf() # type: ignore

    async def _resolve_document_tree(
        self,
        tree: List[Dict[str, Any]],
        project_id: int,
        user_id: int
    ) -> str:
        tasks = [
            self._resolve_node(root, project_id, user_id)
            for root in tree
        ]
        sections = await asyncio.gather(*tasks)
        return "".join(sections)

    def _render_html_template(
        self,
        project_name: str,
        template_name: str,
        body_content: str
    ) -> str:
        template = Template(self._build_html_template())
        return template.render(
            project_name=project_name,
            template_name=template_name,
            body_content=body_content,
            date=datetime.now().strftime("%d/%m/%Y")
        )

    def _build_html_template(self) -> str:
        from app.modules.generator.const import DOCUMENT_TEMPLATE
        return DOCUMENT_TEMPLATE
    
    def _strip_ordinal_prefix(self, text: str) -> str:
        import re
        
        """
        Removes leading ordinal patterns like:
        1. Text
        12. Text
        3) Text
        """
        return re.sub(r"^\s*\d+[\.\)]\s+", "", text)
    
    def _preserve_single_line_breaks(self, text: str) -> str:
        """
        Converts single newlines to <br> so they are preserved in HTML.
        """
        return text.replace("\n", "<br>")