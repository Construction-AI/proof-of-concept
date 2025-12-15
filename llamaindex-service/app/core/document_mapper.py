class DocumentMapper:
    __SCHEMA_BASE_PATH = "/app/schemas"
    __DOCX_TEMPLATE_BASE_PATH = "/app/templates"
    
    __HSE_KEY = "health_and_safety_plan"
    __SDR_KEY = "structural_design_report"
    
    __DOCUMENT_CATEGORIES_MAP = {
        __HSE_KEY: {
            "template_path": __DOCX_TEMPLATE_BASE_PATH + "/health_and_safety_plan.docx",
            "schema_path": __SCHEMA_BASE_PATH + "/health_and_safety_plan.json",
            "valid_names": [
                "bioz",
                "health_and_safety_plan",
                "health and safety plan"
            ]
        },
        __SDR_KEY: {
            "template_path": __DOCX_TEMPLATE_BASE_PATH + "/structural_design_report.docx",
            "schema_path": __SCHEMA_BASE_PATH + "/structural_design_report.json",
            "valid_names": [
                "opis konstrukcji",
                "opis_konstrukcji",
                "structural_design_report",
                "structural design report"
            ]
        }
    }
    
    @staticmethod
    def get_document_type_for_name(name: str) -> str:
        keys = [key.lower() for key in DocumentMapper.__DOCUMENT_CATEGORIES_MAP.keys()]
        name = name.lower()
        if name.lower() in keys:
            return name
        
        for k, v in DocumentMapper.__DOCUMENT_CATEGORIES_MAP.items():
            if name in v["valid_names"]:
                return k
        
        raise ValueError(f"Document type {name} is not recognized. Valid types: [{', '.join(keys)}]")
    
    @staticmethod
    def get_path_for_document_schema_by_name(name: str) -> str:
        document_type = DocumentMapper.get_document_type_for_name(name=name)
        return DocumentMapper.__DOCUMENT_CATEGORIES_MAP[document_type]["schema_path"]
    
    @staticmethod
    def get_path_for_document_template_by_name(name: str) -> str:
        document_type = DocumentMapper.get_document_type_for_name(name=name)
        return DocumentMapper.__DOCUMENT_CATEGORIES_MAP[document_type]["template_path"]
    
    @staticmethod 
    def get_valid_document_types() -> list[str]:
        return DocumentMapper.__DOCUMENT_CATEGORIES_MAP.keys()