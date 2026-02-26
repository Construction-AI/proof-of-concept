DOCUMENT_STYLING = """
<style>
    /* Ustawienia strony i marginesów */
    @page {
        size: A4;
        margin: 25mm 20mm 25mm 20mm;
        
        /* Nagłówek i stopka dla każdej strony */
        @top-left {
            content: "Projekt: {{ project_name }}";
            font-size: 9pt;
            color: #64748b;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 5px;
        }
        @top-right {
            content: "Dokumentacja Techniczna";
            font-size: 9pt;
            color: #64748b;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 5px;
        }
        @bottom-left {
            content: "Wygenerowano automatycznie przez system RAG AI";
            font-size: 8pt;
            color: #94a3b8;
            border-top: 1px solid #e2e8f0;
            padding-top: 5px;
        }
        @bottom-right {
            content: "Strona " counter(page) " z " counter(pages);
            font-size: 9pt;
            color: #64748b;
            border-top: 1px solid #e2e8f0;
            padding-top: 5px;
        }
    }

    /* Usunięcie nagłówków i stopek ze strony tytułowej */
    @page :first {
        @top-left { content: none; border: none; }
        @top-right { content: none; border: none; }
        @bottom-left { content: none; border: none; }
        @bottom-right { content: none; border: none; }
    }

    /* Główne style typograficzne */
    body { 
        font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; 
        color: #1e293b; 
        line-height: 1.6; 
        font-size: 11pt;
        text-align: justify;
    }

    /* Strona tytułowa */
    .cover-page {
        text-align: center;
        margin-top: 30vh;
        page-break-after: always;
    }
    .cover-title {
        font-size: 28pt;
        color: #0f172a;
        margin-bottom: 10px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .cover-subtitle {
        font-size: 16pt;
        color: #3b82f6;
        margin-bottom: 40px;
    }
    .cover-meta {
        font-size: 12pt;
        color: #64748b;
        border-top: 2px solid #e2e8f0;
        padding-top: 20px;
        width: 60%;
        margin: 0 auto;
    }

    /* Nagłówki w treści */
    h1 { 
        color: #0f172a; 
        border-bottom: 2px solid #2563eb; 
        padding-bottom: 8px; 
        font-size: 18pt; 
        margin-top: 1.5em; 
        page-break-after: avoid; /* Zapobiega zostawianiu nagłówka na końcu strony */
    }
    h2 { 
        color: #1e293b; 
        font-size: 14pt; 
        margin-top: 1.2em; 
        page-break-after: avoid; 
    }
    
    /* Elementy list i tekstu */
    /* Precyzyjna kontrola wcięcia list */
    ul, ol { 
        padding-left: 18px; 
        margin-left: 0; 
        margin-bottom: 1em; 
    }
    li { margin-bottom: 6px; }
    .text-gray { color: #64748b; font-style: italic; }
    
    /* Różne warianty odstępów dla list z kreatora */
    ul.spacing-compact li, ol.spacing-compact li { margin-bottom: 2px; }
    ul.spacing-relaxed li, ol.spacing-relaxed li { margin-bottom: 12px; }
</style>
"""

DOCUMENT_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    """ + DOCUMENT_STYLING + """
</head>
<body>
    <div class="cover-page">
        <div class="cover-title">{{ template_name }}</div>
        <div class="cover-subtitle">Baza Wiedzy Projektu</div>
        <div class="cover-meta">
            <p><strong>Projekt:</strong> {{ project_name }}</p>
            <p><strong>Data wygenerowania:</strong> {{ date }}</p>
        </div>
    </div>
    {{ body_content }}
</body>
</html>
"""