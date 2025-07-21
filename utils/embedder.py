# utils/embedder.py
import os
import openai
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI

# .env 파일 로드 (로컬 실행 시)
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 텍스트 → 벡터 임베딩 저장
def initialize_vector_store(clauses):
    texts = [c['text'] for c in clauses]
    metadatas = [{"section": c["section"]} for c in clauses]

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.create_documents(texts, metadatas=metadatas)

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)

    # 참고용 원본 clause도 저장
    vectorstore.index_to_docstore_id = {i: i for i in range(len(docs))}
    vectorstore.docstore._dict = {i: doc for i, doc in enumerate(docs)}
    vectorstore.source_clauses = clauses

    return vectorstore

# 유사 문서 검색 후 QnA
def query_contract(query, role, vectorstore):
    # 질의어에 역할을 반영
    prompt = f"당사는 '{role}'입니다. 아래 질문에 계약서 내용을 바탕으로 답변해주세요:\n\n{query}"
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    docs = retriever.get_relevant_documents(prompt)

    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
    chain = load_qa_chain(llm, chain_type="stuff")
    result = chain.run(input_documents=docs, question=prompt)
    return result
