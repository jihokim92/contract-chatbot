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
    page_title="📋 계약서 검토 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Clean, minimal CSS
st.markdown("""
<style>
    /* Reset and base styles */
    .main {
        padding: 2rem;
        background: #fafafa;
    }
    
    /* Header */
    .header {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        text-align: center;
        border-left: 4px solid #2563eb;
    }
    
    .header h1 {
        color: #1f2937;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        color: #6b7280;
        font-size: 1.1rem;
        margin: 0;
    }
    
    /* Mode selector */
    .mode-selector {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .mode-title {
        color: #1f2937;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .mode-buttons {
        display: flex;
        gap: 1rem;
    }
    
    .mode-btn {
        flex: 1;
        padding: 1rem;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        background: white;
        color: #6b7280;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
    }
    
    .mode-btn:hover {
        border-color: #2563eb;
        color: #2563eb;
    }
    
    .mode-btn.active {
        border-color: #2563eb;
        background: #eff6ff;
        color: #2563eb;
    }
    
    .current-mode {
        background: #f0f9ff;
        border: 1px solid #0ea5e9;
        color: #0369a1;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Content containers */
    .content-box {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .content-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid #f3f4f6;
        padding-bottom: 0.5rem;
    }
    
    /* Status indicators */
    .status-success {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #166534;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-info {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1e40af;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-warning {
        background: #fffbeb;
        border: 1px solid #fed7aa;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Progress steps */
    .progress-container {
        background: #f9fafb;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        background: white;
        border-left: 3px solid #d1d5db;
    }
    
    .progress-step.completed {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    .progress-step.pending {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    /* Category display */
    .category-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #10b981;
    }
    
    .category-title {
        color: #065f46;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .clause-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .clause-number {
        color: #2563eb;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f3f4f6;
    }
    
    .text-block {
        margin: 0.8rem 0;
        padding: 0.8rem;
        border-radius: 6px;
        border-left: 3px solid #d1d5db;
    }
    
    .text-original {
        background: #f9fafb;
        border-left-color: #6b7280;
    }
    
    .text-translated {
        background: #f0fdf4;
        border-left-color: #10b981;
    }
    
    .text-label {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        color: #374151;
    }
    
    /* Buttons */
    .primary-btn {
        background: #2563eb;
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
        margin: 1rem 0;
    }
    
    .primary-btn:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }
    
    .primary-btn:disabled {
        background: #9ca3af;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Analysis result */
    .analysis-result {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #2563eb;
    }
    
    /* Hide Streamlit elements */
    .stButton > button {
        width: 100%;
    }
    
    .stDownloadButton > button {
        width: 100%;
    }
    
    /* Debug info */
    .debug-info {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        color: #92400e;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'review_mode' not in st.session_state:
    st.session_state.review_mode = "standalone"
if 'target_contract' not in st.session_state:
    st.session_state.target_contract = None
if 'reference_contract' not in st.session_state:
    st.session_state.reference_contract = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = []

# Main header
st.markdown("""
<div class="header">
    <h1>📋 계약서 검토 시스템</h1>
    <p>🔒 세션 기반 보안 | 🌍 다국어 지원 | 🤖 AI 분석</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for API key check
with st.sidebar:
    st.header("🔑 API 설정")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API 키 설정됨")
    else:
        st.error("❌ OpenAI API 키 필요")
        st.info("Streamlit Secrets에서 OPENAI_API_KEY 설정")

# Mode selection
st.markdown("""
<div class="mode-selector">
    <div class="mode-title">🎯 검토 모드 선택</div>
    <div class="mode-buttons">
        <div class="mode-btn" onclick="document.querySelector('#mode1').click()">
            🔍 단독 검토<br><small>계약서 하나만 분석</small>
        </div>
        <div class="mode-btn" onclick="document.querySelector('#mode2').click()">
            📚 비교 검토<br><small>두 계약서 비교 분석</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Mode selection buttons (hidden)
col1, col2 = st.columns(2)
with col1:
    if st.button("Mode 1", key="mode1", help="단독 검토 모드"):
        st.session_state.review_mode = "standalone"
        st.session_state.processing_complete = False
        st.session_state.analysis_result = None
        st.session_state.debug_info = []
        st.rerun()

with col2:
    if st.button("Mode 2", key="mode2", help="비교 검토 모드"):
        st.session_state.review_mode = "comparison"
        st.session_state.processing_complete = False
        st.session_state.analysis_result = None
        st.session_state.debug_info = []
        st.rerun()

# Display current mode
current_mode = "단독 검토" if st.session_state.review_mode == "standalone" else "비교 검토"
st.markdown(f"""
<div class="current-mode">
    🎯 현재 모드: {current_mode}
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown("""
<div class="content-box">
    <div class="content-title">📄 계약서 업로드</div>
""", unsafe_allow_html=True)

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
                    "translated_text": None
                })
            else:
                extracted_clauses.append({
                    "number": f"Clause {i+1}",
                    "text": clause,
                    "translated_text": None
                })
    
    return extracted_clauses

def translate_clause_to_korean(text, client):
    """개별 조항을 한국어로 번역"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 전문 번역가입니다. 계약서 조항을 자연스러운 한국어로 번역해주세요."},
                {"role": "user", "content": f"다음 계약서 조항을 한국어로 번역해주세요:\n\n{text[:1000]}"}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"번역 오류: {str(e)}"

def categorize_clauses(clauses, client):
    """조항들을 카테고리별로 분류"""
    try:
        # 모든 조항 텍스트를 하나로 합치기
        all_clauses_text = "\n\n".join([f"{clause['number']}: {clause['text'][:200]}" for clause in clauses[:10]])
        
        prompt = f"""
다음 계약서 조항들을 카테고리별로 분류해주세요:

{all_clauses_text}

다음 카테고리로 분류해주세요:
1. 계약 목적 및 범위
2. 당사자 권리와 의무
3. 정산 및 지급 조건
4. 지적재산권
5. 기밀유지
6. 계약 해지
7. 책임 및 면책
8. 분쟁해결
9. 기타

JSON 형태로 응답해주세요:
{{
    "categories": {{
        "계약 목적 및 범위": ["조항번호"],
        "당사자 권리와 의무": ["조항번호"],
        "정산 및 지급 조건": ["조항번호"],
        "지적재산권": ["조항번호"],
        "기밀유지": ["조항번호"],
        "계약 해지": ["조항번호"],
        "책임 및 면책": ["조항번호"],
        "분쟁해결": ["조항번호"],
        "기타": ["조항번호"]
    }}
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 계약서 분석 전문가입니다. 조항들을 정확하게 카테고리별로 분류해주세요."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        st.session_state.debug_info.append(f"GPT 응답: {result[:200]}...")
        
        # JSON 파싱 시도
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                categorized = json.loads(json_str)
                st.session_state.debug_info.append(f"JSON 파싱 성공: {len(categorized.get('categories', {}))}개 카테고리")
                return categorized
        except Exception as e:
            st.session_state.debug_info.append(f"JSON 파싱 실패: {str(e)}")
        
        # 기본 분류
        default_categories = {
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
        
        # 기본 분류 로직: 첫 번째 조항을 "계약 목적 및 범위"에 넣기
        if clauses:
            default_categories["categories"]["계약 목적 및 범위"].append(clauses[0]["number"])
            st.session_state.debug_info.append(f"기본 분류: {clauses[0]['number']}을 계약 목적에 추가")
        
        return default_categories
        
    except Exception as e:
        st.session_state.debug_info.append(f"카테고리 분류 오류: {str(e)}")
        return None

# Target contract upload
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
        "categorized_clauses": None
    }
    
    if st.session_state.target_contract["text"]:
        st.session_state.target_contract["clauses"] = extract_clauses_from_text(
            st.session_state.target_contract["text"]
        )
        
        st.markdown(f"""
        <div class="status-success">
            ✅ {target_file.name} 업로드 완료<br>
            📊 추출된 조항 수: {len(st.session_state.target_contract['clauses'])}
        </div>
        """, unsafe_allow_html=True)

# Reference contract upload (only for comparison mode)
if st.session_state.review_mode == "comparison":
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
            
            st.markdown(f"""
            <div class="status-success">
                ✅ {reference_file.name} 업로드 완료<br>
                📊 추출된 조항 수: {len(st.session_state.reference_contract['clauses'])}
            </div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Processing section
if st.session_state.target_contract and st.session_state.target_contract["text"]:
    st.markdown("""
    <div class="content-box">
        <div class="content-title">🚀 처리 및 분석</div>
    """, unsafe_allow_html=True)
    
    # Check if ready for processing
    ready_for_processing = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_processing = False
            st.markdown("""
            <div class="status-warning">
                ⚠️ 비교 검토를 위해서는 레퍼런스 계약서도 업로드해주세요.
            </div>
            """, unsafe_allow_html=True)
    
    if ready_for_processing:
        if st.button("🌍 번역 및 분류 시작", type="primary", use_container_width=True, disabled=st.session_state.processing_complete):
            with st.spinner("번역 및 카테고리 분류를 진행하고 있습니다..."):
                try:
                    client = openai.OpenAI()
                    
                    # 번역 및 카테고리 분류
                    clauses = st.session_state.target_contract["clauses"]
                    
                    # 각 조항 번역
                    for i, clause in enumerate(clauses[:5]):  # 최대 5개 조항만 번역
                        clause["translated_text"] = translate_clause_to_korean(clause["text"], client)
                        st.session_state.debug_info.append(f"조항 {clause['number']} 번역 완료")
                    
                    # 카테고리 분류
                    categorized = categorize_clauses(clauses, client)
                    st.session_state.target_contract["categorized_clauses"] = categorized
                    st.session_state.processing_complete = True
                    
                    st.markdown("""
                    <div class="status-success">
                        ✅ 번역 및 분류 완료!
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ 처리 중 오류가 발생했습니다: {str(e)}")
    
    # Display progress
    if st.session_state.target_contract:
        st.markdown("""
        <div class="progress-container">
            <h4>📋 처리 현황</h4>
        """, unsafe_allow_html=True)
        
        steps = [
            ("파일 업로드", True),
            ("조항 추출", bool(st.session_state.target_contract.get("clauses"))),
            ("번역 및 분류", st.session_state.processing_complete),
            ("AI 분석", bool(st.session_state.analysis_result))
        ]
        
        for step_name, completed in steps:
            status_class = "completed" if completed else "pending"
            icon = "✅" if completed else "⏳"
            st.markdown(f"""
            <div class="progress-step {status_class}">
                {icon} {step_name}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Debug information
if st.session_state.debug_info:
    with st.expander("🔍 디버그 정보", expanded=False):
        st.markdown("""
        <div class="debug-info">
        """, unsafe_allow_html=True)
        for info in st.session_state.debug_info:
            st.write(info)
        st.markdown("</div>", unsafe_allow_html=True)

# Display categorized clauses
if st.session_state.processing_complete and st.session_state.target_contract.get("categorized_clauses"):
    st.markdown("""
    <div class="content-box">
        <div class="content-title">📂 카테고리별 조항 분류</div>
    """, unsafe_allow_html=True)
    
    categorized = st.session_state.target_contract["categorized_clauses"]
    clauses_dict = {clause["number"]: clause for clause in st.session_state.target_contract["clauses"]}
    
    total_clauses = 0
    for category, clause_numbers in categorized["categories"].items():
        if clause_numbers:
            total_clauses += len(clause_numbers)
            st.markdown(f"""
            <div class="category-section">
                <div class="category-title">
                    📂 {category} ({len(clause_numbers)}개 조항)
                </div>
            """, unsafe_allow_html=True)
            
            for clause_num in clause_numbers:
                if clause_num in clauses_dict:
                    clause = clauses_dict[clause_num]
                    st.markdown(f"""
                    <div class="clause-card">
                        <div class="clause-number">{clause['number']}</div>
                        
                        <div class="text-block text-original">
                            <div class="text-label">🌍 원문:</div>
                            {clause['text'][:150]}{'...' if len(clause['text']) > 150 else ''}
                        </div>
                        
                        {f'''
                        <div class="text-block text-translated">
                            <div class="text-label">🇰🇷 한국어:</div>
                            {clause['translated_text'][:150]}{'...' if len(clause['translated_text']) > 150 else ''}
                        </div>
                        ''' if clause.get('translated_text') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    
    if total_clauses == 0:
        st.markdown("""
        <div class="status-warning">
            ⚠️ 분류된 조항이 없습니다. 디버그 정보를 확인해주세요.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Analysis section
if st.session_state.target_contract and st.session_state.target_contract["text"]:
    st.markdown("""
    <div class="content-box">
        <div class="content-title">🤖 AI 분석</div>
    """, unsafe_allow_html=True)
    
    # Check if ready for analysis
    ready_for_analysis = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_analysis = False
            st.markdown("""
            <div class="status-warning">
                ⚠️ 비교 검토를 위해서는 레퍼런스 계약서도 업로드해주세요.
            </div>
            """, unsafe_allow_html=True)
    
    if ready_for_analysis:
        if st.button("🚀 AI 분석 시작", type="primary", use_container_width=True):
            with st.spinner("AI가 계약서를 분석하고 있습니다..."):
                try:
                    # Prepare analysis prompt
                    if st.session_state.review_mode == "standalone":
                        prompt = f"""
다음 계약서를 전문적으로 분석해주세요:

계약서 내용:
{st.session_state.target_contract["text"][:6000]}

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
{st.session_state.target_contract["text"][:3000]}

[레퍼런스 계약서]
{st.session_state.reference_contract["text"][:3000]}

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
            <div class="analysis-result">
                <h4>📊 AI 분석 결과</h4>
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
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Security notice
st.markdown("""
<div class="content-box">
    <div class="content-title">🔒 보안 안내</div>
    <ul>
        <li>업로드된 모든 파일은 세션 종료 시 자동으로 삭제됩니다</li>
        <li>외부 저장소나 데이터베이스에 저장되지 않습니다</li>
        <li>분석 결과는 다운로드 후 안전한 곳에 보관하세요</li>
    </ul>
</div>
""", unsafe_allow_html=True) 