from docx import Document
from docx.shared import Cm
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
            node.content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam fringilla orci justo, non porta leo posuere eget."
            
        
        
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
        text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam fringilla orci justo, non porta leo posuere eget."
        # if node.source == "static":
        #     text = node.content or ""
        # else:
        #     # by this stage fields MUST be resolved
        #     raise ValueError("Unresolved field paragraph reached DOCX renderer")

        self.document.add_paragraph(text, style="Normal")

    def _render_list(self, node: SchemaList):
        for child in node.children:
            self._render_list_item(list_type=node.list_type, node=child)

    def _render_list_item(self, list_type: Literal["numbered", "bulleted"], node: SchemaListItem):
        for child in node.children:
            if isinstance(child, SchemaParagraph):
                style = "List Number" if list_type == "numbered" else "List Bullet"
                self.document.add_paragraph(
                    child.content or "",
                    style=style
                )
            else:
                self._render_node(child)

    def _render_table(self, node: SchemaTable):
        # Placeholder: depends on your final table model
        table = self.document.add_table(rows=1, cols=1)
        table.style = "Table Grid"
