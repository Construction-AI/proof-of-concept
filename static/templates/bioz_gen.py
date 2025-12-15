from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def create_tight_bioz_template():
    doc = Document()

    # --- 1. FUNKCJE POMOCNICZE DO FORMATOWANIA ---
    
    def remove_spacing(paragraph):
        """Ustawia odstępy przed i po akapicie na 0."""
        p_format = paragraph.paragraph_format
        p_format.space_before = Pt(0)
        p_format.space_after = Pt(0)
        # Opcjonalnie: ustawia interlinię na 1.0 (pojedynczą)
        p_format.line_spacing = 1.0 

    # --- 2. KONFIGURACJA STYLÓW ---
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    # Domyślny odstęp dla zwykłego tekstu (żeby nie był zbity)
    style.paragraph_format.space_after = Pt(6)

    # Nagłówki
    for level in range(1, 4):
        h_style = doc.styles[f'Heading {level}']
        h_style.font.name = 'Calibri Light'
        h_style.font.color.rgb = None
        h_style.font.bold = True
        if level == 1:
            h_style.font.size = Pt(16)
            h_style.paragraph_format.space_before = Pt(24)
            h_style.paragraph_format.space_after = Pt(12)

    # --- 3. STRONA TYTUŁOWA ---
    title = doc.add_heading('PLAN BEZPIECZEŃSTWA\nI OCHRONY ZDROWIA (BIOZ)', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph().paragraph_format.space_after = Pt(24)

    table_cover = doc.add_table(rows=0, cols=2)
    table_cover.autofit = False
    table_cover.columns[0].width = Cm(5)
    table_cover.columns[1].width = Cm(11)

    def add_cover_row(label, tag_value):
        row = table_cover.add_row()
        # Zerujemy odstępy w tabeli dla zwartości
        remove_spacing(row.cells[0].paragraphs[0])
        remove_spacing(row.cells[1].paragraphs[0])
        
        row.cells[0].paragraphs[0].add_run(label).bold = True
        row.cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        row.cells[1].paragraphs[0].add_run(f'{{{{ {tag_value} }}}}')
        return row

    add_cover_row('NAZWA OBIEKTU:', 'content.title_page.object_info.name')
    add_cover_row('ADRES INWESTYCJI:', 'content.title_page.object_info.address.zip_city')
    add_cover_row('INWESTOR:', 'content.title_page.investor.name')
    add_cover_row('ADRES INWESTORA:', 'content.title_page.investor.address')
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    add_cover_row('GENERALNY WYKONAWCA:', 'content.title_page.contractor.name')
    
    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    # Podpis
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sig.add_run('Opracował:').font.size = Pt(10)
    
    doc.add_paragraph('_' * 40).alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # --- 4. TREŚĆ DOKUMENTU ---

    # Sekcja 1
    doc.add_heading('1. CZĘŚĆ OPISOWA', level=1)
    doc.add_heading('1.1. Przedmiot inwestycji', level=2)
    doc.add_paragraph('{{ content.descriptive_part.scope_of_works.description }}')

    doc.add_heading('1.2. Uczestnicy procesu budowlanego', level=2)
    p = doc.add_paragraph()
    p.add_run('Kierownik Budowy: ').bold = True
    p.add_run('{{ content.title_page.site_manager.name }} ')
    
    # Warunek (Jinja) w jednej linii, aby uniknąć problemów z odstępami
    p.add_run('{% if content.title_page.site_manager.qualifications_number %}'
              '(nr upr.: {{ content.title_page.site_manager.qualifications_number }})'
              '{% else %}(brak danych o uprawnieniach){% endif %}')

    # --- SEKCJA Z LISTĄ (TUTAJ BYŁ PROBLEM) ---
    doc.add_heading('2. ZAKRES I KOLEJNOŚĆ ROBÓT', level=1)
    doc.add_paragraph('Przewiduje się następującą kolejność realizacji robót budowlanych:')

    # 1. Tag otwierający pętlę -> Zerujemy odstęp
    p_start = doc.add_paragraph("{% for stage in content.descriptive_part.scope_of_works.stages %}")
    remove_spacing(p_start)

    # 2. Element listy -> Zerujemy odstęp (lub ustawiamy na np. 2pt)
    # Używamy ręcznej numeracji loop.index
    p_item = doc.add_paragraph("{{ loop.index }}. {{ stage }}")
    remove_spacing(p_item)
    # Dodajemy mały odstęp tylko jeśli chcesz, np. 2 pkt:
    # p_item.paragraph_format.space_after = Pt(2)

    # 3. Tag zamykający pętlę -> Zerujemy odstęp
    p_end = doc.add_paragraph("{% endfor %}")
    remove_spacing(p_end)


    # Sekcja 3
    doc.add_heading('3. ZAGOSPODAROWANIE PLACU BUDOWY', level=1)
    doc.add_heading('3.1. Istniejące obiekty budowlane', level=2)
    doc.add_paragraph('{{ content.descriptive_part.existing_objects }}')

    doc.add_heading('3.2. Zagrożenia od infrastruktury technicznej', level=2)
    
    table_infra = doc.add_table(rows=1, cols=2)
    table_infra.style = 'Table Grid'
    hdr = table_infra.rows[0].cells
    hdr[0].text = 'Element infrastruktury'
    hdr[1].text = 'Opis / Zagrożenie'
    
    def add_infra_row(label, path):
        row = table_infra.add_row().cells
        remove_spacing(row[0].paragraphs[0])
        remove_spacing(row[1].paragraphs[0])
        row[0].text = label
        row[1].text = f"{{{{ {path} if {path} else 'Nie dotyczy' }}}}"

    add_infra_row('Linie energetyczne', 'content.descriptive_part.site_hazards.power_lines')
    add_infra_row('Instalacje podziemne', 'content.descriptive_part.site_hazards.underground_utilities')
    add_infra_row('Ruch drogowy', 'content.descriptive_part.site_hazards.traffic')

    # --- SEKCJA ZAGROŻEŃ (DRUGA LISTA) ---
    doc.add_heading('4. IDENTYFIKACJA ZAGROŻEŃ I ŚRODKI PROFILAKTYCZNE', level=1)
    doc.add_paragraph('Zidentyfikowane zagrożenia:')

    # Pętla zagrożeń - ten sam zabieg co wyżej
    p_h_start = doc.add_paragraph('{% for hazard in content.descriptive_part.work_hazards %}')
    remove_spacing(p_h_start)

    p_h_item = doc.add_paragraph('{{ hazard }}', style='List Bullet')
    p_h_item.paragraph_format.space_after = Pt(2) 
    
    p_h_end = doc.add_paragraph('{% endfor %}')
    remove_spacing(p_h_end)

    doc.add_heading('4.1. Szczegółowe instrukcje', level=2)
    
    # Bloki warunkowe
    # Wykopy
    p_if = doc.add_paragraph('{% if content.descriptive_part.preventive_measures.excavations %}')
    remove_spacing(p_if)
    
    doc.add_heading('Zabezpieczenie wykopów', level=3)
    doc.add_paragraph('{{ content.descriptive_part.preventive_measures.excavations }}')
    
    p_endif = doc.add_paragraph('{% endif %}')
    remove_spacing(p_endif)

    # (Analogicznie dla reszty bloków if/endif...)
    
    # --- 5. STRONA Z DEBUG INFORMACJAMI ---
    doc.add_page_break()
    doc.add_heading('INFORMACJE DEBUG / GENERACJI', level=1)
    debug_table = doc.add_table(rows=0, cols=2)
    debug_table.autofit = False
    debug_table.columns[0].width = Cm(6)
    debug_table.columns[1].width = Cm(10)

    def add_debug_row(label, value):
        row = debug_table.add_row()
        remove_spacing(row.cells[0].paragraphs[0])
        remove_spacing(row.cells[1].paragraphs[0])
        row.cells[0].paragraphs[0].add_run(label).bold = True
        row.cells[1].paragraphs[0].add_run(value)
        
    add_debug_row("Typ dokumentu: ", "{{ meta.document_type }}")
    add_debug_row("ID Firmy: ", "{{ meta.company_id }}")
    add_debug_row("ID Projektu: ", "{{ meta.project_id }}")
    add_debug_row("Autor: ", "{{ meta.author }}")
    add_debug_row("System Prompt: ", "{{ meta.system_instruction }}.")
    add_debug_row("Wersja: ", "{{ meta.version }}")
    add_debug_row("Język: ", "{{ meta.language }}")
    add_debug_row("Data utworzenia", "{{ meta.date_created }}")

    filename = 'health_and_safety_plan.docx'
    doc.save(filename)
    print(f"Wygenerowano zwarty szablon: {filename}")

if __name__ == "__main__":
    create_tight_bioz_template()