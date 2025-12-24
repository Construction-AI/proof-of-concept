from app.models.schema.base_node import SchemaBaseNode
from app.models.schema.basic import *

class SchemaMapper:
    @staticmethod
    def parse_element(data: dict) -> SchemaBaseNode:
        if data["type"] == "document":
            return SchemaDocument(
                id=data["id"],
                meta=data["meta"],
                children=[SchemaMapper.parse_element(item) for item in data["children"]]
            )
        if data["type"] == "section":
            return SchemaSection(
                id=data["id"],
                title=data["title"],
                children=[SchemaMapper.parse_element(item) for item in data["children"]],
            )
            
        if data["type"] == "subsection":
            return SchemaSubsection(
                id=data["id"],
                children=[SchemaMapper.parse_element(item) for item in data["children"]],
            )
            
        if data["type"] == "heading":
            return SchemaHeading(
                id=data["id"],
            )
            
        if data["type"] == "paragraph":
            return SchemaParagraph(
                id=data["id"],
                source=data["source"],
                field=data.get("field"),
                content=data.get("content")
            )
            
        if data["type"] == "list":
            return SchemaList(
                id=data["id"],
                children=[SchemaMapper.parse_element(item) for item in data["children"]],
                list_type=data["list_type"]
            )
            
        if data["type"] == "list_item":
            return SchemaListItem(
                id=data["id"],
                children=[SchemaMapper.parse_element(item) for item in data["children"]],
            )
            
        if data["type"] == "table":
            return SchemaTable(
                id=data["id"],
            )
    
    @staticmethod
    def parse_schema(data: dict) -> SchemaDocument:
        document = SchemaMapper.parse_element(data=data)
        
        for k,v in data["fields"].items():
            field = SchemaField(
                id=str(k),
                source=v.get("source"),
                prompt=v.get("prompt"),
                required=v.get("required"),
                data_type=v.get("data_type")
            )
            
            document.fields[k] = field
        return document