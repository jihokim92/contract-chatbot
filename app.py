import streamlit as st
import tempfile
from utils.parser import extract_clauses_from_pdf
from utils.embedder import initialize_vector_store, query_contract

st.set_page_config(page_title="계약서 챗봇", layout="wide")

st.title("📄 계약서 기반 Q&A 챗봇")

role = st.radio("✅ 우리 역할은 무엇인가요?", ["Licensor", "Licensee"], horizontal=True)

uploaded_file = st.file_uploader("📂 계약서 PDF 업로드", type=["pdf"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        pdf_path = tmp.name
    
    st.success("✅ 계약서 업로드 완료. 조항을 분석 중입니다...")
    
    clauses = extract_clauses_from_pdf(pdf_path)
    
    if len(clauses) == 0:
        st.error("❌ 파싱된 조항이 없습니다. PDF 내용을 확인해주세요.")
    else:
        index = initialize_vector_store(clauses)
        st.success("🧠 계약 조항 벡터화 완료!")
        
        st.subheader("💬 계약서에 대해 질문해보세요:")
        question = st.text_input("예: 우리가 손해배상 책임지는 조항은 어디야?", key="q")
        
        if question:
            with st.spinner("답변 생성 중..."):
                answer = query_contract(question, role, index)
                st.markdown("#### 🤖 챗봇의 답변:")
                st.markdown(answer)
        
        if st.checkbox("🔍 참고 조항 보기"):
            for clause in index["source_clauses"][:5]:
                st.markdown(f"**{clause['section']}**\n\n{clause['text'][:300]}...") 