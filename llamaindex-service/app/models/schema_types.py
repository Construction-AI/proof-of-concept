from enum import Enum
from typing import Tuple

BASE_PATH = "/app/schema"

class SchemaType(Enum):
    BIOZ: Tuple[str, str] = ("bioz", BASE_PATH + "/bioz_generation_schema_full.json")
    OPIS_KONSTRUKCJI: Tuple[str, str] = ("opis konstrukcji", BASE_PATH + "/extraction_schema_konstrukcja_full.json")
    BAZA_PROJEKTOWA: Tuple[str, str] = ("baza projektowa", BASE_PATH + "/project_info_extraction_schema.json")

    def get_key(self) -> str:
        return self.value[0]
    
    def get_path(self) -> str:
        return self.value[1]
    
    @staticmethod
    def list_available_schema_types() -> list:
        return [st.get_key() for st in SchemaType]
    
    @staticmethod
    def get_path_for_type_name(type_name: str) -> str:
        for st in SchemaType:
            if (st.get_key() == type_name.lower()):
                return st.get_path()
        else:
            raise ValueError(f"No schema type found for: {type_name}. Available types: [{', '.join(SchemaType.list_available_schema_types())}]")
        
    @staticmethod
    def get_schema_type_for_type_name(type_name: str) -> str:
        for st in SchemaType:
            if (st.get_key() == type_name.lower()):
                return st
        else:
            raise ValueError(f"No schema type found for: {type_name}. Available types: [{', '.join(SchemaType.list_available_schema_types())}]")
        