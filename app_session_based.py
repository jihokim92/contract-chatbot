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
    initial_sidebar_state="expanded"
)

# Clean, modern CSS
st.markdown("""
<style>
    /* Global styles */
    .main {
        background: #f8fafc;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Top banner */
    .top-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        text-align: center;
        font-weight: 500;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .banner-text {
        font-size: 1.1rem;
    }
    
    .banner-btn {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .banner-btn:hover {
        background: #2563eb;
    }
    
    /* Main layout */
    .app-container {
        display: flex;
        gap: 2rem;
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Left panel - Configuration */
    .config-panel {
        width: 400px;
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: fit-content;
    }
    
    .panel-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Mode selection */
    .mode-option {
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .mode-option.active {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .mode-option:hover:not(.active) {
        border-color: #cbd5e1;
        background: #f8fafc;
    }
    
    .mode-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .mode-desc {
        color: #64748b;
        font-size: 0.9rem;
    }
    
    /* File upload */
    .upload-section {
        margin: 2rem 0;
    }
    
    .upload-area {
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .upload-area:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .upload-icon {
        font-size: 2rem;
        color: #64748b;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        color: #374151;
        font-weight: 500;
    }
    
    /* Status messages */
    .status {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status.success {
        background: #f0fdf4;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status.warning {
        background: #fffbeb;
        color: #92400e;
        border: 1px solid #fed7aa;
    }
    
    /* Action buttons */
    .action-btn {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
        margin: 0.5rem 0;
    }
    
    .action-btn:hover {
        background: #2563eb;
    }
    
    .action-btn:disabled {
        background: #94a3b8;
        cursor: not-allowed;
    }
    
    /* Right panel - Preview/Results */
    .preview-panel {
        flex: 1;
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .preview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    
    .preview-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e293b;
    }
    
    .preview-actions {
        display: flex;
        gap: 0.5rem;
    }
    
    .btn-secondary {
        background: #64748b;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-secondary:hover {
        background: #475569;
    }
    
    /* Category display */
    .category-section {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #3b82f6;
    }
    
    .category-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .clause-item {
        background: white;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .clause-header {
        font-weight: 600;
        color: #3b82f6;
        margin-bottom: 0.5rem;
    }
    
    .clause-text {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    .clause-translation {
        color: #059669;
        font-style: italic;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    /* Analysis result */
    .analysis-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit elements */
    .stButton > button {
        width: 100%;
    }
    
    .stDownloadButton > button {
        width: 100%;
    }
    
    /* Responsive */
    @media (max-width: 1200px) {
        .app-container {
            flex-direction: column;
        }
        
        .config-panel {
            width: 100%;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'mode' not in st.session_state:
    st.session_state.mode = "single"
if 'target_file' not in st.session_state:
    st.session_state.target_file = None
if 'reference_file' not in st.session_state:
    st.session_state.reference_file = None
if 'target_text' not in st.session_state:
    st.session_state.target_text = None
if 'reference_text' not in st.session_state:
    st.session_state.reference_text = None
if 'clauses' not in st.session_state:
    st.session_state.clauses = []
if 'categorized_clauses' not in st.session_state:
    st.session_state.categorized_clauses = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'processing_step' not in st.session_state:
    st.session_state.processing_step = 0

# Top banner
st.markdown("""
<div class="top-banner">
    <div class="banner-text">이제 사이트에 채팅 버튼만 설치하면 14일 프로 플랜 무료 체험이 시작됩니다!</div>
    <button class="banner-btn">계약서 분석 시작하기</button>
</div>
""", unsafe_allow_html=True)

# Main app container
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Left Configuration Panel
st.markdown("""
<div class="config-panel">
    <div class="panel-title">
        🏠 계약서 검토 시스템 만들기
    </div>
""", unsafe_allow_html=True)

# Mode selection
st.markdown("""
<div class="mode-option" onclick="document.querySelector('#single_mode').click()">
    <div class="mode-title">🔍 단독 검토</div>
    <div class="mode-desc">계약서 하나만 업로드하여 AI 분석</div>
</div>
<div class="mode-option" onclick="document.querySelector('#compare_mode').click()">
    <div class="mode-title">📚 비교 검토</div>
    <div class="mode-desc">두 계약서를 비교하여 차이점 분석</div>
</div>
""", unsafe_allow_html=True)

# Hidden mode buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Single", key="single_mode", help="단독 검토"):
        st.session_state.mode = "single"
        st.session_state.processing_step = 0
        st.session_state.categorized_clauses = None
        st.session_state.analysis_result = None
        st.rerun()
with col2:
    if st.button("Compare", key="compare_mode", help="비교 검토"):
        st.session_state.mode = "compare"
        st.session_state.processing_step = 0
        st.session_state.categorized_clauses = None
        st.session_state.analysis_result = None
        st.rerun()

# File upload section
st.markdown("""
<div class="upload-section">
    <h4>📄 계약서 업로드</h4>
    <div class="upload-area">
        <div class="upload-icon">📁</div>
        <div class="upload-text">클릭하여 계약서 선택 (PDF)</div>
    </div>
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
    """텍스트에서 조항 추출 (개선된 로직)"""
    if not text:
        return []
    
    # 다양한 조항 패턴 지원
    patterns = [
        r'\n\s*(?=\d+\.)',  # 숫자. 패턴
        r'\n\s*(?=제\s*\d+조)',  # 제X조 패턴
        r'\n\s*(?=Article\s+\d+)',  # Article 패턴
        r'\n\s*(?=Section\s+\d+)',  # Section 패턴
        r'\n\s*(?=Clause\s+\d+)',   # Clause 패턴
    ]
    
    clauses = []
    for pattern in patterns:
        parts = re.split(pattern, text)
        if len(parts) > 1:
            for i, part in enumerate(parts[1:], 1):
                part = part.strip()
                if len(part) > 30:  # 최소 길이
                    # 조항 번호 추출
                    match = re.match(r'^(\d+\.?\s*|제\s*\d+조\s*|Article\s+\d+\.?\s*|Section\s+\d+\.?\s*|Clause\s+\d+\.?\s*)(.*)', part, re.DOTALL)
                    if match:
                        clause_num = match.group(1).strip()
                        clause_text = match.group(2).strip()
                        clauses.append({
                            "number": clause_num,
                            "text": clause_text,
                            "translated": None
                        })
                    else:
                        clauses.append({
                            "number": f"조항 {i}",
                            "text": part,
                            "translated": None
                        })
            break  # 첫 번째 패턴에서 조항을 찾으면 중단
    
    return clauses

def categorize_clauses_simple(clauses):
    """키워드 기반 조항 분류"""
    categories = {
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
    
    # 각 카테고리별 키워드
    keywords = {
        "계약 목적 및 범위": ["목적", "범위", "의도", "계약", "협약", "계약서", "목적", "scope", "purpose", "objective"],
        "당사자 권리와 의무": ["권리", "의무", "책임", "허가", "승인", "right", "obligation", "duty", "responsibility"],
        "정산 및 지급 조건": ["지급", "비용", "가격", "금액", "정산", "보상", "payment", "fee", "price", "cost", "settlement"],
        "지적재산권": ["지적재산", "특허", "저작권", "상표", "라이선스", "intellectual", "property", "patent", "copyright"],
        "기밀유지": ["기밀", "비밀", "비공개", "프라이버시", "confidential", "secret", "non-disclosure", "privacy"],
        "계약 해지": ["해지", "종료", "만료", "취소", "terminate", "end", "expire", "cancel"],
        "책임 및 면책": ["책임", "면책", "손해", "손실", "청구", "liability", "indemnify", "damage", "loss"],
        "분쟁해결": ["분쟁", "중재", "조정", "법원", "법적", "dispute", "arbitration", "mediation", "court"]
    }
    
    for clause in clauses:
        text_lower = clause["text"].lower()
        categorized = False
        
        for category, category_keywords in keywords.items():
            if any(keyword in text_lower for keyword in category_keywords):
                categories[category].append(clause["number"])
                categorized = True
                break
        
        if not categorized:
            categories["기타"].append(clause["number"])
    
    return {"categories": categories}

def translate_clause(text, client):
    """조항을 한국어로 번역"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 전문 번역가입니다. 계약서 조항을 자연스러운 한국어로 번역해주세요."},
                {"role": "user", "content": f"다음 계약서 조항을 한국어로 번역해주세요:\n\n{text[:800]}"}
            ],
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"번역 오류: {str(e)}"

# File uploader
target_file = st.file_uploader("계약서 업로드", type=['pdf'], key="target", label_visibility="collapsed")

if target_file:
    st.session_state.target_file = target_file
    if st.session_state.target_text is None:
        st.session_state.target_text = extract_text_from_pdf(target_file)
        if st.session_state.target_text:
            st.session_state.clauses = extract_clauses_from_text(st.session_state.target_text)
            st.session_state.processing_step = 1

# Reference file for comparison mode
if st.session_state.mode == "compare":
    reference_file = st.file_uploader("비교용 계약서 업로드", type=['pdf'], key="reference", label_visibility="collapsed")
    
    if reference_file:
        st.session_state.reference_file = reference_file
        if st.session_state.reference_text is None:
            st.session_state.reference_text = extract_text_from_pdf(reference_file)

# Status display
if st.session_state.target_text:
    st.markdown(f"""
    <div class="status success">
        ✅ 계약서 업로드 완료
        📊 {len(st.session_state.clauses)}개 조항 발견
    </div>
    """, unsafe_allow_html=True)

if st.session_state.mode == "compare" and st.session_state.reference_text:
    st.markdown(f"""
    <div class="status success">
        ✅ 비교용 계약서 업로드 완료
    </div>
    """, unsafe_allow_html=True)

# Processing button
if st.session_state.target_text and st.session_state.processing_step >= 1:
    ready = True
    if st.session_state.mode == "compare" and not st.session_state.reference_text:
        ready = False
        st.markdown("""
        <div class="status warning">
            ⚠️ 비교 검토를 위해서는 비교용 계약서도 업로드해주세요
        </div>
        """, unsafe_allow_html=True)
    
    if ready:
        if st.button("🌍 분석 시작", type="primary", use_container_width=True):
            with st.spinner("계약서를 분석하고 있습니다..."):
                try:
                    client = openai.OpenAI()
                    
                    # 조항 번역
                    for clause in st.session_state.clauses[:5]:
                        clause["translated"] = translate_clause(clause["text"], client)
                    
                    # 조항 분류
                    st.session_state.categorized_clauses = categorize_clauses_simple(st.session_state.clauses)
                    st.session_state.processing_step = 3
                    
                    st.markdown("""
                    <div class="status success">
                        ✅ 분석 완료!
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ 분석 오류: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)

# Right Preview Panel
st.markdown("""
<div class="preview-panel">
    <div class="preview-header">
        <div class="preview-title">📊 분석 결과</div>
        <div class="preview-actions">
            <button class="btn-secondary">취소</button>
            <button class="btn-secondary">결과 저장</button>
        </div>
    </div>
""", unsafe_allow_html=True)

# Display categorized clauses
if st.session_state.categorized_clauses:
    categorized = st.session_state.categorized_clauses
    clauses_dict = {clause["number"]: clause for clause in st.session_state.clauses}
    
    total_clauses = 0
    for category, clause_numbers in categorized["categories"].items():
        if clause_numbers:
            total_clauses += len(clause_numbers)
            st.markdown(f"""
            <div class="category-section">
                <div class="category-title">
                    📂 {category} ({len(clause_numbers)}개)
                </div>
            """, unsafe_allow_html=True)
            
            for clause_num in clause_numbers:
                if clause_num in clauses_dict:
                    clause = clauses_dict[clause_num]
                    st.markdown(f"""
                    <div class="clause-item">
                        <div class="clause-header">{clause['number']}</div>
                        <div class="clause-text">
                            {clause['text'][:100]}{'...' if len(clause['text']) > 100 else ''}
                        </div>
                        {f'''
                        <div class="clause-translation">
                            🇰🇷 {clause['translated'][:100]}{'...' if len(clause['translated']) > 100 else ''}
                        </div>
                        ''' if clause.get('translated') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    
    if total_clauses == 0:
        st.markdown("""
        <div class="status warning">
            ⚠️ 분류된 조항이 없습니다. 계약서 구조를 확인해주세요.
        </div>
        """, unsafe_allow_html=True)

# AI Analysis section
if st.session_state.target_text and st.session_state.processing_step >= 3:
    ready_for_analysis = True
    if st.session_state.mode == "compare" and not st.session_state.reference_text:
        ready_for_analysis = False
    
    if ready_for_analysis:
        if st.button("🤖 AI 분석 시작", type="primary", use_container_width=True):
            with st.spinner("AI가 계약서를 분석하고 있습니다..."):
                try:
                    # 분석 프롬프트 준비
                    if st.session_state.mode == "single":
                        prompt = f"""
다음 계약서를 전문적으로 분석해주세요:

계약서 내용:
{st.session_state.target_text[:4000]}

다음 항목들을 중심으로 분석해주세요:
1. 계약의 주요 목적과 범위
2. 당사자의 권리와 의무
3. 책임과 보상 조항
4. 위험 요소와 주의사항
5. 개선이 필요한 조항들
6. 전반적인 평가 및 권고사항

한국어로 상세히 분석해주세요.
"""
                    else:  # 비교 모드
                        prompt = f"""
다음 두 계약서를 비교 분석해주세요:

[검토 대상 계약서]
{st.session_state.target_text[:2000]}

[비교용 계약서]
{st.session_state.reference_text[:2000]}

다음 항목들을 중심으로 비교 분석해주세요:
1. 주요 차이점과 유사점
2. 검토 대상 계약서의 장단점
3. 비교용 계약서 대비 개선 필요 사항
4. 위험 요소 비교
5. 권고사항

한국어로 상세히 분석해주세요.
"""
                    
                    # OpenAI API 호출
                    client = openai.OpenAI()
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "당신은 계약서 검토 전문가입니다. 정확하고 실용적인 분석을 제공해주세요."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=1500,
                        temperature=0.3
                    )
                    
                    st.session_state.analysis_result = response.choices[0].message.content
                    st.session_state.processing_step = 4
                    
                except Exception as e:
                    st.error(f"❌ 분석 오류: {str(e)}")
                    st.info("OpenAI API 키를 확인해주세요.")
        
        # 분석 결과 표시
        if st.session_state.analysis_result:
            st.markdown("""
            <div class="analysis-box">
                <h4>📊 AI 분석 결과</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.analysis_result)
            
            # 분석 결과 다운로드
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

st.markdown("</div></div>", unsafe_allow_html=True) 