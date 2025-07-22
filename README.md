# 계약서 챗봇 (Contract Chatbot)

글로벌 파트너사와의 계약서를 분석하고 질의응답을 도와주는 AI 챗봇입니다.

## 기능

- PDF 계약서 업로드 및 텍스트 추출
- 계약 조항별 분석 및 벡터화
- Licensor/Licensee 입장별 맞춤 답변
- 한국어로 계약서 해석 제공

## 설치 및 실행

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. OpenAI API 키 설정:
`.env` 파일을 생성하고 다음 내용을 추가하세요:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. 애플리케이션 실행:
```bash
streamlit run app.py
```

## 사용법

1. 웹 브라우저에서 `http://localhost:8501` 접속
2. Licensor 또는 Licensee 역할 선택
3. PDF 계약서 파일 업로드
4. 계약서에 대한 질문 입력
5. AI 챗봇의 답변 확인

## 프로젝트 구조

```
contract-chatbot/
├── app.py              # 메인 Streamlit 애플리케이션
├── requirements.txt    # Python 패키지 의존성
├── .env               # 환경변수 (API 키 등)
├── utils/
│   ├── __init__.py
│   ├── parser.py      # PDF 파싱 모듈
│   └── embedder.py    # 벡터화 및 챗봇 모듈
└── README.md
```

## 기술 스택

- **Frontend**: Streamlit
- **AI/ML**: OpenAI GPT, LangChain
- **Vector Database**: FAISS
- **PDF Processing**: PyPDF2
- **Embeddings**: OpenAI Embeddings 