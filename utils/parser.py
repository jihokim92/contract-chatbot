# utils/parser.py
from PyPDF2 import PdfReader
import re

def extract_clauses_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    clause_pattern = re.compile(r"^\\d+(\\.\\d+)*\\s", re.MULTILINE)
    raw_clauses = re.split(clause_pattern, full_text)
    matches = clause_pattern.findall(full_text)

    clauses = []
    for i in range(len(matches)):
        clause = {
            "section": matches[i].strip(),
            "text": raw_clauses[i+1].strip() if i+1 < len(raw_clauses) else ""
        }
        clauses.append(clause)

    return clauses
