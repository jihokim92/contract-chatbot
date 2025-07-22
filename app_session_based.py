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
    page_title="📋 AI 계약서 검토 시스템",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern, sophisticated CSS with glassmorphism and animations
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@300;400;500;600;700&display=swap');
    
    /* Global Reset & Variables */
    :root {
        --primary-color: #6366f1;
        --primary-light: #8b5cf6;
        --primary-dark: #4338ca;
        --secondary-color: #06b6d4;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-primary: #fefefe;
        --bg-secondary: #f8fafc;
        --bg-card: rgba(255, 255, 255, 0.9);
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-muted: #94a3b8;
        --border-color: rgba(226, 232, 240, 0.8);
        --shadow-light: 0 2px 8px rgba(0, 0, 0, 0.06);
        --shadow-medium: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-heavy: 0 8px 32px rgba(0, 0, 0, 0.12);
        --radius-small: 8px;
        --radius-medium: 12px;
        --radius-large: 16px;
        --radius-xl: 24px;
    }
    
    * {
        box-sizing: border-box;
    }
    
    /* Main Layout */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 40%, #f093fb 100%);
        min-height: 100vh;
        padding: 0;
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main > div {
        background: transparent;
    }
    
    /* Header */
    .header-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .header-content {
        max-width: 1400px;
        margin: 0 auto;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        color: white;
        font-size: 1.75rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 0;
    }
    
    .header-subtitle {
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.95rem;
        margin-left: 2.5rem;
        margin-top: 0.25rem;
    }
    
    .header-badge {
        background: rgba(255, 255, 255, 0.2);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-large);
        font-size: 0.875rem;
        font-weight: 500;
        backdrop-filter: blur(10px);
    }
    
    /* Main Container */
    .app-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 2rem 4rem;
        display: grid;
        grid-template-columns: 420px 1fr;
        gap: 2rem;
        animation: fadeInUp 0.6s ease-out;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Left Panel - Control */
    .control-panel {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: var(--radius-xl);
        padding: 2rem;
        box-shadow: var(--shadow-heavy);
        height: fit-content;
        position: sticky;
        top: 140px;
    }
    
    .panel-header {
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .panel-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .panel-description {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Mode Selection */
    .mode-section {
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .mode-grid {
        display: grid;
        gap: 1rem;
    }
    
    .mode-card {
        background: rgba(255, 255, 255, 0.7);
        border: 2px solid transparent;
        border-radius: var(--radius-medium);
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .mode-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .mode-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .mode-card.active {
        border-color: var(--primary-color);
        background: rgba(99, 102, 241, 0.05);
        box-shadow: var(--shadow-medium);
    }
    
    .mode-card.active::before {
        opacity: 0.05;
    }
    
    .mode-icon {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .mode-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .mode-description {
        color: var(--text-secondary);
        font-size: 0.875rem;
        line-height: 1.4;
        position: relative;
        z-index: 1;
    }
    
    /* File Upload */
    .upload-section {
        margin-bottom: 2rem;
    }
    
    .upload-card {
        background: rgba(255, 255, 255, 0.6);
        border: 2px dashed var(--border-color);
        border-radius: var(--radius-medium);
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .upload-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .upload-card:hover {
        border-color: var(--primary-color);
        background: rgba(99, 102, 241, 0.02);
        transform: translateY(-1px);
    }
    
    .upload-card:hover::before {
        opacity: 0.03;
    }
    
    .upload-icon {
        font-size: 2.5rem;
        color: var(--text-muted);
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .upload-card:hover .upload-icon {
        color: var(--primary-color);
        animation: bounce 1s ease-in-out;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% {
            transform: translateY(0);
        }
        40% {
            transform: translateY(-10px);
        }
        60% {
            transform: translateY(-5px);
        }
    }
    
    .upload-title {
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .upload-subtitle {
        color: var(--text-secondary);
        font-size: 0.875rem;
        position: relative;
        z-index: 1;
    }
    
    /* Status Messages */
    .status-message {
        padding: 1rem 1.25rem;
        border-radius: var(--radius-medium);
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
        animation: slideInRight 0.4s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .status-success {
        background: rgba(16, 185, 129, 0.1);
        color: var(--success-color);
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.1);
        color: var(--warning-color);
        border: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .status-info {
        background: rgba(6, 182, 212, 0.1);
        color: var(--secondary-color);
        border: 1px solid rgba(6, 182, 212, 0.2);
    }
    
    /* Action Buttons */
    .action-button {
        background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: var(--radius-medium);
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        margin: 1rem 0;
        box-shadow: var(--shadow-light);
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .action-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .action-button:hover::before {
        left: 100%;
    }
    
    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
    }
    
    .action-button:active {
        transform: translateY(0);
    }
    
    .action-button:disabled {
        background: var(--text-muted);
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    .secondary-button {
        background: rgba(255, 255, 255, 0.8);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    .secondary-button:hover {
        background: rgba(255, 255, 255, 0.95);
    }
    
    /* Right Panel - Results */
    .results-panel {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: var(--radius-xl);
        padding: 0;
        box-shadow: var(--shadow-heavy);
        overflow: hidden;
        min-height: 600px;
    }
    
    .results-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05));
        padding: 2rem;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .results-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .results-actions {
        display: flex;
        gap: 0.75rem;
    }
    
    .icon-button {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid var(--border-color);
        color: var(--text-secondary);
        padding: 0.5rem;
        border-radius: var(--radius-small);
        cursor: pointer;
        transition: all 0.2s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
    }
    
    .icon-button:hover {
        background: rgba(255, 255, 255, 0.95);
        color: var(--primary-color);
        transform: translateY(-1px);
    }
    
    .results-content {
        padding: 2rem;
        max-height: calc(100vh - 300px);
        overflow-y: auto;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        color: var(--text-muted);
    }
    
    .empty-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.3;
    }
    
    .empty-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .empty-subtitle {
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Category Sections */
    .category-section {
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-medium);
        margin-bottom: 1.5rem;
        overflow: hidden;
        animation: fadeInUp 0.5s ease-out;
    }
    
    .category-header {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.02));
        padding: 1.25rem 1.5rem;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .category-title {
        font-weight: 600;
        color: var(--text-primary);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .category-count {
        background: var(--primary-color);
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
    }
    
    .clause-list {
        padding: 1rem;
    }
    
    .clause-item {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-small);
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .clause-item:hover {
        background: rgba(255, 255, 255, 0.95);
        transform: translateY(-1px);
        box-shadow: var(--shadow-light);
    }
    
    .clause-number {
        font-weight: 600;
        color: var(--primary-color);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .clause-text {
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: 0.75rem;
    }
    
    .clause-translation {
        background: rgba(16, 185, 129, 0.05);
        color: var(--success-color);
        padding: 0.75rem;
        border-radius: var(--radius-small);
        border-left: 3px solid var(--success-color);
        font-style: italic;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Analysis Results */
    .analysis-container {
        background: rgba(255, 255, 255, 0.6);
        border: 1px solid var(--border-color);
        border-radius: var(--radius-medium);
        padding: 2rem;
        margin: 1.5rem 0;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .analysis-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    .analysis-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .analysis-content {
        color: var(--text-secondary);
        line-height: 1.7;
        font-size: 0.95rem;
    }
    
    /* Progress Indicators */
    .progress-container {
        background: rgba(255, 255, 255, 0.8);
        padding: 1.5rem;
        border-radius: var(--radius-medium);
        margin: 1rem 0;
    }
    
    .progress-bar {
        background: rgba(99, 102, 241, 0.1);
        height: 6px;
        border-radius: 3px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, var(--primary-color), var(--primary-light));
        height: 100%;
        border-radius: 3px;
        transition: width 0.8s ease-out;
    }
    
    /* Responsive Design */
    @media (max-width: 1200px) {
        .app-container {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }
        
        .control-panel {
            position: static;
        }
    }
    
    @media (max-width: 768px) {
        .app-container {
            padding: 0 1rem 2rem;
        }
        
        .header-content {
            flex-direction: column;
            text-align: center;
            gap: 1rem;
        }
        
        .header-title {
            font-size: 1.5rem;
        }
        
        .control-panel,
        .results-panel {
            padding: 1.5rem;
        }
        
        .mode-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Hide Streamlit Elements */
    .stRadio > div {
        display: none;
    }
    
    .stFileUploader > div {
        display: none;
    }
    
    .stButton > button {
        display: none;
    }
    
    /* Loading Animation */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 0.8s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(99, 102, 241, 0.3);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(99, 102, 241, 0.5);
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

# Header
st.markdown("""
<div class="header-container">
    <div class="header-content">
        <div>
            <div class="header-title">🤖 AI 계약서 검토 시스템</div>
            <div class="header-subtitle">지능형 계약서 분석 및 위험 요소 검토</div>
        </div>
        <div class="header-badge">⚡ Powered by GPT-4</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main app container
st.markdown('<div class="app-container">', unsafe_allow_html=True)

# Left Control Panel
st.markdown("""
<div class="control-panel">
    <div class="panel-header">
        <div class="panel-title">
            🎯 검토 설정
        </div>
        <div class="panel-description">
            계약서 업로드 후 AI 분석을 시작하세요
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Custom mode selection
st.markdown("""
<div class="mode-section">
    <div class="section-title">
        📋 검토 모드 선택
    </div>
    <div class="mode-grid">
        <div class="mode-card" onclick="selectMode('single')" id="mode-single">
            <div class="mode-icon">🔍</div>
            <div class="mode-title">단독 검토</div>
            <div class="mode-description">하나의 계약서를 상세히 분석하고 위험 요소를 검토합니다</div>
        </div>
        <div class="mode-card" onclick="selectMode('compare')" id="mode-compare">
            <div class="mode-icon">📊</div>
            <div class="mode-title">비교 검토</div>
            <div class="mode-description">두 계약서를 비교 분석하여 차이점을 파악합니다</div>
        </div>
    </div>
</div>

<script>
function selectMode(mode) {
    document.querySelectorAll('.mode-card').forEach(card => {
        card.classList.remove('active');
    });
    document.getElementById('mode-' + mode).classList.add('active');
    
    // Streamlit 상태 업데이트 로직은 여기에 추가
}

// 초기 모드 설정
document.getElementById('mode-single').classList.add('active');
</script>
""", unsafe_allow_html=True)

# Hidden Streamlit radio for actual functionality
mode = st.radio(
    "검토 모드 선택",
    ["🔍 단독 검토", "📊 비교 검토"],
    label_visibility="collapsed"
)

# Update session state based on selection
if "단독 검토" in mode:
    st.session_state.mode = "single"
else:
    st.session_state.mode = "compare"

# File upload section with custom styling
st.markdown("""
<div class="upload-section">
    <div class="section-title">
        📄 계약서 업로드
    </div>
    <div class="upload-card">
        <div class="upload-icon">📁</div>
        <div class="upload-title">계약서를 선택하세요</div>
        <div class="upload-subtitle">PDF 파일을 드래그하거나 클릭하여 업로드</div>
    </div>
</div>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """PDF에서 텍스트 추출"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\\n"
        return text.strip()
    except Exception as e:
        st.error(f"PDF 읽기 오류: {str(e)}")
        return None

def extract_clauses_from_text(text):
    """텍스트에서 조항 추출 (개선된 로직)"""
    if not text:
        return []
    
    patterns = [
        r'\\n\\s*(?=\\d+\\.)',
        r'\\n\\s*(?=제\\s*\\d+조)',
        r'\\n\\s*(?=Article\\s+\\d+)',
        r'\\n\\s*(?=Section\\s+\\d+)',
        r'\\n\\s*(?=Clause\\s+\\d+)',
    ]
    
    clauses = []
    for pattern in patterns:
        parts = re.split(pattern, text)
        if len(parts) > 1:
            for i, part in enumerate(parts[1:], 1):
                part = part.strip()
                if len(part) > 30:
                    match = re.match(r'^(\\d+\\.?\\s*|제\\s*\\d+조\\s*|Article\\s+\\d+\\.?\\s*|Section\\s+\\d+\\.?\\s*|Clause\\s+\\d+\\.?\\s*)(.*)', part, re.DOTALL)
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
            break
    
    return clauses

def categorize_clauses_simple(clauses):
    """키워드 기반 조항 분류"""
    categories = {
        "📋 계약 목적 및 범위": [],
        "⚖️ 당사자 권리와 의무": [],
        "💰 정산 및 지급 조건": [],
        "🛡️ 지적재산권": [],
        "🔒 기밀유지": [],
        "❌ 계약 해지": [],
        "⚠️ 책임 및 면책": [],
        "🏛️ 분쟁해결": [],
        "📂 기타": []
    }
    
    keywords = {
        "📋 계약 목적 및 범위": ["목적", "범위", "의도", "계약", "협약", "scope", "purpose"],
        "⚖️ 당사자 권리와 의무": ["권리", "의무", "책임", "허가", "승인", "right", "obligation"],
        "💰 정산 및 지급 조건": ["지급", "비용", "가격", "금액", "정산", "payment", "fee"],
        "🛡️ 지적재산권": ["지적재산", "특허", "저작권", "상표", "intellectual", "property"],
        "🔒 기밀유지": ["기밀", "비밀", "비공개", "confidential", "secret"],
        "❌ 계약 해지": ["해지", "종료", "만료", "취소", "terminate", "end"],
        "⚠️ 책임 및 면책": ["책임", "면책", "손해", "손실", "liability", "damage"],
        "🏛️ 분쟁해결": ["분쟁", "중재", "조정", "법원", "dispute", "arbitration"]
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
            categories["📂 기타"].append(clause["number"])
    
    return {"categories": categories}

def translate_clause(text, client):
    """조항을 한국어로 번역"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 전문 번역가입니다. 계약서 조항을 자연스러운 한국어로 번역해주세요."},
                {"role": "user", "content": f"다음 계약서 조항을 한국어로 번역해주세요:\\n\\n{text[:800]}"}
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
    st.markdown("""
    <div class="upload-section">
        <div class="section-title">
            📊 비교용 계약서 업로드
        </div>
        <div class="upload-card">
            <div class="upload-icon">📋</div>
            <div class="upload-title">비교할 계약서를 선택하세요</div>
            <div class="upload-subtitle">기준이 되는 계약서 PDF를 업로드</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    reference_file = st.file_uploader("비교용 계약서 업로드", type=['pdf'], key="reference", label_visibility="collapsed")
    
    if reference_file:
        st.session_state.reference_file = reference_file
        if st.session_state.reference_text is None:
            st.session_state.reference_text = extract_text_from_pdf(reference_file)

# Status display with beautiful styling
if st.session_state.target_text:
    st.markdown(f"""
    <div class="status-message status-success">
        <span>✅</span>
        <div>
            <strong>계약서 업로드 완료</strong><br>
            <small>{len(st.session_state.clauses)}개 조항이 발견되었습니다</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.mode == "compare" and st.session_state.reference_text:
    st.markdown("""
    <div class="status-message status-success">
        <span>✅</span>
        <div>
            <strong>비교용 계약서 업로드 완료</strong><br>
            <small>비교 분석 준비가 완료되었습니다</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Processing button with enhanced styling
if st.session_state.target_text and st.session_state.processing_step >= 1:
    ready = True
    if st.session_state.mode == "compare" and not st.session_state.reference_text:
        ready = False
        st.markdown("""
        <div class="status-message status-warning">
            <span>⚠️</span>
            <div>
                <strong>추가 파일 필요</strong><br>
                <small>비교 검토를 위해서는 비교용 계약서도 업로드해주세요</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if ready:
        st.markdown("""
        <button class="action-button" onclick="startAnalysis()">
            <span>🚀</span>
            <span>AI 분석 시작</span>
        </button>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 분석 시작", type="primary", use_container_width=True):
            with st.spinner("🤖 AI가 계약서를 분석하고 있습니다..."):
                try:
                    client = openai.OpenAI()
                    
                    # Progress indicator
                    progress_html = """
                    <div class="progress-container">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div class="loading-spinner"></div>
                            <span>조항 분석 및 번역 중...</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 30%"></div>
                        </div>
                    </div>
                    """
                    progress_placeholder = st.empty()
                    progress_placeholder.markdown(progress_html, unsafe_allow_html=True)
                    
                    # 조항 번역 (최대 5개)
                    for i, clause in enumerate(st.session_state.clauses[:5]):
                        clause["translated"] = translate_clause(clause["text"], client)
                        progress = 30 + (i + 1) * 20
                        progress_html = f"""
                        <div class="progress-container">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <div class="loading-spinner"></div>
                                <span>조항 {i+1}/5 번역 완료...</span>
                            </div>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {progress}%"></div>
                            </div>
                        </div>
                        """
                        progress_placeholder.markdown(progress_html, unsafe_allow_html=True)
                    
                    # 조항 분류
                    st.session_state.categorized_clauses = categorize_clauses_simple(st.session_state.clauses)
                    st.session_state.processing_step = 3
                    
                    # AI 분석
                    progress_html = """
                    <div class="progress-container">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <div class="loading-spinner"></div>
                            <span>AI 전문 분석 중...</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: 80%"></div>
                        </div>
                    </div>
                    """
                    progress_placeholder.markdown(progress_html, unsafe_allow_html=True)
                    
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
                    else:
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
                    
                    # 완료 상태
                    progress_html = """
                    <div class="status-message status-success">
                        <span>🎉</span>
                        <div>
                            <strong>분석 완료!</strong><br>
                            <small>AI 분석이 성공적으로 완료되었습니다</small>
                        </div>
                    </div>
                    """
                    progress_placeholder.markdown(progress_html, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ 분석 오류: {str(e)}")

st.markdown("</div>", unsafe_allow_html=True)  # Close control panel

# Right Results Panel
st.markdown("""
<div class="results-panel">
    <div class="results-header">
        <div class="results-title">
            📊 분석 결과
        </div>
        <div class="results-actions">
            <button class="icon-button" title="새로고침">↻</button>
            <button class="icon-button" title="다운로드">↓</button>
            <button class="icon-button" title="공유">⤴</button>
        </div>
    </div>
    <div class="results-content">
""", unsafe_allow_html=True)

# Display results or empty state
if not st.session_state.categorized_clauses and not st.session_state.analysis_result:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📋</div>
        <div class="empty-title">분석 결과가 표시됩니다</div>
        <div class="empty-subtitle">
            계약서를 업로드하고 분석을 시작하면<br>
            상세한 검토 결과를 확인할 수 있습니다
        </div>
    </div>
    """, unsafe_allow_html=True)

# Display categorized clauses with beautiful styling
if st.session_state.categorized_clauses:
    categorized = st.session_state.categorized_clauses
    clauses_dict = {clause["number"]: clause for clause in st.session_state.clauses}
    
    st.markdown("### 📂 조항 분류 결과")
    st.markdown("---")
    
    for category, clause_numbers in categorized["categories"].items():
        if clause_numbers:
            st.markdown(f"""
            <div class="category-section">
                <div class="category-header">
                    <div class="category-title">{category}</div>
                    <div class="category-count">{len(clause_numbers)}</div>
                </div>
                <div class="clause-list">
            """, unsafe_allow_html=True)
            
            for clause_num in clause_numbers:
                if clause_num in clauses_dict:
                    clause = clauses_dict[clause_num]
                    clause_text = clause['text'][:200] + ('...' if len(clause['text']) > 200 else '')
                    
                    clause_html = f"""
                    <div class="clause-item">
                        <div class="clause-number">📄 {clause['number']}</div>
                        <div class="clause-text">{clause_text}</div>
                    """
                    
                    if clause.get('translated'):
                        translated_text = clause['translated'][:200] + ('...' if len(clause['translated']) > 200 else '')
                        clause_html += f"""
                        <div class="clause-translation">
                            🇰🇷 {translated_text}
                        </div>
                        """
                    
                    clause_html += "</div>"
                    st.markdown(clause_html, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)

# Display AI analysis results
if st.session_state.analysis_result:
    st.markdown("""
    <div class="analysis-container">
        <div class="analysis-header">
            <span>🤖</span>
            <div class="analysis-title">AI 전문 분석 결과</div>
        </div>
        <div class="analysis-content">
    """, unsafe_allow_html=True)
    
    # Format the analysis result with better typography
    analysis_formatted = st.session_state.analysis_result.replace("\\n", "<br>")
    st.markdown(analysis_formatted, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Download button with custom styling
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_filename = f"계약서_분석_{timestamp}.txt"
    
    st.download_button(
        label="📥 분석 결과 다운로드",
        data=st.session_state.analysis_result,
        file_name=analysis_filename,
        mime="text/plain",
        use_container_width=True
    )

st.markdown("</div></div>", unsafe_allow_html=True)  # Close results panel and app container
