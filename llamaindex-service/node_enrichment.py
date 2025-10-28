import re
from typing import Tuple, List
from llama_index.core.schema import BaseNode

HEADER_PATTERNS = [
    r"^\s*[A-Z]\.\s+.+",                 # "A. CZĘŚĆ OPISOWA"
    r"^\s*\d+(\.\d+)*\.\s+.+",          # "1. ", "4.2. ", "6.1.2. "
    r"^\s*[IVXLCDM]+\.\s+.+",           # "I. ", "VI. "
    r"^\s*[A-ZŻŹĆĄŚĘŁÓŃ][A-ZŻŹĆĄŚĘŁÓŃ\s\-]{5,}$",  # wiersz WIELKIMI
    r"^\s*Rozdział\s+\d+.+",            # "Rozdział 2 ..."
]

HEADER_RE = re.compile("|".join(HEADER_PATTERNS))

def detect_heading(lines: List[str]) -> Tuple[str, str]:
    """
    Returns (section, subsection). Simple heuristic:
    - section = first line compliant with the regex
    - subsection = next line, if looks like heading of lower tier
    """
    clean = [l.strip() for l in lines if l.strip()]
    section = ""
    subsection = ""
    for i, l in enumerate(clean[:5]): # We look at the beginning of the chunk
        if HEADER_RE.match(l):
            section = l
            # let's try to catch the subheading as the next significant line
            for l2 in clean[i+1:i+4]:
                if len(l2.split()) >= 2 and not HEADER_RE.match(l2) and len(l2) < 120:
                    subsection = l2
                    break
            break
        return section, subsection

def enrich_nodes_with_headings(nodes: List[BaseNode]) -> List[BaseNode]:
    for n in nodes:
        txt = n.get_content()
        lines = txt.splitlines()
        section, subsection = detect_heading(lines)
        if section:
            n.metadata["section"] = section
        if subsection:
            n.metadata["subsection"] = subsection
        # base fields, if nojne
        n.metadata.setdefault("file_name", n.metadata.get("file_path", n.metadata.get("doc_id")))
        # PyMuPDFReader: often gives "page_label" or "page_number"
        if "page_label" not in n.metadata:
            pg = n.metadata.get("page_number", None)
            if pg is not None:
                n.metadata["page_label"] = str(pg)
        return nodes

