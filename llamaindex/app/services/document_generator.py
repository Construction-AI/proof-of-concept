# app/services/document_generator.py

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Document type templates with prompts
DOCUMENT_TEMPLATES = {
    "Plany BIOZ": """
        Utwórz Plan Bezpieczeństwa i Ochrony Zdrowia (BIOZ) dla projektu budowlanego "{project_name}".
        Plan powinien zawierać następujące sekcje:
        1. Zakres robót budowlanych
        2. Wykaz istniejących obiektów
        3. Elementy zagospodarowania terenu
        4. Przewidywane zagrożenia podczas realizacji robót
        5. Sposób instruktażu pracowników
        6. Środki techniczne i organizacyjne zapobiegające niebezpieczeństwom
        
        Użyj wiedzy o projektach budowlanych, uwzględniając informacje z dostarczonych dokumentów.
    """,
    "Opisy techniczne (dla projektów budowlanych i wykonawczych)": """
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
    "Karty materiałowe": """
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
    "Specyfikacje techniczne wykonania i odbioru robót budowlanych (STWiORB)": """
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
    "Zestawienia materiałowe i harmonogramy robót": """
        Przygotuj zestawienie materiałowe i harmonogram robót dla projektu "{project_name}".
        Zestawienie powinno zawierać:
        1. Wykaz wszystkich materiałów z jednostkami i ilościami
        2. Harmonogram robót z podziałem na etapy
        3. Czasy realizacji poszczególnych zadań
        4. Kolejność wykonywania prac
        5. Kamienie milowe projektu
        
        Bazuj na informacjach z dostarczonych dokumentów projektowych.
    """
}

class DocumentGeneratorService:
    def __init__(self, indexing_service):
        """
        Initialize document generator with indexing service
        
        Args:
            indexing_service: Instance of IndexingService
        """
        self.indexing_service = indexing_service
    
    def generate_document(self, project_name: str, industry: str, document_type: str) -> Dict[str, Any]:
        """
        Generate document based on the specified type
        
        Args:
            project_name: Name of the project
            industry: Industry of the project
            document_type: Type of document to generate
            
        Returns:
            Document generation result
        """
        try:
            # Check if document type exists in templates
            if document_type not in DOCUMENT_TEMPLATES:
                return {
                    "status": "error",
                    "message": f"Unknown document type: {document_type}"
                }
            
            # Get the prompt template and format it
            prompt_template = DOCUMENT_TEMPLATES[document_type]
            prompt = prompt_template.format(project_name=project_name)
            
            # Query the index to generate document content
            result = self.indexing_service.query_index(prompt)
            
            # Return the raw query result
            return {
                "status": "completed",
                "project_name": project_name,
                "industry": industry,
                "document_type": document_type,
                "content": result,
                "message": f"Successfully generated {document_type}"
            }
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            return {
                "status": "error",
                "message": f"Error generating document: {str(e)}"
            }