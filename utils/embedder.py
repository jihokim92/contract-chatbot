# utils/embedder.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

import os

# ✅ 벡터스토어 초기화 함수
def initialize_vector_store(clauses):
    documents = [
        Document(
            page_content=clause["text"],
            metadata={"section": clause["section"]}
        )
        for clause in clauses
    ]
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(documents, embeddings)
    return {"db": db, "source_clauses": clauses}

# ✅ 사용자 질문에 대한 계약서 기반 응답 생성
def query_contract(question, role, index):
    db = index["db"]
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Role 기반 프롬프트 설정
    system_prompt = f"""
너는 계약서 해석을 도와주는 챗봇이야. 우리 회사는 계약에서 '{role}'의 입장이야.
항상 그 관점을 기준으로 해석해줘. 답변은 반드시 한국어로 해줘.
계약서 원문은 영어이고, 아래 내용을 기반으로 질문에 답변해줘.
"""

    # 챗봇 구성
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0.1),
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": {
            "input_variables": ["context", "question"],
            "template": f"{system_prompt}\n\n문서 내용:\n{{context}}\n\n질문:\n{{question}}\n\n답변:"
        }}
    )

    # 답변 생성
    answer = qa_chain.run(question)
    return answer
