# 📄 app.py (임시 버전 for 디버깅)
import streamlit as st
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import os

# ✅ 임시 텍스트 데이터 (PDF 없이 강제 삽입)
clauses = [
    {"section": "1. LICENSE", "text": "Licensor grants Licensee a non-exclusive license to use the software."},
    {"section": "2. TERM", "text": "The agreement shall commence on the Effective Date and continue for 2 years."},
    {"section": "3. TERMINATION", "text": "Either party may terminate this Agreement for cause with prior notice."}
]

# ✅ 벡터스토어 초기화
documents = [Document(page_content=c["text"], metadata={"section": c["section"]}) for c in clauses]
embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(documents, embeddings)

# ✅ QnA 체인
retriever = db.as_retriever()
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(temperature=0.1),
    retriever=retriever,
    return_source_documents=True
)

# ✅ Streamlit UI
st.title("🔍 계약서 챗봇 (임시 테스트)")
user_q = st.text_input("질문을 입력하세요:")

if user_q:
    result = qa_chain.run(user_q)
    st.markdown("### 🤖 답변:")
    st.write(result)
