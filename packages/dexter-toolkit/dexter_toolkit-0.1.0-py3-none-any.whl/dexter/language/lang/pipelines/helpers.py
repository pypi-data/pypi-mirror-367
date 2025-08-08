

def load_documents(pdf_paths: list) -> list:
    """
    Load and return documents from multiple PDF files.
    """
    documents = []
    for pdf_path in pdf_paths:
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
    return documents