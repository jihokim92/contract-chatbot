import streamlit as st
import tempfile
import os
import json
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="계약서 검토 시스템", layout="wide")

st.title("📋 계약서 검토 시스템")

# 세션 상태 초기화
if 'contracts_db' not in st.session_state:
    st.session_state.contracts_db = []
if 'current_contract' not in st.session_state:
    st.session_state.current_contract = None

# 사이드바
with st.sidebar:
    st.header("📚 시스템 메뉴")
    
    # API 키 상태 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API 키 설정됨")
    else:
        st.error("❌ OpenAI API 키 필요")
    
    menu = st.selectbox(
        "메뉴 선택",
        ["🏠 대시보드", "📖 기존 계약서 관리", "🔍 계약서 검토", "❓ 기존 계약서 질의"]
    )

# 대시보드
if menu == "🏠 대시보드":
    st.header("📊 시스템 현황")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("저장된 계약서", len(st.session_state.contracts_db))
    
    with col2:
        st.metric("총 조항 수", sum(len(contract.get('clauses', [])) for contract in st.session_state.contracts_db))
    
    with col3:
        st.metric("시스템 상태", "정상" if api_key else "API 키 필요")
    
    # 최근 업로드된 계약서
    if st.session_state.contracts_db:
        st.subheader("📋 최근 업로드된 계약서")
        for contract in st.session_state.contracts_db[-3:]:
            with st.expander(f"📄 {contract.get('title', '제목 없음')} - {contract.get('upload_date', '날짜 없음')}"):
                st.write(f"**파트너사:** {contract.get('partner', 'N/A')}")
                st.write(f"**조항 수:** {len(contract.get('clauses', []))}")
                st.write(f"**계약 유형:** {contract.get('type', 'N/A')}")

# 기존 계약서 관리
elif menu == "📖 기존 계약서 관리":
    st.header("📖 기존 계약서 학습")
    
    st.info("💡 검토가 완료된 계약서를 업로드하여 지식베이스에 추가합니다.")
    
    with st.form("contract_upload"):
        uploaded_file = st.file_uploader("📂 계약서 PDF 업로드", type=["pdf"])
        
        col1, col2 = st.columns(2)
        with col1:
            contract_title = st.text_input("계약서 제목")
            partner_name = st.text_input("파트너사명")
        
        with col2:
            contract_type = st.selectbox("계약 유형", ["라이선스", "NDA", "서비스", "구매", "기타"])
            upload_date = st.date_input("업로드 날짜", datetime.now())
        
        submit_button = st.form_submit_button("📚 지식베이스에 추가")
        
        if submit_button and uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                pdf_path = tmp.name
            
            try:
                # PDF 파싱
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                
                # 조항 분리 (개선된 로직)
                import re
                clauses = []
                
                # 숫자로 시작하는 섹션 찾기
                sections = re.split(r'\n\s*(?=\d+\.)', full_text)
                
                for i, section in enumerate(sections):
                    section = section.strip()
                    if section and len(section) > 20:
                        # 섹션 번호 추출
                        section_match = re.match(r'^(\d+\.?\s*)(.*)', section, re.DOTALL)
                        if section_match:
                            clause_num = section_match.group(1).strip()
                            clause_text = section_match.group(2).strip()
                            clauses.append({
                                "number": clause_num,
                                "text": clause_text,
                                "type": "조항"
                            })
                        else:
                            clauses.append({
                                "number": f"Section {i+1}",
                                "text": section,
                                "type": "섹션"
                            })
                
                # 계약서 정보 저장
                contract_data = {
                    "title": contract_title or uploaded_file.name,
                    "partner": partner_name,
                    "type": contract_type,
                    "upload_date": upload_date.strftime("%Y-%m-%d"),
                    "clauses": clauses,
                    "full_text": full_text[:5000],  # 전체 텍스트 일부만 저장
                    "file_name": uploaded_file.name
                }
                
                st.session_state.contracts_db.append(contract_data)
                
                st.success(f"✅ '{contract_title}' 계약서가 성공적으로 추가되었습니다!")
                st.info(f"📊 총 {len(clauses)}개의 조항이 추출되었습니다.")
                
                # 조항 미리보기
                with st.expander("🔍 추출된 조항 미리보기"):
                    for clause in clauses[:5]:
                        st.markdown(f"**{clause['number']}**")
                        st.text(clause['text'][:200] + "..." if len(clause['text']) > 200 else clause['text'])
                        st.divider()
                
            except Exception as e:
                st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")
            
            finally:
                try:
                    os.unlink(pdf_path)
                except:
                    pass

# 계약서 검토
elif menu == "🔍 계약서 검토":
    st.header("🔍 신규 계약서 검토")
    
    if not st.session_state.contracts_db:
        st.warning("⚠️ 먼저 기존 계약서를 업로드해주세요.")
        st.info("📖 '기존 계약서 관리' 메뉴에서 계약서를 추가하세요.")
    else:
        st.info("💡 새로운 계약서를 업로드하면 기존 지식베이스와 비교하여 검토 의견을 제공합니다.")
        
        uploaded_file = st.file_uploader("📂 검토할 계약서 PDF 업로드", type=["pdf"])
        
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                pdf_path = tmp.name
            
            try:
                # PDF 파싱
                from PyPDF2 import PdfReader
                reader = PdfReader(pdf_path)
                full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                
                st.success("✅ 계약서 분석을 시작합니다...")
                
                # AI 검토 함수
                def ai_contract_review(new_text, existing_contracts):
                    try:
                        import openai
                        
                        # 기존 계약서 요약
                        existing_summary = ""
                        for contract in existing_contracts[:3]:  # 최근 3개만 사용
                            existing_summary += f"\n- {contract['title']} ({contract['partner']}): {len(contract['clauses'])}개 조항"
                        
                        prompt = f"""
당신은 계약서 검토 전문가입니다. 새로운 계약서를 기존 계약서들과 비교하여 검토해주세요.

**기존 계약서 정보:**
{existing_summary}

**새로운 계약서 내용:**
{new_text[:3000]}

다음 항목별로 검토 의견을 제공해주세요:

1. **전체적인 위험도 평가** (낮음/보통/높음)
2. **주요 조항별 분석** (책임/의무, R/S 구조, 보상 등)
3. **기존 계약서와의 차이점**
4. **개선 제안사항**
5. **특별 주의사항**

답변은 한국어로 작성하고, 구체적이고 실용적인 의견을 제공해주세요.
                        """
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "당신은 계약서 검토 전문가입니다."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=1000,
                            temperature=0.1
                        )
                        
                        return response.choices[0].message.content
                        
                    except Exception as e:
                        return f"❌ AI 검토 중 오류가 발생했습니다: {str(e)}"
                
                # AI 검토 실행
                with st.spinner("🤖 AI가 계약서를 검토하고 있습니다..."):
                    review_result = ai_contract_review(full_text, st.session_state.contracts_db)
                
                st.markdown("## 📋 AI 검토 결과")
                st.markdown(review_result)
                
                # 조항별 상세 분석
                st.subheader("🔍 조항별 상세 분석")
                
                # 조항 분리
                import re
                sections = re.split(r'\n\s*(?=\d+\.)', full_text)
                clauses = []
                
                for i, section in enumerate(sections):
                    section = section.strip()
                    if section and len(section) > 20:
                        section_match = re.match(r'^(\d+\.?\s*)(.*)', section, re.DOTALL)
                        if section_match:
                            clause_num = section_match.group(1).strip()
                            clause_text = section_match.group(2).strip()
                            clauses.append({
                                "number": clause_num,
                                "text": clause_text
                            })
                
                # 조항별 분석
                for clause in clauses[:10]:  # 처음 10개 조항만
                    with st.expander(f"📄 조항 {clause['number']}"):
                        st.text(clause['text'][:300] + "..." if len(clause['text']) > 300 else clause['text'])
                        
                        # 조항별 AI 분석
                        def analyze_clause(clause_text):
                            try:
                                import openai
                                
                                prompt = f"""
다음 계약 조항을 분석해주세요:

{clause_text[:500]}

다음 항목별로 간단히 분석해주세요:
- **조항 유형**: (책임/의무, 권리, 보상, 기타)
- **위험도**: (낮음/보통/높음)
- **주의사항**: 간단한 의견
                                """
                                
                                response = openai.ChatCompletion.create(
                                    model="gpt-3.5-turbo",
                                    messages=[
                                        {"role": "system", "content": "계약 조항 분석 전문가입니다."},
                                        {"role": "user", "content": prompt}
                                    ],
                                    max_tokens=200,
                                    temperature=0.1
                                )
                                
                                return response.choices[0].message.content
                                
                            except Exception as e:
                                return f"분석 중 오류: {str(e)}"
                        
                        if st.button(f"분석", key=f"analyze_{clause['number']}"):
                            with st.spinner("분석 중..."):
                                analysis = analyze_clause(clause['text'])
                                st.markdown(analysis)
            
            except Exception as e:
                st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")
            
            finally:
                try:
                    os.unlink(pdf_path)
                except:
                    pass

# 기존 계약서 질의
elif menu == "❓ 기존 계약서 질의":
    st.header("❓ 기존 계약서 질의")
    
    if not st.session_state.contracts_db:
        st.warning("⚠️ 저장된 계약서가 없습니다.")
        st.info("📖 '기존 계약서 관리' 메뉴에서 계약서를 추가하세요.")
    else:
        st.info("💡 저장된 계약서들에 대해 질문하세요.")
        
        # 계약서 선택
        contract_options = [f"{c['title']} ({c['partner']})" for c in st.session_state.contracts_db]
        selected_contract = st.selectbox("계약서 선택", contract_options)
        
        if selected_contract:
            # 선택된 계약서 찾기
            contract_idx = contract_options.index(selected_contract)
            contract = st.session_state.contracts_db[contract_idx]
            
            st.write(f"**파트너사:** {contract['partner']}")
            st.write(f"**계약 유형:** {contract['type']}")
            st.write(f"**조항 수:** {len(contract['clauses'])}")
            
            # 질문 입력
            question = st.text_input("질문을 입력하세요", placeholder="예: 우리의 책임과 의무는 무엇인가요?")
            
            if question:
                # AI 질의응답
                def answer_question(question, contract_data):
                    try:
                        import openai
                        
                        prompt = f"""
다음 계약서에 대한 질문에 답변해주세요:

**계약서 정보:**
- 제목: {contract_data['title']}
- 파트너사: {contract_data['partner']}
- 계약 유형: {contract_data['type']}

**계약서 내용:**
{contract_data['full_text'][:2000]}

**질문:** {question}

계약서 내용을 바탕으로 구체적이고 정확한 답변을 한국어로 제공해주세요.
                        """
                        
                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system", "content": "계약서 분석 전문가입니다."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=500,
                            temperature=0.1
                        )
                        
                        return response.choices[0].message.content
                        
                    except Exception as e:
                        return f"❌ 답변 생성 중 오류가 발생했습니다: {str(e)}"
                
                with st.spinner("🤖 답변을 생성하고 있습니다..."):
                    answer = answer_question(question, contract)
                
                st.markdown("### 🤖 AI 답변")
                st.markdown(answer)
                
                # 관련 조항 표시
                st.subheader("📋 관련 조항")
                keywords = question.lower().split()
                relevant_clauses = []
                
                for clause in contract['clauses']:
                    if any(keyword in clause['text'].lower() for keyword in keywords):
                        relevant_clauses.append(clause)
                
                if relevant_clauses:
                    for clause in relevant_clauses[:3]:
                        with st.expander(f"조항 {clause['number']}"):
                            st.text(clause['text'])
                else:
                    st.info("관련 조항을 찾을 수 없습니다.")

st.info("🔧 이 시스템은 기존 계약서를 학습하여 새로운 계약서 검토를 도와줍니다.")
