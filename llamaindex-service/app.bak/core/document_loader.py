from pathlib import Path
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import SimpleDirectoryReader

def load_documents_with_metadata(input_dir: str):
    """
    Ładuje dokumenty. Dla PDF używa PyMuPDFReader (strona=>osobny Document),
    dzięki czemu w metadata mamy 'file_name' i 'page_label'.
    """
    reader = SimpleDirectoryReader(
        input_dir=input_dir,
        recursive=True,
        filename_as_id=False,
        file_extractor={".pdf": PyMuPDFReader()},
    )
    docs = reader.load_data()
    # Upewnijmy się, że mamy przydatne metadane
    for d in docs:
        d.metadata.setdefault("file_name", Path(d.metadata.get("file_path", d.doc_id)).name)
        d.metadata.setdefault("page_label", d.metadata.get("source", None))
    return docs