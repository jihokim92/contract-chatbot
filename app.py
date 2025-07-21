# contract-chatbot/app.py
import streamlit as st
import tempfile
from utils.parser import extract_clauses_from_pdf
from utils.embedder import initialize_vector_store, query_contract

st.set_page_config(page_title="계약서 챗봇", layout="wide")
st.title("📄 계약서 분석 챗봇")

# 1. 역할 선택
role = st.radio("✅ 우리 역할은 무엇인가요?", ["Licensor", "Licensee"], horizontal=True)

# 2. 파일 업로드
uploaded_file = st.file_uploader("📂 계약서 PDF 업로드", type=["pdf"])

if uploaded_file:
    # 임시 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    st.success("✅ 계약서 업로드 완료. 조항을 분석 중입니다...")
    clauses = extract_clauses_from_pdf(tmp_path)

    # 벡터스토어 초기화
    index = initialize_vector_store(clauses)
    st.success("🧠 계약 조항 벡터화 완료!")

    # 사용자 질문 입력
    st.subheader("💬 계약서에 대해 질문해보세요:")
    user_q = st.text_input("질문 (예: 우리가 손해배상 책임지는 조항은 어디야?)", key="q")

    if user_q:
        with st.spinner("답변 생성 중..."):
            result = query_contract(user_q, role, index)
            st.markdown("---")
            st.markdown(f"#### 🤖 챗봇의 답변:")
            st.markdown(result)

        st.markdown("---")
        if st.checkbox("🔍 참고 조항 보기"):
            for clause in index['source_clauses']:  # source_clauses에 저장됨
                st.markdown(f"**{clause['section']}** {clause['text'][:300]}...")
