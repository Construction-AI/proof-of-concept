from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_cell_border(cell, **kwargs):
    """
    Funkcja pomocnicza do ustawiania obramowania komórek tabeli.
    Umożliwia tworzenie ładnych tabel z nagłówkami.
    """
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for key, value in kwargs.items():
        tcBorders = tcPr.first_child_found_in("w:tcBorders")
        if tcBorders is None:
            tcBorders = OxmlElement('w:tcBorders')
            tcPr.append(tcBorders)
        tag = 'w:{}'.format(key)
        element = OxmlElement(tag)
        element.set(qn('w:val'), value)
        element.set(qn('w:sz'), '4')
        element.set(qn('w:space'), '0')
        element.set(qn('w:color'), 'auto')
        tcBorders.append(element)

def create_professional_bioz_template():
    doc = Document()

    # --- KONFIGURACJA STYLÓW ---
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    
    # Styl nagłówków
    for level in range(1, 4):
        h_style = doc.styles[f'Heading {level}']
        h_style.font.name = 'Calibri Light'
        h_style.font.color.rgb = None # Czarny kolor
        h_style.font.bold = True
        if level == 1:
            h_style.font.size = Pt(16)
            h_style.paragraph_format.space_before = Pt(24)
        elif level == 2:
            h_style.font.size = Pt(14)

    # --- STRONA TYTUŁOWA ---
    # Nazwa dokumentu
    title = doc.add_heading('PLAN BEZPIECZEŃSTWA\nI OCHRONY ZDROWIA (BIOZ)', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph().paragraph_format.space_after = Pt(24)

    # Tabela na stronie tytułowej (bez krawędzi) dla wyrównania
    table_cover = doc.add_table(rows=0, cols=2)
    table_cover.autofit = False
    table_cover.columns[0].width = Cm(5)
    table_cover.columns[1].width = Cm(11)

    def add_cover_row(label, tag_value):
        row = table_cover.add_row()
        cell_label = row.cells[0]
        cell_val = row.cells[1]
        
        # Stylizacja etykiety
        p_label = cell_label.paragraphs[0]
        p_label.add_run(label).bold = True
        p_label.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Stylizacja wartości (z tagiem Jinja)
        p_val = cell_val.paragraphs[0]
        p_val.add_run(f'{{{{ {tag_value} }}}}')
        p_val.alignment = WD_ALIGN_PARAGRAPH.LEFT
        return row

    add_cover_row('NAZWA OBIEKTU:', 'content.title_page.object_info.name')
    # Adres łączony warunkowo
    add_cover_row('ADRES INWESTYCJI:', 'content.title_page.object_info.address.zip_city')
    # Można dodać ulicę jeśli istnieje w nowym wierszu lub po przecinku
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    add_cover_row('INWESTOR:', 'content.title_page.investor.name')
    add_cover_row('ADRES INWESTORA:', 'content.title_page.investor.address')

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_cover_row('GENERALNY WYKONAWCA:', 'content.title_page.contractor.name')
    
    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    # Sekcja podpisów na dole strony
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p_sig.add_run('Opracował:')
    run.font.size = Pt(10)
    
    doc.add_paragraph('_' * 40).alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth = doc.add_paragraph('{{ meta.author }}')
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.runs[0].font.size = Pt(10)

    doc.add_page_break()

    # --- TREŚĆ DOKUMENTU ---

    # 1. DANE INWESTYCJI
    doc.add_heading('1. CZĘŚĆ OPISOWA', level=1)
    
    doc.add_heading('1.1. Przedmiot inwestycji', level=2)
    doc.add_paragraph('{{ content.descriptive_part.scope_of_works.description }}')

    doc.add_heading('1.2. Uczestnicy procesu budowlanego', level=2)
    
    # Lista uczestników
    p = doc.add_paragraph()
    p.add_run('Kierownik Budowy: ').bold = True
    p.add_run('{{ content.title_page.site_manager.name }} ')
    # Warunkowe wyświetlanie uprawnień
    p.add_run('{% if content.title_page.site_manager.qualifications_number %}')
    p.add_run('(nr upr.: {{ content.title_page.site_manager.qualifications_number }})')
    p.add_run('{% else %}(brak danych o uprawnieniach){% endif %}')

    # 2. ZAKRES I ETAPY ROBÓT
    doc.add_heading('2. ZAKRES I KOLEJNOŚĆ ROBÓT', level=1)
    doc.add_paragraph('Przewiduje się następującą kolejność realizacji robót budowlanych:')

    # Pętla po etapach
    doc.add_paragraph('{% for stage in content.descriptive_part.scope_of_works.stages %}')
    p_stage = doc.add_paragraph('{{ stage }}', style='List Bullet')
    doc.add_paragraph('{% endfor %}')

    # 3. WARUNKI TERENOWE I ISTNIEJĄCE OBIEKTY
    doc.add_heading('3. ZAGOSPODAROWANIE PLACU BUDOWY', level=1)
    
    doc.add_heading('3.1. Istniejące obiekty budowlane', level=2)
    # Obsługa stringa lub listy w existing_objects
    doc.add_paragraph('{{ content.descriptive_part.existing_objects.items }}')

    doc.add_heading('3.2. Zagrożenia od infrastruktury technicznej', level=2)
    
    # Tabela zagrożeń infrastrukturalnych
    table_infra = doc.add_table(rows=1, cols=2)
    table_infra.style = 'Table Grid'
    hdr = table_infra.rows[0].cells
    hdr[0].text = 'Element infrastruktury'
    hdr[1].text = 'Opis / Zagrożenie'
    
    # Wiersze tabeli z warunkami
    def add_infra_row(label, path):
        row = table_infra.add_row().cells
        row[0].text = label
        # Jeśli null -> wpisz "Brak danych" lub obsłuż Jinją
        row[1].text = f"{{{{ {path} if {path} else 'Nie dotyczy/Brak danych' }}}}"

    add_infra_row('Linie energetyczne', 'content.descriptive_part.site_hazards.power_lines')
    add_infra_row('Instalacje podziemne', 'content.descriptive_part.site_hazards.underground_utilities')
    add_infra_row('Ruch drogowy', 'content.descriptive_part.site_hazards.traffic')

    # 4. ZAGROŻENIA I PROFILAKTYKA
    doc.add_heading('4. IDENTYFIKACJA ZAGROŻEŃ I ŚRODKI PROFILAKTYCZNE', level=1)

    doc.add_paragraph('Podczas realizacji inwestycji zidentyfikowano występowanie następujących zagrożeń dla bezpieczeństwa i zdrowia ludzi:')

    # Wyliczanie zagrożeń (work_hazards)
    doc.add_paragraph('{% for hazard in content.descriptive_part.work_hazards %}')
    doc.add_paragraph('{{ hazard }}', style='List Bullet')
    doc.add_paragraph('{% endfor %}')

    doc.add_heading('4.1. Szczegółowe instrukcje bezpiecznego wykonywania robót', level=2)
    
    # Dynamiczne sekcje dla środków zapobiegawczych
    # Wykopy
    p_exc = doc.add_paragraph('{% if content.descriptive_part.preventive_measures.excavations %}')
    doc.add_heading('Zabezpieczenie wykopów', level=3)
    doc.add_paragraph('{{ content.descriptive_part.preventive_measures.excavations }}')
    doc.add_paragraph('{% endif %}')

    # Praca na wysokości
    p_hei = doc.add_paragraph('{% if content.descriptive_part.preventive_measures.heights %}')
    doc.add_heading('Praca na wysokości', level=3)
    doc.add_paragraph('{{ content.descriptive_part.preventive_measures.heights }}')
    doc.add_paragraph('{% endif %}')

    # Maszyny
    p_mac = doc.add_paragraph('{% if content.descriptive_part.preventive_measures.machinery %}')
    doc.add_heading('Praca maszyn budowlanych', level=3)
    doc.add_paragraph('{{ content.descriptive_part.preventive_measures.machinery }}')
    doc.add_paragraph('{% endif %}')

    # Zapis
    filename = 'health_and_safety_plan.docx'
    doc.save(filename)
    print(f"Wygenerowano profesjonalny szablon: {filename}")

if __name__ == "__main__":
    create_professional_bioz_template()