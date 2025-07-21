# utils/parser.py

import fitz  # PyMuPDF
import re

def extract_clauses_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    # 정규표현식으로 조항 번호와 텍스트 추출
    raw_clauses = re.split(r"\n?\s*(\d{1,2}(?:\.\d{1,2})*)\s+", full_text)
    
    # 첫 항목은 문서 시작부분, 이후는 [조항번호, 텍스트, 조항번호, 텍스트, ...]
    clauses = []
    for i in range(1, len(raw_clauses) - 1, 2):
        section = raw_clauses[i].strip()
        text = raw_clauses[i + 1].strip()
        if text:  # 빈 텍스트 제거
            clauses.append({
                "section": section,
                "text": text
            })

    return clauses
