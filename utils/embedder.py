# utils/embedder.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

def initialize_vector_store(clauses):
    # ✅ 조항 중 텍스트가 있는 것만 필터링
    filtered_clauses = [
        clause for clause in clauses
        if clause.get("text") and clause["text"].strip()
    ]

    if not filtered_clauses:
        raise ValueError("❌ 유효한 조항이 없습니다. 계약서에서 텍스트가 추출되지 않았습니다.")

    documents = [
        Document(
            page_content=clause["text"].strip(),
            metadata={"section": clause["section"]}
        )
        for clause in filtered_clauses
    ]

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(documents, embeddings)
    return {"db": db, "source_clauses": filtered_clauses}

def query_contract(question, role, index):
    db = index["db"]
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    system_prompt = f"""
너는 계약서 해석을 도와주는 챗봇이야. 우리 회사는 계약에서 '{role}'의 입장이야.
항상 그 관점을 기준으로 해석해줘. 답변은 반드시 한국어로 해줘.
계약서 원문은 영어이고, 아래 내용을 기반으로 질문에 답변해줘.
"""

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=f"""{system_prompt}

문서 내용:
{{context}}

질문:
{{question}}

답변:"""
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0.1),
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain.run(question)
