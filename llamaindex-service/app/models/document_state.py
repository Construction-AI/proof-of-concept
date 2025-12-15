from app.core.document_mapper import DocumentMapper

class DocumentType:
    def __init__(self, type: str):
        self.type = DocumentMapper.get_document_type_for_name(name=type)
        
    
    
    