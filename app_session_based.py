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
    page_title="📋 Contract Review System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS with clean design
st.markdown("""
<style>
    /* Global styles */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
        padding: 0;
    }
    
    /* Header */
    .hero-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 3rem 2rem;
        text-align: center;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        color: #6b7280;
        font-size: 1.2rem;
        font-weight: 400;
    }
    
    /* Main container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Mode selector */
    .mode-selector {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .mode-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    
    .mode-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        border: 2px solid #e5e7eb;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .mode-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        border-color: #667eea;
    }
    
    .mode-card.active {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8faff 0%, #e8f0ff 100%);
    }
    
    .mode-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .mode-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    
    .mode-desc {
        color: #6b7280;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* Current mode indicator */
    .current-mode {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* Content sections */
    .content-section {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        padding: 2.5rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .section-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Upload area */
    .upload-area {
        border: 3px dashed #667eea;
        border-radius: 16px;
        padding: 3rem;
        text-align: center;
        background: linear-gradient(135deg, #f8faff 0%, #e8f0ff 100%);
        transition: all 0.3s ease;
        margin: 2rem 0;
    }
    
    .upload-area:hover {
        border-color: #764ba2;
        background: linear-gradient(135deg, #f0f4ff 0%, #e0e8ff 100%);
    }
    
    .upload-icon {
        font-size: 4rem;
        color: #667eea;
        margin-bottom: 1rem;
    }
    
    .upload-text {
        font-size: 1.2rem;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    .upload-hint {
        color: #6b7280;
        font-size: 0.9rem;
    }
    
    /* Status cards */
    .status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .status-success {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    }
    
    .status-info {
        border-left-color: #3b82f6;
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
    }
    
    .status-warning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    
    /* Progress steps */
    .progress-container {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    .progress-steps {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 2rem 0;
    }
    
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    
    .step-circle {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .step-circle.completed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .step-circle.pending {
        background: #f3f4f6;
        color: #9ca3af;
        border: 2px solid #e5e7eb;
    }
    
    .step-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #6b7280;
        text-align: center;
    }
    
    .step-label.completed {
        color: #10b981;
        font-weight: 600;
    }
    
    /* Category display */
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .category-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .category-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    .category-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        font-size: 1.2rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .category-content {
        padding: 1.5rem;
    }
    
    .clause-item {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 3px solid #667eea;
    }
    
    .clause-header {
        font-weight: 600;
        color: #2563eb;
        margin-bottom: 0.8rem;
        font-size: 1.1rem;
    }
    
    .text-content {
        background: white;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .text-label {
        font-weight: 600;
        font-size: 0.85rem;
        color: #6b7280;
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Action buttons */
    .action-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1.2rem 2.5rem;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 100%;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
    }
    
    .action-btn:disabled {
        background: #9ca3af;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Analysis result */
    .analysis-result {
        background: linear-gradient(135deg, #f8faff 0%, #e8f0ff 100%);
        padding: 2rem;
        border-radius: 16px;
        margin: 2rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Hide Streamlit elements */
    .stButton > button {
        width: 100%;
    }
    
    .stDownloadButton > button {
        width: 100%;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .mode-grid {
            grid-template-columns: 1fr;
        }
        
        .category-grid {
            grid-template-columns: 1fr;
        }
        
        .progress-steps {
            flex-direction: column;
            gap: 1rem;
        }
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

# Hero header
st.markdown("""
<div class="hero-header">
    <div class="hero-title">📋 Contract Review System</div>
    <div class="hero-subtitle">AI-powered contract analysis with multilingual support</div>
</div>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Sidebar for API key check
with st.sidebar:
    st.header("🔑 API Settings")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API Key Configured")
    else:
        st.error("❌ OpenAI API Key Required")
        st.info("Set OPENAI_API_KEY in Streamlit Secrets")

# Mode selection
st.markdown("""
<div class="mode-selector">
    <div class="section-title">🎯 Select Review Mode</div>
    <div class="mode-grid">
        <div class="mode-card" onclick="document.querySelector('#mode1').click()">
            <div class="mode-icon">🔍</div>
            <div class="mode-title">Single Review</div>
            <div class="mode-desc">Analyze one contract with AI-powered insights</div>
        </div>
        <div class="mode-card" onclick="document.querySelector('#mode2').click()">
            <div class="mode-icon">📚</div>
            <div class="mode-title">Compare Review</div>
            <div class="mode-desc">Compare two contracts and identify differences</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Mode selection buttons (hidden)
col1, col2 = st.columns(2)
with col1:
    if st.button("Mode 1", key="mode1", help="Single Review Mode"):
        st.session_state.review_mode = "standalone"
        st.session_state.processing_complete = False
        st.session_state.analysis_result = None
        st.session_state.debug_info = []
        st.rerun()

with col2:
    if st.button("Mode 2", key="mode2", help="Compare Review Mode"):
        st.session_state.review_mode = "comparison"
        st.session_state.processing_complete = False
        st.session_state.analysis_result = None
        st.session_state.debug_info = []
        st.rerun()

# Display current mode
current_mode = "Single Review" if st.session_state.review_mode == "standalone" else "Compare Review"
st.markdown(f"""
<div class="current-mode">
    🎯 Current Mode: {current_mode}
</div>
""", unsafe_allow_html=True)

# File upload section
st.markdown("""
<div class="content-section">
    <div class="section-title">📄 Upload Contract</div>
    <div class="upload-area">
        <div class="upload-icon">📁</div>
        <div class="upload-text">Drag and drop your contract here</div>
        <div class="upload-hint">or click to browse files (PDF only)</div>
    </div>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF"""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"PDF reading error: {str(e)}")
        return None

def extract_clauses_from_text(text):
    """Extract clauses from text"""
    if not text:
        return []
    
    # Improved clause pattern matching
    clauses = re.split(r'\n\s*(?=\d+\.)', text)
    extracted_clauses = []
    
    for i, clause in enumerate(clauses):
        clause = clause.strip()
        if clause and len(clause) > 20:
            # Extract clause number
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
    """Translate individual clause to Korean"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the contract clause into natural Korean."},
                {"role": "user", "content": f"Translate this contract clause to Korean:\n\n{text[:1000]}"}
            ],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Translation error: {str(e)}"

def categorize_clauses(clauses, client):
    """Categorize clauses by type"""
    try:
        # Create a more structured prompt
        all_clauses_text = "\n\n".join([f"{clause['number']}: {clause['text'][:200]}" for clause in clauses[:8]])
        
        prompt = f"""
Analyze these contract clauses and categorize them:

{all_clauses_text}

Categorize into these types:
1. Purpose & Scope
2. Rights & Obligations  
3. Payment & Settlement
4. Intellectual Property
5. Confidentiality
6. Termination
7. Liability & Indemnification
8. Dispute Resolution
9. Others

Return as JSON:
{{
    "categories": {{
        "Purpose & Scope": ["clause_numbers"],
        "Rights & Obligations": ["clause_numbers"],
        "Payment & Settlement": ["clause_numbers"],
        "Intellectual Property": ["clause_numbers"],
        "Confidentiality": ["clause_numbers"],
        "Termination": ["clause_numbers"],
        "Liability & Indemnification": ["clause_numbers"],
        "Dispute Resolution": ["clause_numbers"],
        "Others": ["clause_numbers"]
    }}
}}
"""
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a contract analysis expert. Categorize clauses accurately."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        result = response.choices[0].message.content
        st.session_state.debug_info.append(f"GPT Response: {result[:200]}...")
        
        # JSON parsing
        try:
            json_start = result.find('{')
            json_end = result.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = result[json_start:json_end]
                categorized = json.loads(json_str)
                st.session_state.debug_info.append(f"JSON parsing successful: {len(categorized.get('categories', {}))} categories")
                return categorized
        except Exception as e:
            st.session_state.debug_info.append(f"JSON parsing failed: {str(e)}")
        
        # Fallback categorization
        default_categories = {
            "categories": {
                "Purpose & Scope": [],
                "Rights & Obligations": [],
                "Payment & Settlement": [],
                "Intellectual Property": [],
                "Confidentiality": [],
                "Termination": [],
                "Liability & Indemnification": [],
                "Dispute Resolution": [],
                "Others": []
            }
        }
        
        # Simple categorization logic
        if clauses:
            # First clause is usually purpose/scope
            default_categories["categories"]["Purpose & Scope"].append(clauses[0]["number"])
            
            # Distribute remaining clauses
            for i, clause in enumerate(clauses[1:4]):
                if "payment" in clause["text"].lower() or "fee" in clause["text"].lower():
                    default_categories["categories"]["Payment & Settlement"].append(clause["number"])
                elif "confidential" in clause["text"].lower() or "secret" in clause["text"].lower():
                    default_categories["categories"]["Confidentiality"].append(clause["number"])
                elif "terminate" in clause["text"].lower() or "end" in clause["text"].lower():
                    default_categories["categories"]["Termination"].append(clause["number"])
                else:
                    default_categories["categories"]["Rights & Obligations"].append(clause["number"])
            
            st.session_state.debug_info.append(f"Fallback categorization applied")
        
        return default_categories
        
    except Exception as e:
        st.session_state.debug_info.append(f"Categorization error: {str(e)}")
        return None

# Target contract upload
target_file = st.file_uploader(
    "Upload contract to review",
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
            ✅ {target_file.name} uploaded successfully<br>
            📊 Extracted {len(st.session_state.target_contract['clauses'])} clauses
        </div>
        """, unsafe_allow_html=True)

# Reference contract upload (only for comparison mode)
if st.session_state.review_mode == "comparison":
    reference_file = st.file_uploader(
        "Upload reference contract for comparison",
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
                ✅ {reference_file.name} uploaded successfully<br>
                📊 Extracted {len(st.session_state.reference_contract['clauses'])} clauses
            </div>
            """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Processing section
if st.session_state.target_contract and st.session_state.target_contract["text"]:
    st.markdown("""
    <div class="content-section">
        <div class="section-title">🚀 Process & Analyze</div>
    """, unsafe_allow_html=True)
    
    # Check if ready for processing
    ready_for_processing = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_processing = False
            st.markdown("""
            <div class="status-warning">
                ⚠️ Please upload a reference contract for comparison review.
            </div>
            """, unsafe_allow_html=True)
    
    if ready_for_processing:
        if st.button("🌍 Start Translation & Categorization", type="primary", use_container_width=True, disabled=st.session_state.processing_complete):
            with st.spinner("Processing translation and categorization..."):
                try:
                    client = openai.OpenAI()
                    
                    # Translation and categorization
                    clauses = st.session_state.target_contract["clauses"]
                    
                    # Translate clauses
                    for i, clause in enumerate(clauses[:6]):  # Translate up to 6 clauses
                        clause["translated_text"] = translate_clause_to_korean(clause["text"], client)
                        st.session_state.debug_info.append(f"Clause {clause['number']} translated")
                    
                    # Categorize clauses
                    categorized = categorize_clauses(clauses, client)
                    st.session_state.target_contract["categorized_clauses"] = categorized
                    st.session_state.processing_complete = True
                    
                    st.markdown("""
                    <div class="status-success">
                        ✅ Translation and categorization completed!
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Processing error: {str(e)}")
    
    # Display progress
    if st.session_state.target_contract:
        st.markdown("""
        <div class="progress-container">
            <div class="section-title">📋 Processing Status</div>
            <div class="progress-steps">
        """, unsafe_allow_html=True)
        
        steps = [
            ("Upload", True),
            ("Extract", bool(st.session_state.target_contract.get("clauses"))),
            ("Process", st.session_state.processing_complete),
            ("Analyze", bool(st.session_state.analysis_result))
        ]
        
        for step_name, completed in steps:
            status_class = "completed" if completed else "pending"
            st.markdown(f"""
            <div class="progress-step">
                <div class="step-circle {status_class}">
                    {'✓' if completed else '○'}
                </div>
                <div class="step-label {status_class}">{step_name}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Debug information
if st.session_state.debug_info:
    with st.expander("🔍 Debug Information", expanded=False):
        for info in st.session_state.debug_info:
            st.write(info)

# Display categorized clauses
if st.session_state.processing_complete and st.session_state.target_contract.get("categorized_clauses"):
    st.markdown("""
    <div class="content-section">
        <div class="section-title">📂 Categorized Clauses</div>
        <div class="category-grid">
    """, unsafe_allow_html=True)
    
    categorized = st.session_state.target_contract["categorized_clauses"]
    clauses_dict = {clause["number"]: clause for clause in st.session_state.target_contract["clauses"]}
    
    total_clauses = 0
    for category, clause_numbers in categorized["categories"].items():
        if clause_numbers:
            total_clauses += len(clause_numbers)
            st.markdown(f"""
            <div class="category-card">
                <div class="category-header">
                    📂 {category} ({len(clause_numbers)})
                </div>
                <div class="category-content">
            """, unsafe_allow_html=True)
            
            for clause_num in clause_numbers:
                if clause_num in clauses_dict:
                    clause = clauses_dict[clause_num]
                    st.markdown(f"""
                    <div class="clause-item">
                        <div class="clause-header">{clause['number']}</div>
                        
                        <div class="text-content">
                            <div class="text-label">🌍 Original</div>
                            {clause['text'][:120]}{'...' if len(clause['text']) > 120 else ''}
                        </div>
                        
                        {f'''
                        <div class="text-content">
                            <div class="text-label">🇰🇷 Korean</div>
                            {clause['translated_text'][:120]}{'...' if len(clause['translated_text']) > 120 else ''}
                        </div>
                        ''' if clause.get('translated_text') else ''}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div></div>", unsafe_allow_html=True)
    
    if total_clauses == 0:
        st.markdown("""
        <div class="status-warning">
            ⚠️ No clauses were categorized. Please check debug information.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# Analysis section
if st.session_state.target_contract and st.session_state.target_contract["text"]:
    st.markdown("""
    <div class="content-section">
        <div class="section-title">🤖 AI Analysis</div>
    """, unsafe_allow_html=True)
    
    # Check if ready for analysis
    ready_for_analysis = True
    if st.session_state.review_mode == "comparison":
        if not st.session_state.reference_contract or not st.session_state.reference_contract["text"]:
            ready_for_analysis = False
            st.markdown("""
            <div class="status-warning">
                ⚠️ Please upload a reference contract for comparison review.
            </div>
            """, unsafe_allow_html=True)
    
    if ready_for_analysis:
        if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing the contract..."):
                try:
                    # Prepare analysis prompt
                    if st.session_state.review_mode == "standalone":
                        prompt = f"""
Analyze this contract professionally:

Contract content:
{st.session_state.target_contract["text"][:6000]}

Analyze the following aspects:
1. Contract purpose and scope
2. Rights and obligations of parties
3. Payment and settlement terms
4. Risk factors and considerations
5. Areas needing improvement
6. Overall assessment and recommendations

Provide analysis in Korean.
"""
                    else:  # comparison mode
                        prompt = f"""
Compare these two contracts:

[Target Contract]
{st.session_state.target_contract["text"][:3000]}

[Reference Contract]
{st.session_state.reference_contract["text"][:3000]}

Compare the following aspects:
1. Key differences and similarities
2. Pros and cons of target contract
3. Areas for improvement compared to reference
4. Risk factor comparison
5. Recommendations

Provide analysis in Korean.
"""
                    
                    # Call OpenAI API
                    client = openai.OpenAI()
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "You are a contract review expert. Provide accurate and practical analysis."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=2000,
                        temperature=0.3
                    )
                    
                    st.session_state.analysis_result = response.choices[0].message.content
                    
                except Exception as e:
                    st.error(f"❌ Analysis error: {str(e)}")
                    st.info("Please check your OpenAI API key.")
        
        # Display analysis result
        if st.session_state.analysis_result:
            st.markdown("""
            <div class="analysis-result">
                <h4>📊 AI Analysis Result</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.analysis_result)
            
            # Download analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_filename = f"contract_analysis_{timestamp}.txt"
            
            st.download_button(
                label="📥 Download Analysis Result",
                data=st.session_state.analysis_result,
                file_name=analysis_filename,
                mime="text/plain",
                use_container_width=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Security notice
st.markdown("""
<div class="content-section">
    <div class="section-title">🔒 Security Notice</div>
    <ul>
        <li>All uploaded files are automatically deleted when the session ends</li>
        <li>No external storage or database is used</li>
        <li>Please download analysis results to a secure location</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) 