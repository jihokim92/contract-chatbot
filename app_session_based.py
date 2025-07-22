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

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main container */
    .main-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    /* Header */
    .main-header {
        text-align: center;
        color: white;
        margin-bottom: 1rem;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Mode cards */
    .mode-container {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .mode-card {
        flex: 1;
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 3px solid transparent;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .mode-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .mode-card.active {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8f0ff 100%);
    }
    
    .mode-card h3 {
        color: #333;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .mode-card p {
        color: #666;
        font-size: 0.9rem;
    }
    
    /* Upload area */
    .upload-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .upload-title {
        color: #333;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Progress indicators */
    .progress-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 8px;
        background: white;
    }
    
    .progress-step.completed {
        background: #e8f5e8;
        border-left: 3px solid #4CAF50;
    }
    
    .progress-step.pending {
        background: #fff3cd;
        border-left: 3px solid #ffc107;
    }
    
    /* Category cards */
    .category-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .category-header {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .clause-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .clause-number {
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .text-section {
        margin: 0.5rem 0;
        padding: 0.8rem;
        border-radius: 8px;
    }
    
    .original-text {
        background: #f5f5f5;
        border-left: 3px solid #666;
    }
    
    .translated-text {
        background: #e8f5e8;
        border-left: 3px solid #4CAF50;
    }
    
    .text-label {
        font-weight: bold;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }
    
    /* Action buttons */
    .action-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 10px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 1rem 0;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    .action-button:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    
    /* Analysis result */
    .analysis-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #2196f3;
    }
    
    .analysis-header {
        color: #2196f3;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Status indicators */
    .status-success {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    
    .status-info {
        background: #e3f2fd;
        color: #1565c0;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    
    /* Hide Streamlit elements */
    .stButton > button {
        width: 100%;
    }
    
    .stDownloadButton > button {
        width: 100%;
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

# Main header
st.markdown("""
<div class="main-container">
    <div class="main-header">
        <h1>📋 계약서 검토 시스템</h1>
        <p>🔒 세션 기반 보안 | 🌍 다국어 지원 | 🤖 AI 분석</p>
    </div>
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

# Mode selection with beautiful cards
st.markdown("""
<div class="mode-container">
    <div class="mode-card" onclick="document.querySelector('#mode1').click()">
        <h3>🔍 단독 검토</h3>
        <p>계약서 하나만 업로드하여<br>원론적 분석 진행</p>
    </div>
    <div class="mode-card" onclick="document.querySelector('#mode2').click()">
        <h3>📚 비교 검토</h3>
        <p>두 계약서를 비교하여<br>차이점 분석</p>
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
        st.rerun()

with col2:
    if st.button("Mode 2", key="mode2", help="비교 검토 모드"):
        st.session_state.review_mode = "comparison"
        st.session_state.processing_complete = False
        st.session_state.analysis_result = None
        st.rerun()

# Display current mode
current_mode = "단독 검토" if st.session_state.review_mode == "standalone" else "비교 검토"
st.markdown(f"""
<div class="status-info">
    <strong>현재 모드:</strong> {current_mode}
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown("""
<div class="upload-container">
    <div class="upload-title">
        📄 계약서 업로드
    </div>
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
        all_clauses_text = "\n\n".join([f"{clause['number']}: {clause['text'][:300]}" for clause in clauses[:15]])
        
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
        
        # JSON 파싱 시도
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                categorized = json.loads(json_str)
                return categorized
        except:
            pass
        
        # 기본 분류
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
    <div class="upload-container">
        <div class="upload-title">
            🚀 처리 및 분석
        </div>
    """, unsafe_allow_html=True)
    
    # Check if ready for processing
    ready_for_processing = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_processing = False
            st.warning("⚠️ 비교 검토를 위해서는 레퍼런스 계약서도 업로드해주세요.")
    
    if ready_for_processing:
        if st.button("🌍 번역 및 분류 시작", type="primary", use_container_width=True, disabled=st.session_state.processing_complete):
            with st.spinner("번역 및 카테고리 분류를 진행하고 있습니다..."):
                try:
                    client = openai.OpenAI()
                    
                    # 번역 및 카테고리 분류
                    clauses = st.session_state.target_contract["clauses"]
                    
                    # 각 조항 번역
                    for clause in clauses[:10]:  # 최대 10개 조항만 번역
                        clause["translated_text"] = translate_clause_to_korean(clause["text"], client)
                    
                    # 카테고리 분류
                    categorized = categorize_clauses(clauses, client)
                    st.session_state.target_contract["categorized_clauses"] = categorized
                    st.session_state.processing_complete = True
                    
                    st.success("✅ 번역 및 분류 완료!")
                    
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

# Display categorized clauses
if st.session_state.processing_complete and st.session_state.target_contract.get("categorized_clauses"):
    st.markdown("""
    <div class="category-container">
        <div class="category-header">
            📂 카테고리별 조항 분류
        </div>
    """, unsafe_allow_html=True)
    
    categorized = st.session_state.target_contract["categorized_clauses"]
    clauses_dict = {clause["number"]: clause for clause in st.session_state.target_contract["clauses"]}
    
    for category, clause_numbers in categorized["categories"].items():
        if clause_numbers:  # 해당 카테고리에 조항이 있는 경우만 표시
            st.markdown(f"""
            <div class="category-header">
                📂 {category} ({len(clause_numbers)}개 조항)
            </div>
            """, unsafe_allow_html=True)
            
            for clause_num in clause_numbers:
                if clause_num in clauses_dict:
                    clause = clauses_dict[clause_num]
                    st.markdown(f"""
                    <div class="clause-item">
                        <div class="clause-number">{clause['number']}</div>
                        
                        <div class="text-section original-text">
                            <div class="text-label">🌍 원문:</div>
                            {clause['text'][:200]}{'...' if len(clause['text']) > 200 else ''}
                        </div>
                        
                        {f'''
                        <div class="text-section translated-text">
                            <div class="text-label">🇰🇷 한국어:</div>
                            {clause['translated_text'][:200]}{'...' if len(clause['translated_text']) > 200 else ''}
                        </div>
                        ''' if clause.get('translated_text') else ''}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Analysis section
if st.session_state.target_contract and st.session_state.target_contract["text"]:
    st.markdown("""
    <div class="analysis-container">
        <div class="analysis-header">
            🤖 AI 분석
        </div>
    """, unsafe_allow_html=True)
    
    # Check if ready for analysis
    ready_for_analysis = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_analysis = False
            st.warning("⚠️ 비교 검토를 위해서는 레퍼런스 계약서도 업로드해주세요.")
    
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
            <div class="analysis-header">
                📊 AI 분석 결과
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
    
    st.markdown("</div>", unsafe_allow_html=True)

# Security notice
st.markdown("""
<div class="upload-container">
    <div class="upload-title">
        🔒 보안 안내
    </div>
    <ul>
        <li>업로드된 모든 파일은 세션 종료 시 자동으로 삭제됩니다</li>
        <li>외부 저장소나 데이터베이스에 저장되지 않습니다</li>
        <li>분석 결과는 다운로드 후 안전한 곳에 보관하세요</li>
    </ul>
</div>
""", unsafe_allow_html=True) 