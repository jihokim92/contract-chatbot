# utils/parser.py
import fitz  # PyMuPDF
import re

def extract_clauses_from_pdf(file_path):
    doc = fitz.open(file_path)
    full_text = ""
    
    # 전체 텍스트 추출
    for page in doc:
        page_text = page.get_text()
        full_text += page_text + "\n"

    # 정규표현식: 조항 헤더 추출 (예: "1.", "1.1", "2.3.4" 등)
    clause_pattern = re.compile(r"(?P<header>(\d+(\.\d+)*))\s+(?P<body>.+)")
    
    # 결과 리스트
    clauses = []

    # 현재 조항 추적
    current_clause = None

    for line in full_text.splitlines():
        line = line.strip()
        if not line:
            continue

        match = clause_pattern.match(line)
        if match:
            # 새 조항 시작
            if current_clause:
                clauses.append(current_clause)
            current_clause = {
                "section": match.group("header"),
                "text": match.group("body")
            }
        elif current_clause:
            # 현재 조항에 이어붙이기
            current_clause["text"] += " " + line

    # 마지막 조항 추가
    if current_clause:
        clauses.append(current_clause)

    return clauses
