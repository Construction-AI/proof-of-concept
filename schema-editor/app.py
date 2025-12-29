import streamlit as st
import json
from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel, ValidationError
import uuid
from copy import deepcopy

# ============================================================================
# PYDANTIC MODELS (Authoritative)
# ============================================================================

class SchemaBaseNode(BaseModel):
    id: str
    type: Literal[
        "document",
        "section",
        "subsection",
        "heading",
        "paragraph",
        "list",
        "list_item",
        "table",
        "field",
        "repeat",
        "conditional"
    ]

class FieldExtraction(BaseModel):
    status: Optional[str] = None
    confidence: Optional[float] = None

class SchemaField(BaseModel):
    type: Literal["field"] = "field"
    source: Literal["ai", "user"]
    prompt: Optional[str] = None
    required: Optional[bool] = None
    data_type: Literal["text", "number", "boolean", "date", "list[text]"]
    extraction: Optional[FieldExtraction] = None
    value: Optional[str] = None

class SchemaHeading(SchemaBaseNode):
    type: Literal["heading"] = "heading"
    text: str

class SchemaParagraph(SchemaBaseNode):
    type: Literal["paragraph"] = "paragraph"
    source: Literal["static", "field"]
    field: Optional[str] = None
    content: Optional[Union[str, FieldExtraction]] = None

class SchemaListItem(SchemaBaseNode):
    type: Literal["list_item"] = "list_item"
    children: List[Union['SchemaNode']] = []

class SchemaList(SchemaBaseNode):
    type: Literal["list"] = "list"
    list_type: Literal["numbered", "bulleted"]
    children: List[SchemaListItem] = []

class SchemaTable(SchemaBaseNode):
    type: Literal["table"] = "table"
    children: List[Union['SchemaNode']] = []

class SchemaSubsection(SchemaBaseNode):
    type: Literal["subsection"] = "subsection"
    title: str
    children: List[Union['SchemaNode']] = []

class SchemaSection(SchemaBaseNode):
    type: Literal["section"] = "section"
    title: str
    children: List[Union['SchemaNode']] = []

SchemaNode = Union[
    SchemaSection,
    SchemaSubsection,
    SchemaHeading,
    SchemaParagraph,
    SchemaList,
    SchemaListItem,
    SchemaTable,
]

class SchemaDocument(SchemaBaseNode):
    type: Literal["document"] = "document"
    meta: Dict[str, str]
    children: List[SchemaNode] = []
    fields: Dict[str, SchemaField] = {}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_id(prefix: str = "node") -> str:
    """Generate unique ID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def get_valid_child_types(parent_type: str) -> List[str]:
    """Return valid child node types for a given parent"""
    rules = {
        "document": ["section"],
        "section": ["subsection", "heading", "paragraph", "list", "table"],
        "subsection": ["heading", "paragraph", "list", "table"],
        "list": ["list_item"],
        "list_item": ["paragraph", "list"],
        "heading": [],
        "paragraph": [],
        "table": [],
    }
    return rules.get(parent_type, [])

def find_node_by_id(node: Dict, target_id: str) -> Optional[Dict]:
    """Recursively find a node by ID"""
    if node.get("id") == target_id:
        return node
    
    for child in node.get("children", []):
        result = find_node_by_id(child, target_id)
        if result:
            return result
    return None

def delete_node_by_id(node: Dict, target_id: str) -> bool:
    """Recursively delete a node by ID"""
    children = node.get("children", [])
    for i, child in enumerate(children):
        if child.get("id") == target_id:
            children.pop(i)
            return True
        if delete_node_by_id(child, target_id):
            return True
    return False

def move_node(parent: Dict, node_id: str, direction: str) -> bool:
    """Move node up or down within siblings"""
    children = parent.get("children", [])
    for i, child in enumerate(children):
        if child.get("id") == node_id:
            if direction == "up" and i > 0:
                children[i], children[i-1] = children[i-1], children[i]
                return True
            elif direction == "down" and i < len(children) - 1:
                children[i], children[i+1] = children[i+1], children[i]
                return True
            return False
    
    # Check nested children
    for child in children:
        if move_node(child, node_id, direction):
            return True
    return False

def get_field_references(node: Dict) -> List[str]:
    """Get all field references in the schema"""
    refs = []
    if node.get("type") == "paragraph" and node.get("source") == "field":
        field_ref = node.get("field")
        if field_ref:
            refs.append(field_ref)
    
    for child in node.get("children", []):
        refs.extend(get_field_references(child))
    
    return refs

def init_session_state():
    """Initialize session state with default schema"""
    if "schema" not in st.session_state:
        st.session_state.schema = {
            "id": generate_id("doc"),
            "type": "document",
            "meta": {
                "company_id": "",
                "project_id": "",
                "document_type": ""
            },
            "children": [],
            "fields": {}
        }
    
    if "editing_node" not in st.session_state:
        st.session_state.editing_node = None
    
    if "editing_field" not in st.session_state:
        st.session_state.editing_field = None

# ============================================================================
# PAGE 1: DOCUMENT META
# ============================================================================

def page_document_meta():
    st.header("📄 Document Metadata")
    
    schema = st.session_state.schema
    meta = schema.get("meta", {})
    
    st.subheader("Required Fields")
    
    col1, col2 = st.columns(2)
    
    with col1:
        company_id = st.text_input("Company ID", value=meta.get("company_id", ""), key="meta_company")
        project_id = st.text_input("Project ID", value=meta.get("project_id", ""), key="meta_project")
    
    with col2:
        document_type = st.text_input("Document Type", value=meta.get("document_type", ""), key="meta_doctype")
    
    # Additional metadata
    st.subheader("Additional Metadata")
    
    # Get additional keys
    additional_keys = [k for k in meta.keys() if k not in ["company_id", "project_id", "document_type"]]
    
    # Edit existing additional fields
    for key in additional_keys:
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.text_input("Key", value=key, disabled=True, key=f"addkey_{key}")
        with col2:
            new_value = st.text_input("Value", value=meta.get(key, ""), key=f"addval_{key}")
            meta[key] = new_value
        with col3:
            if st.button("🗑️", key=f"del_{key}"):
                del meta[key]
                st.rerun()
    
    # Add new field
    st.subheader("Add New Metadata Field")
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        new_key = st.text_input("New Key", key="new_meta_key")
    with col2:
        new_value = st.text_input("New Value", key="new_meta_value")
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ Add"):
            if new_key and new_key not in meta:
                meta[new_key] = new_value
                st.rerun()
            elif new_key in meta:
                st.error("Key already exists")
    
    # Update meta
    meta["company_id"] = company_id
    meta["project_id"] = project_id
    meta["document_type"] = document_type
    schema["meta"] = meta

# ============================================================================
# PAGE 2: STRUCTURE EDITOR
# ============================================================================

def render_node_tree(node: Dict, level: int = 0, parent_id: Optional[str] = None):
    """Recursively render node tree with actions"""
    indent = "　" * level
    node_type = node.get("type", "unknown")
    node_id = node.get("id", "")
    
    # Build node summary
    summary = f"{node_type}"
    if node_type in ["section", "subsection"]:
        summary += f": {node.get('title', 'Untitled')}"
    elif node_type == "heading":
        summary += f": {node.get('text', '')}"
    elif node_type == "paragraph":
        source = node.get("source", "")
        if source == "static":
            content = node.get("content", "")[:50]
            summary += f" (static): {content}..."
        elif source == "field":
            summary += f" (field): {node.get('field', 'none')}"
    elif node_type == "list":
        summary += f" ({node.get('list_type', 'bulleted')})"
    
    # Display node
    col1, col2, col3, col4, col5, col6 = st.columns([4, 1, 1, 1, 1, 1])
    
    with col1:
        st.text(f"{indent}└─ {summary}")
    
    with col2:
        valid_children = get_valid_child_types(node_type)
        if valid_children and st.button("➕", key=f"add_{node_id}"):
            st.session_state.editing_node = {"parent_id": node_id, "action": "add"}
            st.rerun()
    
    with col3:
        if st.button("✏️", key=f"edit_{node_id}"):
            st.session_state.editing_node = {"node": node, "action": "edit"}
            st.rerun()
    
    with col4:
        if st.button("🗑️", key=f"del_{node_id}"):
            delete_node_by_id(st.session_state.schema, node_id)
            st.rerun()
    
    with col5:
        if parent_id and st.button("⬆️", key=f"up_{node_id}"):
            parent = find_node_by_id(st.session_state.schema, parent_id)
            if parent:
                move_node(parent, node_id, "up")
                st.rerun()
    
    with col6:
        if parent_id and st.button("⬇️", key=f"down_{node_id}"):
            parent = find_node_by_id(st.session_state.schema, parent_id)
            if parent:
                move_node(parent, node_id, "down")
                st.rerun()
    
    # Render children
    for child in node.get("children", []):
        render_node_tree(child, level + 1, node_id)

def node_editor_form():
    """Display node editor form"""
    editing = st.session_state.editing_node
    
    if not editing:
        return
    
    action = editing.get("action")
    
    if action == "add":
        st.subheader("Add New Node")
        parent_id = editing.get("parent_id")
        parent = find_node_by_id(st.session_state.schema, parent_id)
        
        if not parent:
            st.error("Parent node not found")
            return
        
        valid_types = get_valid_child_types(parent.get("type"))
        
        node_type = st.selectbox("Node Type", valid_types)
        node_id = st.text_input("Node ID", value=generate_id(node_type))
        
        new_node = {"id": node_id, "type": node_type}
        
        # Type-specific fields
        if node_type in ["section", "subsection"]:
            title = st.text_input("Title", key="node_title")
            new_node["title"] = title
            new_node["children"] = []
        
        elif node_type == "heading":
            text = st.text_input("Text", key="node_text")
            new_node["text"] = text
        
        elif node_type == "paragraph":
            source = st.radio("Source", ["static", "field"], key="para_source")
            new_node["source"] = source
            
            if source == "static":
                content = st.text_area("Content", key="para_content")
                new_node["content"] = content
            else:
                fields = st.session_state.schema.get("fields", {})
                if fields:
                    field_key = st.selectbox("Field", list(fields.keys()), key="para_field")
                    new_node["field"] = field_key
                else:
                    st.warning("No fields defined. Please create fields first.")
                    new_node["field"] = None
        
        elif node_type == "list":
            list_type = st.radio("List Type", ["numbered", "bulleted"], key="list_type")
            new_node["list_type"] = list_type
            new_node["children"] = []
        
        elif node_type == "list_item":
            new_node["children"] = []
        
        elif node_type == "table":
            new_node["children"] = []
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Create Node"):
                parent.setdefault("children", []).append(new_node)
                st.session_state.editing_node = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.editing_node = None
                st.rerun()
    
    elif action == "edit":
        st.subheader("Edit Node")
        node = editing.get("node")
        node_type = node.get("type")
        
        st.text(f"Type: {node_type}")
        node_id = st.text_input("Node ID", value=node.get("id"))
        node["id"] = node_id
        
        # Type-specific fields
        if node_type in ["section", "subsection"]:
            title = st.text_input("Title", value=node.get("title", ""), key="edit_title")
            node["title"] = title
        
        elif node_type == "heading":
            text = st.text_input("Text", value=node.get("text", ""), key="edit_text")
            node["text"] = text
        
        elif node_type == "paragraph":
            source = st.radio("Source", ["static", "field"], 
                            index=0 if node.get("source") == "static" else 1, 
                            key="edit_para_source")
            node["source"] = source
            
            if source == "static":
                content = st.text_area("Content", value=node.get("content", "") if isinstance(node.get("content"), str) else "", key="edit_para_content")
                node["content"] = content
                node["field"] = None
            else:
                fields = st.session_state.schema.get("fields", {})
                if fields:
                    current_field = node.get("field")
                    field_options = list(fields.keys())
                    default_idx = field_options.index(current_field) if current_field in field_options else 0
                    field_key = st.selectbox("Field", field_options, index=default_idx, key="edit_para_field")
                    node["field"] = field_key
                    node["content"] = None
                else:
                    st.warning("No fields defined.")
        
        elif node_type == "list":
            list_type = st.radio("List Type", ["numbered", "bulleted"],
                               index=0 if node.get("list_type") == "numbered" else 1,
                               key="edit_list_type")
            node["list_type"] = list_type
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Changes"):
                st.session_state.editing_node = None
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.editing_node = None
                st.rerun()

def page_structure_editor():
    st.header("🏗️ Structure Editor")
    
    schema = st.session_state.schema
    
    # Node editor (if active)
    if st.session_state.editing_node:
        with st.expander("Node Editor", expanded=True):
            node_editor_form()
        st.divider()
    
    # Tree view
    st.subheader("Document Structure")
    
    # Add section button at document level
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text("📄 Document")
    with col2:
        if st.button("➕ Add Section", key="add_root_section"):
            st.session_state.editing_node = {"parent_id": schema["id"], "action": "add"}
            st.rerun()
    
    # Render tree
    for child in schema.get("children", []):
        render_node_tree(child, level=1, parent_id=schema["id"])
    
    if not schema.get("children"):
        st.info("No structure defined yet. Add a section to get started.")

# ============================================================================
# PAGE 3: FIELDS EDITOR
# ============================================================================

def page_fields_editor():
    st.header("🏷️ Fields Editor")
    
    schema = st.session_state.schema
    fields = schema.get("fields", {})
    
    # Display existing fields
    if fields:
        st.subheader("Existing Fields")
        
        for field_key, field_data in fields.items():
            with st.expander(f"**{field_key}** ({field_data.get('data_type', 'unknown')})"):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**Source:** {field_data.get('source', 'N/A')}")
                    st.write(f"**Data Type:** {field_data.get('data_type', 'N/A')}")
                    st.write(f"**Required:** {field_data.get('required', False)}")
                    if field_data.get('prompt'):
                        st.write(f"**Prompt:** {field_data.get('prompt')}")
                    if field_data.get('value'):
                        st.write(f"**Value:** {field_data.get('value')}")
                
                with col2:
                    if st.button("✏️ Edit", key=f"edit_field_{field_key}"):
                        st.session_state.editing_field = {"key": field_key, "data": deepcopy(field_data)}
                        st.rerun()
                    
                    # Check if field is referenced
                    refs = get_field_references(schema)
                    if field_key in refs:
                        st.warning("In use")
                    else:
                        if st.button("🗑️ Delete", key=f"del_field_{field_key}"):
                            del fields[field_key]
                            st.rerun()
    else:
        st.info("No fields defined yet.")
    
    st.divider()
    
    # Field editor
    if st.session_state.editing_field:
        st.subheader("Edit Field")
        editing = st.session_state.editing_field
        field_key = editing["key"]
        field_data = editing["data"]
        
        # Cannot change key when editing
        st.text_input("Field Key", value=field_key, disabled=True)
        
        source = st.selectbox("Source", ["ai", "user"], 
                            index=0 if field_data.get("source") == "ai" else 1,
                            key="edit_field_source")
        
        data_type = st.selectbox("Data Type", 
                                ["text", "number", "boolean", "date", "list[text]"],
                                index=["text", "number", "boolean", "date", "list[text]"].index(field_data.get("data_type", "text")),
                                key="edit_field_datatype")
        
        required = st.checkbox("Required", value=field_data.get("required", False), key="edit_field_required")
        
        prompt = None
        if source == "ai":
            prompt = st.text_area("Prompt (required for AI fields)", 
                                value=field_data.get("prompt", ""),
                                key="edit_field_prompt")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Field"):
                if source == "ai" and not prompt:
                    st.error("Prompt is required for AI fields")
                else:
                    fields[field_key] = {
                        "type": "field",
                        "source": source,
                        "data_type": data_type,
                        "required": required,
                        "prompt": prompt,
                        "extraction": field_data.get("extraction"),
                        "value": field_data.get("value")
                    }
                    st.session_state.editing_field = None
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.editing_field = None
                st.rerun()
    
    else:
        st.subheader("Add New Field")
        
        new_field_key = st.text_input("Field Key (unique identifier)", key="new_field_key")
        
        source = st.selectbox("Source", ["ai", "user"], key="new_field_source")
        
        data_type = st.selectbox("Data Type", 
                                ["text", "number", "boolean", "date", "list[text]"],
                                key="new_field_datatype")
        
        required = st.checkbox("Required", key="new_field_required")
        
        prompt = None
        if source == "ai":
            prompt = st.text_area("Prompt (required for AI fields)", key="new_field_prompt")
        
        if st.button("➕ Add Field"):
            if not new_field_key:
                st.error("Field key is required")
            elif new_field_key in fields:
                st.error("Field key already exists")
            elif source == "ai" and not prompt:
                st.error("Prompt is required for AI fields")
            else:
                fields[new_field_key] = {
                    "type": "field",
                    "source": source,
                    "data_type": data_type,
                    "required": required,
                    "prompt": prompt,
                    "extraction": None,
                    "value": None
                }
                st.rerun()

# ============================================================================
# PAGE 4: JSON PREVIEW
# ============================================================================

def page_json_preview():
    st.header("📋 JSON Preview")
    
    # Import section
    st.subheader("📥 Import Schema")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        uploaded_file = st.file_uploader("Upload JSON schema file", type=['json'], key="json_upload")
    
    with col2:
        st.write("")
        st.write("")
        if uploaded_file is not None:
            if st.button("🔄 Load Schema"):
                try:
                    # Read and decode file
                    json_bytes = uploaded_file.read()
                    json_str = json_bytes.decode('utf-8')
                    imported_schema = json.loads(json_str)
                    
                    # Validate before importing
                    is_valid, errors = validate_schema(imported_schema)
                    
                    if is_valid:
                        st.session_state.schema = imported_schema
                        st.session_state.editing_node = None
                        st.session_state.editing_field = None
                        st.success("✅ Schema imported successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid schema file")
                        for error in errors:
                            st.error(error)
                
                except json.JSONDecodeError as e:
                    st.error(f"❌ Invalid JSON file: {str(e)}")
                except UnicodeDecodeError:
                    st.error("❌ File encoding error. Please ensure the file is UTF-8 encoded.")
                except Exception as e:
                    st.error(f"❌ Error loading schema: {str(e)}")
    
    st.divider()
    
    # Export section
    st.subheader("📤 Export Schema")
    
    schema = st.session_state.schema
    
    # Use ensure_ascii=False to support Polish and other Unicode characters
    json_str = json.dumps(schema, indent=2, ensure_ascii=False)
    
    st.code(json_str, language="json", line_numbers=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Encode as UTF-8 bytes for download
        json_bytes = json_str.encode('utf-8')
        st.download_button(
            label="⬇️ Download JSON",
            data=json_bytes,
            file_name="document_schema.json",
            mime="application/json; charset=utf-8"
        )
    
    with col2:
        if st.button("📋 Copy to Clipboard"):
            st.info("💡 Use the copy button in the top-right corner of the code block above")

# ============================================================================
# PAGE 5: VALIDATION
# ============================================================================

def validate_schema(schema: Dict) -> tuple[bool, List[str]]:
    """Validate schema against Pydantic models"""
    errors = []
    
    try:
        # Try to parse as SchemaDocument
        SchemaDocument(**schema)
        return True, []
    except ValidationError as e:
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            errors.append(f"{loc}: {error['msg']}")
        return False, errors
    except Exception as e:
        errors.append(f"Unexpected error: {str(e)}")
        return False, errors

def page_validation():
    st.header("✅ Schema Validation")
    
    schema = st.session_state.schema
    
    if st.button("🔍 Validate Schema"):
        with st.spinner("Validating..."):
            is_valid, errors = validate_schema(schema)
        
        if is_valid:
            st.success("✅ Schema is valid!")
            st.balloons()
        else:
            st.error("❌ Schema validation failed")
            st.subheader("Errors:")
            for error in errors:
                st.error(error)
    
    st.divider()
    
    # Additional checks
    st.subheader("Additional Checks")
    
    # Check required meta fields
    meta = schema.get("meta", {})
    required_meta = ["company_id", "project_id", "document_type"]
    missing_meta = [k for k in required_meta if not meta.get(k)]
    
    if missing_meta:
        st.warning(f"⚠️ Missing required meta fields: {', '.join(missing_meta)}")
    else:
        st.success("✅ All required meta fields present")
    
    # Check field references
    fields = schema.get("fields", {})
    field_refs = get_field_references(schema)
    orphaned_refs = [ref for ref in field_refs if ref not in fields]
    
    if orphaned_refs:
        st.error(f"❌ Orphaned field references: {', '.join(orphaned_refs)}")
    else:
        st.success("✅ All field references valid")
    
    # Check AI fields have prompts
    ai_fields_missing_prompt = [k for k, v in fields.items() 
                               if v.get("source") == "ai" and not v.get("prompt")]
    
    if ai_fields_missing_prompt:
        st.error(f"❌ AI fields missing prompts: {', '.join(ai_fields_missing_prompt)}")
    else:
        st.success("✅ All AI fields have prompts")

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    st.set_page_config(
        page_title="Document Schema Editor",
        page_icon="📄",
        layout="wide"
    )
    
    init_session_state()
    
    st.title("📄 Document Schema Editor")
    st.caption("Create and manage structured document schemas")
    
    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📄 Document Meta",
        "🏗️ Structure Editor",
        "🏷️ Fields Editor",
        "📋 JSON Preview",
        "✅ Validation"
    ])
    
    with tab1:
        page_document_meta()
    
    with tab2:
        page_structure_editor()
    
    with tab3:
        page_fields_editor()
    
    with tab4:
        page_json_preview()
    
    with tab5:
        page_validation()

if __name__ == "__main__":
    main()