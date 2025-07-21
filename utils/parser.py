# utils/parser.py
import fitz  # PyMuPDF
import re

def extract_clauses_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()

    # 정규표현식으로 조항 파싱 (예: 1. ~ / 1.1 ~ / 2. ~)
    pattern = re.compile(r"(?P<section>\d{1,2}(?:\.\d{1,2})?)\s+(?P<text>.+?)(?=\n\d{1,2}(?:\.\d{1,2})?\s+|$)", re.DOTALL)
    matches = pattern.finditer(text)

    clauses = []
    for match in matches:
        section = match.group("section").strip()
        clause_text = match.group("text").strip().replace("\n", " ")
        if clause_text:  # 빈 문자열 거르기
            clauses.append({
                "section": section,
                "text": clause_text
            })

    return clauses
