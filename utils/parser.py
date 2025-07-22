from PyPDF2 import PdfReader

def extract_clauses_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
    sections = full_text.split("\n\n")
    
    clauses = [
        {"section": f"Clause {i+1}", "text": section.strip()}
        for i, section in enumerate(sections) if section.strip()
    ]
    
    return clauses 