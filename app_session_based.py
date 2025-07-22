import streamlit as st
import tempfile
import os
import json
from datetime import datetime
import openai
from PyPDF2 import PdfReader
import re

# Page configuration
st.set_page_config(
    page_title="계약서 검토 시스템 (세션 기반)",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mode-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .file-upload-area {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        margin: 1rem 0;
    }
    .analysis-box {
        background: #e8f4fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .category-card {
        background: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .clause-item {
        background: #ffffff;
        padding: 0.8rem;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        margin: 0.3rem 0;
    }
    .original-text {
        background: #f5f5f5;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.9em;
        margin: 0.3rem 0;
    }
    .translated-text {
        background: #e8f5e8;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.9em;
        margin: 0.3rem 0;
        border-left: 3px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📋 계약서 검토 시스템 (세션 기반)</h1>
    <p>🔒 세션 종료 시 모든 데이터가 자동으로 삭제됩니다 | 🌍 다국어 지원</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("ℹ️ 사용법")
    st.markdown("""
    ### 📋 검토 모드 선택
    
    **🔍 Mode 1: 단독 검토**
    - 검토 대상 계약서만 업로드
    - GPT를 통한 원론적 분석
    - 조항별 카테고리 분류
    
    **📚 Mode 2: 비교 검토**
    - 검토 대상 + 레퍼런스 계약서
    - 기존 계약서와 비교 분석
    
    ### 🌍 다국어 지원
    - 영어, 한국어 등 모든 언어 지원
    - 한국어 번역 자동 제공
    - 원문과 번역문 동시 표시
    
    ### ⚠️ 보안 주의사항
    - 세션 종료 시 모든 파일 삭제
    - 외부 저장소 사용 안함
    - 임시 메모리만 사용
    """)
    
    # API Key check
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API 키 설정됨")
    else:
        st.error("❌ OpenAI API 키 필요")
        st.info("Streamlit Secrets에서 OPENAI_API_KEY 설정")

# Initialize session state
if 'review_mode' not in st.session_state:
    st.session_state.review_mode = "standalone"
if 'target_contract' not in st.session_state:
    st.session_state.target_contract = None
if 'reference_contract' not in st.session_state:
    st.session_state.reference_contract = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'categorized_clauses' not in st.session_state:
    st.session_state.categorized_clauses = None

# Mode selection
st.header("🎯 검토 모드 선택")
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 Mode 1: 단독 검토", use_container_width=True):
        st.session_state.review_mode = "standalone"
        st.session_state.analysis_result = None
        st.session_state.categorized_clauses = None
        st.rerun()

with col2:
    if st.button("📚 Mode 2: 비교 검토", use_container_width=True):
        st.session_state.review_mode = "comparison"
        st.session_state.analysis_result = None
        st.session_state.categorized_clauses = None
        st.rerun()

# Display current mode
if st.session_state.review_mode == "standalone":
    st.markdown("""
    <div class="mode-card">
        <h3>🔍 Mode 1: 단독 검토</h3>
        <p>검토 대상 계약서만 업로드하여 GPT를 통한 원론적 분석과 조항별 카테고리 분류를 진행합니다.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="mode-card">
        <h3>📚 Mode 2: 비교 검토</h3>
        <p>검토 대상 계약서와 레퍼런스 계약서를 비교하여 분석합니다.</p>
    </div>
    """, unsafe_allow_html=True)

# File upload section
st.header("📁 계약서 업로드")

def extract_text_from_pdf(pdf_file):
    """PDF에서 텍스트 추출"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"PDF 읽기 오류: {str(e)}")
        return None

def extract_clauses_from_text(text):
    """텍스트에서 조항 추출"""
    if not text:
        return []
    
    # 조항 패턴 매칭 (숫자. 로 시작하는 섹션)
    clauses = re.split(r'\n\s*(?=\d+\.)', text)
    extracted_clauses = []
    
    for i, clause in enumerate(clauses):
        clause = clause.strip()
        if clause and len(clause) > 20:  # 최소 길이 체크
            # 조항 번호 추출
            match = re.match(r'^(\d+\.?\s*)(.*)', clause, re.DOTALL)
            if match:
                clause_num = match.group(1).strip()
                clause_text = match.group(2).strip()
                extracted_clauses.append({
                    "number": clause_num,
                    "text": clause_text,
                    "summary": clause_text[:100] + "..." if len(clause_text) > 100 else clause_text
                })
            else:
                extracted_clauses.append({
                    "number": f"Clause {i+1}",
                    "text": clause,
                    "summary": clause[:100] + "..." if len(clause) > 100 else clause
                })
    
    return extracted_clauses

def translate_to_korean(text, client):
    """텍스트를 한국어로 번역"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 전문 번역가입니다. 주어진 텍스트를 자연스러운 한국어로 번역해주세요."},
                {"role": "user", "content": f"다음 텍스트를 한국어로 번역해주세요:\n\n{text[:3000]}"}
            ],
            max_tokens=1000,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"번역 오류: {str(e)}"

def categorize_clauses(clauses, client):
    """조항들을 카테고리별로 분류"""
    try:
        # 모든 조항 텍스트를 하나로 합치기
        all_clauses_text = "\n\n".join([f"{clause['number']}: {clause['text'][:500]}" for clause in clauses[:20]])  # 최대 20개 조항
        
        prompt = f"""
다음 계약서 조항들을 주요 카테고리별로 분류해주세요:

{all_clauses_text}

다음 카테고리 중에서 가장 적합한 것으로 분류해주세요:
1. 계약 목적 및 범위 (Purpose & Scope)
2. 당사자 권리와 의무 (Rights & Obligations)
3. 정산 및 지급 조건 (Payment & Settlement)
4. 지적재산권 (Intellectual Property)
5. 기밀유지 (Confidentiality)
6. 계약 해지 (Termination)
7. 책임 및 면책 (Liability & Indemnification)
8. 분쟁해결 (Dispute Resolution)
9. 기타 (Others)

JSON 형태로 응답해주세요:
{{
    "categories": {{
        "계약 목적 및 범위": [조항번호들],
        "당사자 권리와 의무": [조항번호들],
        "정산 및 지급 조건": [조항번호들],
        "지적재산권": [조항번호들],
        "기밀유지": [조항번호들],
        "계약 해지": [조항번호들],
        "책임 및 면책": [조항번호들],
        "분쟁해결": [조항번호들],
        "기타": [조항번호들]
    }}
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 계약서 분석 전문가입니다. 조항들을 정확하게 카테고리별로 분류해주세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        
        # JSON 파싱 시도
        try:
            # JSON 부분만 추출
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                categorized = json.loads(json_str)
                return categorized
        except:
            pass
        
        # JSON 파싱 실패 시 기본 분류
        return {
            "categories": {
                "계약 목적 및 범위": [],
                "당사자 권리와 의무": [],
                "정산 및 지급 조건": [],
                "지적재산권": [],
                "기밀유지": [],
                "계약 해지": [],
                "책임 및 면책": [],
                "분쟁해결": [],
                "기타": []
            }
        }
        
    except Exception as e:
        st.error(f"카테고리 분류 오류: {str(e)}")
        return None

# Target contract upload
st.subheader("📄 검토 대상 계약서")
target_file = st.file_uploader(
    "검토할 계약서를 업로드하세요",
    type=['pdf'],
    key="target_uploader"
)

if target_file:
    st.session_state.target_contract = {
        "file": target_file,
        "name": target_file.name,
        "text": extract_text_from_pdf(target_file),
        "clauses": None,
        "translated_text": None,
        "categorized_clauses": None
    }
    
    if st.session_state.target_contract["text"]:
        st.session_state.target_contract["clauses"] = extract_clauses_from_text(
            st.session_state.target_contract["text"]
        )
        
        st.success(f"✅ {target_file.name} 업로드 완료")
        st.info(f"📊 추출된 조항 수: {len(st.session_state.target_contract['clauses'])}")
        
        # 번역 및 카테고리 분류 버튼
        if st.button("🌍 번역 및 분류 시작", type="primary", use_container_width=True):
            with st.spinner("번역 및 카테고리 분류를 진행하고 있습니다..."):
                try:
                    client = openai.OpenAI()
                    
                    # 번역
                    translated = translate_to_korean(st.session_state.target_contract["text"], client)
                    st.session_state.target_contract["translated_text"] = translated
                    
                    # 카테고리 분류
                    categorized = categorize_clauses(st.session_state.target_contract["clauses"], client)
                    st.session_state.target_contract["categorized_clauses"] = categorized
                    
                    st.success("✅ 번역 및 분류 완료!")
                    
                except Exception as e:
                    st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")
        
        # 번역 결과 표시
        if st.session_state.target_contract.get("translated_text"):
            st.subheader("🌍 한국어 번역")
            with st.expander("📖 전체 번역 보기", expanded=False):
                st.markdown(st.session_state.target_contract["translated_text"])
        
        # 카테고리별 조항 표시
        if st.session_state.target_contract.get("categorized_clauses"):
            st.subheader("📋 카테고리별 조항 분류")
            
            categorized = st.session_state.target_contract["categorized_clauses"]
            clauses_dict = {clause["number"]: clause for clause in st.session_state.target_contract["clauses"]}
            
            for category, clause_numbers in categorized["categories"].items():
                if clause_numbers:  # 해당 카테고리에 조항이 있는 경우만 표시
                    st.markdown(f"""
                    <div class="category-card">
                        <h4>📂 {category}</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for clause_num in clause_numbers:
                        if clause_num in clauses_dict:
                            clause = clauses_dict[clause_num]
                            st.markdown(f"""
                            <div class="clause-item">
                                <strong>{clause['number']}</strong>
                                <div class="original-text">
                                    <strong>원문:</strong><br>
                                    {clause['text'][:300]}{'...' if len(clause['text']) > 300 else ''}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.divider()

# Reference contract upload (only for comparison mode)
if st.session_state.review_mode == "comparison":
    st.subheader("📚 레퍼런스 계약서")
    reference_file = st.file_uploader(
        "비교할 레퍼런스 계약서를 업로드하세요",
        type=['pdf'],
        key="reference_uploader"
    )
    
    if reference_file:
        st.session_state.reference_contract = {
            "file": reference_file,
            "name": reference_file.name,
            "text": extract_text_from_pdf(reference_file),
            "clauses": None
        }
        
        if st.session_state.reference_contract["text"]:
            st.session_state.reference_contract["clauses"] = extract_clauses_from_text(
                st.session_state.reference_contract["text"]
            )
            
            st.success(f"✅ {reference_file.name} 업로드 완료")
            st.info(f"📊 추출된 조항 수: {len(st.session_state.reference_contract['clauses'])}")

# Analysis section
if st.session_state.target_contract and st.session_state.target_contract["text"]:
    st.header("🤖 AI 분석")
    
    # Check if ready for analysis
    ready_for_analysis = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_analysis = False
            st.warning("⚠️ 비교 검토를 위해서는 레퍼런스 계약서도 업로드해주세요.")
    
    if ready_for_analysis:
        if st.button("🚀 분석 시작", type="primary", use_container_width=True):
            with st.spinner("AI가 계약서를 분석하고 있습니다..."):
                try:
                    # Prepare analysis prompt
                    if st.session_state.review_mode == "standalone":
                        prompt = f"""
다음 계약서를 전문적으로 분석해주세요:

계약서 내용:
{st.session_state.target_contract["text"][:8000]}  # Limit text length

다음 항목들을 중심으로 분석해주세요:
1. 계약의 주요 목적과 범위
2. 당사자의 권리와 의무
3. 책임과 보상 조항
4. 위험 요소와 주의사항
5. 개선이 필요한 조항들
6. 전반적인 평가 및 권고사항

한국어로 상세히 분석해주세요.
"""
                    else:  # comparison mode
                        prompt = f"""
다음 두 계약서를 비교 분석해주세요:

[검토 대상 계약서]
{st.session_state.target_contract["text"][:4000]}

[레퍼런스 계약서]
{st.session_state.reference_contract["text"][:4000]}

다음 항목들을 중심으로 비교 분석해주세요:
1. 주요 차이점과 유사점
2. 검토 대상 계약서의 장단점
3. 레퍼런스 대비 개선 필요 사항
4. 위험 요소 비교
5. 권고사항

한국어로 상세히 분석해주세요.
"""
                    
                    # Call OpenAI API
                    client = openai.OpenAI()
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "당신은 계약서 검토 전문가입니다. 정확하고 실용적인 분석을 제공해주세요."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=2000,
                        temperature=0.3
                    )
                    
                    st.session_state.analysis_result = response.choices[0].message.content
                    
                except Exception as e:
                    st.error(f"❌ 분석 중 오류가 발생했습니다: {str(e)}")
                    st.info("OpenAI API 키를 확인해주세요.")
        
        # Display analysis result
        if st.session_state.analysis_result:
            st.markdown("""
            <div class="analysis-box">
                <h3>📊 AI 분석 결과</h3>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.analysis_result)
            
            # Download analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_filename = f"계약서_분석_{timestamp}.txt"
            
            st.download_button(
                label="📥 분석 결과 다운로드",
                data=st.session_state.analysis_result,
                file_name=analysis_filename,
                mime="text/plain",
                use_container_width=True
            )

# Security notice
st.markdown("""
<div class="warning-box">
    <h4>🔒 보안 안내</h4>
    <ul>
        <li>업로드된 모든 파일은 세션 종료 시 자동으로 삭제됩니다</li>
        <li>외부 저장소나 데이터베이스에 저장되지 않습니다</li>
        <li>분석 결과는 다운로드 후 안전한 곳에 보관하세요</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Session info
with st.expander("ℹ️ 세션 정보"):
    st.write(f"현재 모드: {'단독 검토' if st.session_state.review_mode == 'standalone' else '비교 검토'}")
    st.write(f"검토 대상: {st.session_state.target_contract['name'] if st.session_state.target_contract else '없음'}")
    if st.session_state.review_mode == "comparison":
        st.write(f"레퍼런스: {st.session_state.reference_contract['name'] if st.session_state.reference_contract else '없음'}")
    st.write(f"번역 완료: {'예' if st.session_state.target_contract and st.session_state.target_contract.get('translated_text') else '아니오'}")
    st.write(f"분류 완료: {'예' if st.session_state.target_contract and st.session_state.target_contract.get('categorized_clauses') else '아니오'}")
    st.write(f"분석 완료: {'예' if st.session_state.analysis_result else '아니오'}") 