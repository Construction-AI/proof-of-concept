from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Literal, Dict

from app.models.schema.base_node import SchemaBaseNode
from app.models.schema.basic import (
    SchemaDocument,
    SchemaSection,
    SchemaSubsection,
    SchemaHeading,
    SchemaParagraph,
    SchemaList,
    SchemaListItem,
    SchemaTable,
    SchemaField
)

class DocxGenerator:
    def __init__(self):
        self.document = Document()
        self._configure_page()

    # -------------------------
    # Public API
    # -------------------------
    def generate(self, schema: SchemaDocument, output_path: str) -> None:
        for child in schema.children:
            self._render_node(child)
        self.document.save(output_path)
        
    def preprocess_schema(self, schema: SchemaDocument):
        for child in schema.children:
            self._preprocess_field(fields=schema.fields, node=child)

    # -------------------------
    # Page setup
    # ------------------------
    def _configure_page(self):
        section = self.document.sections[0]
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)

        # -------------------------
        # Base paragraph style
        # -------------------------
        normal = self.document.styles["Normal"]
        normal.font.name = "Times New Roman"
        normal.font.size = Pt(11)

        p_format = normal.paragraph_format
        p_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_format.first_line_indent = Cm(1.25)
        p_format.space_after = Pt(6)
        p_format.space_before = Pt(0)
        p_format.line_spacing = 1.5

        # -------------------------
        # Heading styles
        # -------------------------
        h1 = self.document.styles["Heading 1"]
        h1.font.name = "Times New Roman"
        h1.font.size = Pt(14)
        h1.font.bold = True
        h1.paragraph_format.space_before = Pt(24)
        h1.paragraph_format.space_after = Pt(12)

        h2 = self.document.styles["Heading 2"]
        h2.font.name = "Times New Roman"
        h2.font.size = Pt(13)
        h2.font.bold = True
        h2.paragraph_format.space_before = Pt(18)
        h2.paragraph_format.space_after = Pt(10)


    # -------------------------
    # Dispatcher
    # -------------------------
    def _render_node(self, node: SchemaBaseNode):
        handler = getattr(self, f"_render_{node.type}", None)
        if not handler:
            raise NotImplementedError(f"No renderer for node type: {node.type}")
        handler(node)
        
    # -------------------------
    # Preprocessors
    # -------------------------
    def _preprocess_field(self, fields: Dict[str, SchemaField], node: SchemaBaseNode):
        if not isinstance(node, SchemaParagraph):
            if isinstance(node, (SchemaSection, SchemaSubsection, SchemaList, SchemaListItem)):
                for child in node.children:
                    self._preprocess_field(fields, child)
            return
        if node.source == "static":
            if node.content is None:
                node.content = ""
        else:
            field = fields.get(node.field)
            if not field:
                raise ValueError(f"Could not find field for key: {node.field}")
            
            # TODO: Evaluate with AI
            if field.source == 'user':
                node.content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam fringilla orci justo, non porta leo posuere eget."
            else:
                # TODO: Implement RAG generation
                # from app.infra.knowledge_base.instances_knowledge_base import get_knowledge_base_wrapper
                # kbw = get_knowledge_base_wrapper()
                # node.content = await kbw.query
                node.content = "AI Generated"
        
        
    # -------------------------
    # Renderers
    # -------------------------
    def _render_section(self, node: SchemaSection):
        self.document.add_heading(node.title, level=1)
        for child in node.children:
            self._render_node(child)


    def _render_subsection(self, node: SchemaSubsection):
        self.document.add_heading(node.title, level=2)
        for child in node.children:
            self._render_node(child)

    def _render_heading(self, node: SchemaHeading):
        self.document.add_paragraph(node.text, style="Heading 3")

    def _render_paragraph(self, node: SchemaParagraph):
        text = node.content or ""
        p = self.document.add_paragraph(text, style="Normal")
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


    def _render_list(self, node: SchemaList):
        for child in node.children:
            self._render_list_item(list_type=node.list_type, node=child)

    def _render_list_item(self, list_type: Literal["numbered", "bulleted"], node: SchemaListItem):
        for child in node.children:
            if isinstance(child, SchemaParagraph):
                style = "List Number" if list_type == "numbered" else "List Bullet"
                p = self.document.add_paragraph(child.content or "", style=style)

                # ---- indentation ----
                p.paragraph_format.left_indent = Pt(2)

                # ---- spacing ----
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(4)

                # ---- alignment ----
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            else:
                self._render_node(child)


    def _render_table(self, node: SchemaTable):
        # Placeholder: depends on your final table model
        table = self.document.add_table(rows=1, cols=1)
        table.style = "Table Grid"
