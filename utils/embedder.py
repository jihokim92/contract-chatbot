# utils/embedder.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

def initialize_vector_store(clauses):
    # 비어있는 조항 제거
    documents = []
    for clause in clauses:
        text = clause.get("text", "").strip()
        if text:
            documents.append(
                Document(
                    page_content=text,
                    metadata={"section": clause.get("section", "N/A")}
                )
            )
    
    if not documents:
        raise ValueError("❗ 벡터화할 문서가 없습니다. PDF에서 텍스트를 제대로 추출하지 못했을 수 있습니다.")
    
    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(documents, embeddings)
    
    return {"db": db, "source_clauses": clauses}

def query_contract(question, role, index):
    db = index["db"]
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    
    system_prompt = f"""
    너는 계약서를 해석해주는 법률비서 챗봇이야. 우리 회사는 '{role}'의 입장이야.
    
    계약서 원문은 영어이며, 답변은 반드시 한국어로 해줘.
    
    다음 문서 내용을 바탕으로 질문에 답해줘:
    """
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=system_prompt + "\n\n문서 내용:\n{context}\n\n질문:\n{question}\n\n답변:"
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(temperature=0.1),
        retriever=retriever,
        return_source_documents=False,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa_chain.run(question) 