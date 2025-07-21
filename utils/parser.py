# utils/parser.py
from unstructured.partition.pdf import partition_pdf

def extract_clauses_from_pdf(pdf_path):
    elements = partition_pdf(filename=pdf_path)

    clauses = []
    current_clause = {"section": None, "text": ""}
    
    for el in elements:
        text = el.text.strip()
        if not text:
            continue

        # 조항 번호로 시작하는 경우 새로운 조항으로 인식
        if text[:10].strip().split(" ")[0].replace(".", "").isdigit():
            if current_clause["text"]:
                clauses.append(current_clause)
            current_clause = {
                "section": text.split(" ")[0],
                "text": text
            }
        else:
            current_clause["text"] += " " + text

    if current_clause["text"]:
        clauses.append(current_clause)

    return clauses
