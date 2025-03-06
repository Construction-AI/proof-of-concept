# app/templates/document_templates.py

from typing import Dict, Any, List

# Document type templates with prompts and structure information
DOCUMENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "Plany BIOZ": {
        "prompt_template": """
        Utwórz Plan Bezpieczeństwa i Ochrony Zdrowia (BIOZ) dla projektu budowlanego "{project_name}".
        Plan powinien zawierać następujące sekcje:
        1. Zakres robót budowlanych
        2. Wykaz istniejących obiektów
        3. Elementy zagospodarowania terenu, które mogą stwarzać zagrożenie
        4. Przewidywane zagrożenia podczas realizacji robót
        5. Sposób instruktażu pracowników
        6. Środki techniczne i organizacyjne zapobiegające niebezpieczeństwom
        
        Użyj wiedzy o projektach budowlanych, uwzględniając informacje z dostarczonych dokumentów.
        """,
        "output_format": "docx",
        "sections": [
            {
                "name": "Zakres robót budowlanych",
                "key": "scope_of_work",
                "description": "Opis zakresu prac budowlanych przewidzianych w projekcie"
            },
            {
                "name": "Wykaz istniejących obiektów",
                "key": "existing_objects",
                "description": "Lista obiektów znajdujących się na terenie budowy"
            },
            {
                "name": "Elementy zagospodarowania terenu",
                "key": "site_elements",
                "description": "Elementy terenu, które mogą stwarzać zagrożenie"
            },
            {
                "name": "Przewidywane zagrożenia",
                "key": "anticipated_hazards",
                "description": "Lista potencjalnych zagrożeń podczas realizacji robót"
            },
            {
                "name": "Sposób instruktażu pracowników",
                "key": "worker_instruction",
                "description": "Procedury szkolenia pracowników w zakresie BHP"
            },
            {
                "name": "Środki zapobiegające niebezpieczeństwom",
                "key": "safety_measures",
                "description": "Środki techniczne i organizacyjne minimalizujące ryzyko"
            }
        ]
    },
    "Opisy techniczne (dla projektów budowlanych i wykonawczych)": {
        "prompt_template": """
        Opracuj opis techniczny dla projektu "{project_name}".
        Opis powinien zawierać:
        1. Podstawa opracowania
        2. Zakres opracowania
        3. Charakterystyka obiektu
        4. Rozwiązania materiałowe
        5. Instalacje
        6. Ochrona przeciwpożarowa
        
        Bazuj na informacjach zawartych w załączonych dokumentach projektu.
        """,
        "output_format": "docx",
        "sections": [
            {
                "name": "Podstawa opracowania",
                "key": "basis_of_development",
                "description": "Dokumenty stanowiące podstawę opracowania projektu"
            },
            {
                "name": "Zakres opracowania",
                "key": "scope_of_development",
                "description": "Szczegółowy zakres projektu"
            },
            {
                "name": "Charakterystyka obiektu",
                "key": "object_characteristics",
                "description": "Opis charakterystyki i parametrów obiektu"
            },
            {
                "name": "Rozwiązania materiałowe",
                "key": "material_solutions",
                "description": "Specyfikacja rozwiązań materiałowych"
            },
            {
                "name": "Instalacje",
                "key": "installations",
                "description": "Opis instalacji przewidzianych w projekcie"
            },
            {
                "name": "Ochrona przeciwpożarowa",
                "key": "fire_protection",
                "description": "Rozwiązania z zakresu ochrony przeciwpożarowej"
            }
        ]
    },
    "Karty materiałowe": {
        "prompt_template": """
        Przygotuj karty materiałowe dla projektu "{project_name}".
        Dla każdego kluczowego materiału podaj:
        1. Nazwa materiału
        2. Producent/dostawca
        3. Parametry techniczne
        4. Certyfikaty i atesty
        5. Warunki stosowania
        6. Metody montażu/wykonania
        
        Uwzględnij informacje z dostarczonych dokumentów projektowych.
        """,
        "output_format": "xlsx",
        "sections": [
            {
                "name": "Nazwa materiału",
                "key": "material_name",
                "description": "Pełna nazwa materiału"
            },
            {
                "name": "Producent/dostawca",
                "key": "manufacturer",
                "description": "Producent lub dostawca materiału"
            },
            {
                "name": "Parametry techniczne",
                "key": "technical_parameters",
                "description": "Szczegółowe parametry techniczne materiału"
            },
            {
                "name": "Certyfikaty i atesty",
                "key": "certificates",
                "description": "Wymagane certyfikaty i atesty dla materiału"
            },
            {
                "name": "Warunki stosowania",
                "key": "usage_conditions",
                "description": "Zalecane warunki stosowania materiału"
            },
            {
                "name": "Metody montażu/wykonania",
                "key": "installation_methods",
                "description": "Zalecane metody montażu i wykonania"
            }
        ]
    },
    "Specyfikacje techniczne wykonania i odbioru robót budowlanych (STWiORB)": {
        "prompt_template": """
        Opracuj Specyfikację Techniczną Wykonania i Odbioru Robót Budowlanych dla projektu "{project_name}".
        Specyfikacja powinna zawierać:
        1. Wymagania ogólne
        2. Materiały
        3. Sprzęt
        4. Transport
        5. Wykonanie robót
        6. Kontrola jakości
        7. Obmiar robót
        8. Odbiór robót
        9. Podstawa płatności
        
        Uwzględnij informacje z dostarczonych dokumentów.
        """,
        "output_format": "docx",
        "sections": [
            {
                "name": "Wymagania ogólne",
                "key": "general_requirements",
                "description": "Ogólne wymagania dotyczące robót"
            },
            {
                "name": "Materiały",
                "key": "materials",
                "description": "Specyfikacja wymaganych materiałów"
            },
            {
                "name": "Sprzęt",
                "key": "equipment",
                "description": "Wymagania dotyczące sprzętu"
            },
            {
                "name": "Transport",
                "key": "transport",
                "description": "Wymagania dotyczące transportu"
            },
            {
                "name": "Wykonanie robót",
                "key": "work_execution",
                "description": "Opis sposobu wykonania robót"
            },
            {
                "name": "Kontrola jakości",
                "key": "quality_control",
                "description": "Wymagania dotyczące kontroli jakości"
            },
            {
                "name": "Obmiar robót",
                "key": "work_measurement",
                "description": "Zasady obmiaru robót"
            },
            {
                "name": "Odbiór robót",
                "key": "work_acceptance",
                "description": "Procedury odbioru robót"
            },
            {
                "name": "Podstawa płatności",
                "key": "payment_basis",
                "description": "Podstawa płatności za wykonane roboty"
            }
        ]
    },
    "Zestawienia materiałowe i harmonogramy robót": {
        "prompt_template": """
        Przygotuj zestawienie materiałowe i harmonogram robót dla projektu "{project_name}".
        Zestawienie powinno zawierać:
        1. Wykaz wszystkich materiałów z jednostkami i ilościami
        2. Harmonogram robót z podziałem na etapy
        3. Czasy realizacji poszczególnych zadań
        4. Kolejność wykonywania prac
        5. Kamienie milowe projektu
        
        Bazuj na informacjach z dostarczonych dokumentów projektowych.
        """,
        "output_format": "xlsx",
        "sections": [
            {
                "name": "Wykaz materiałów",
                "key": "material_list",
                "description": "Kompletny wykaz materiałów z jednostkami i ilościami"
            },
            {
                "name": "Harmonogram robót",
                "key": "work_schedule",
                "description": "Harmonogram robót z podziałem na etapy"
            },
            {
                "name": "Czasy realizacji",
                "key": "implementation_times",
                "description": "Czasy realizacji poszczególnych zadań"
            },
            {
                "name": "Kolejność prac",
                "key": "work_sequence",
                "description": "Kolejność wykonywania prac budowlanych"
            },
            {
                "name": "Kamienie milowe",
                "key": "milestones",
                "description": "Kluczowe kamienie milowe projektu"
            }
        ]
    }
}

def get_document_template(document_type: str) -> Dict[str, Any]:
    """
    Get template for a specific document type
    
    Args:
        document_type: Type of document
        
    Returns:
        Template dictionary or None if not found
    """
    return DOCUMENT_TEMPLATES.get(document_type)

def get_available_document_types() -> List[str]:
    """
    Get list of available document types
    
    Returns:
        List of document type names
    """
    return list(DOCUMENT_TEMPLATES.keys())