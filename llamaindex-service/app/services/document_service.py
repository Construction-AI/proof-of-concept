from app.core.node_enrichment import enrich_nodes_with_headings
from app.core.structured_output import structure_output

def process_document(document: dict):
    nodes = document.get("nodes", [])
    enriched_nodes = enrich_nodes_with_headings(nodes)
    return structure_output(enriched_nodes)