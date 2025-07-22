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
    page_title="📋 Contract Review",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern, clean CSS
st.markdown("""
<style>
    /* Global styles */
    .main {
        background: #f8fafc;
        padding: 0;
    }
    
    /* Header */
    .header {
        background: white;
        padding: 2rem;
        text-align: center;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    
    .title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #64748b;
        font-size: 1.1rem;
    }
    
    /* Main container */
    .container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 0 2rem;
    }
    
    /* Mode tabs */
    .mode-tabs {
        display: flex;
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .mode-tab {
        flex: 1;
        padding: 1rem 2rem;
        text-align: center;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
        color: #64748b;
    }
    
    .mode-tab.active {
        background: #3b82f6;
        color: white;
    }
    
    .mode-tab:hover:not(.active) {
        background: #f1f5f9;
    }
    
    /* Content sections */
    .section {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .section-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Upload area */
    .upload-zone {
        border: 2px dashed #cbd5e1;
        border-radius: 8px;
        padding: 3rem;
        text-align: center;
        background: #f8fafc;
        transition: all 0.2s ease;
        margin: 1rem 0;
    }
    
    .upload-zone:hover {
        border-color: #3b82f6;
        background: #eff6ff;
    }
    
    .upload-icon {
        font-size: 3rem;
        color: #64748b;
        margin-bottom: 1rem;
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
    
    .status.info {
        background: #eff6ff;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    
    /* Progress bar */
    .progress-bar {
        background: #e2e8f0;
        border-radius: 8px;
        height: 8px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        height: 100%;
        transition: width 0.3s ease;
    }
    
    /* Category grid */
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .category-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 1.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .category-header {
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
    
    .clause-title {
        font-weight: 600;
        color: #3b82f6;
        margin-bottom: 0.5rem;
    }
    
    .clause-text {
        color: #475569;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Buttons */
    .btn {
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
    
    .btn:hover {
        background: #2563eb;
        transform: translateY(-1px);
    }
    
    .btn:disabled {
        background: #94a3b8;
        cursor: not-allowed;
        transform: none;
    }
    
    .btn.secondary {
        background: #64748b;
    }
    
    .btn.secondary:hover {
        background: #475569;
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
    @media (max-width: 768px) {
        .category-grid {
            grid-template-columns: 1fr;
        }
        
        .mode-tabs {
            flex-direction: column;
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

# Header
st.markdown("""
<div class="header">
    <div class="title">📋 Contract Review</div>
    <div class="subtitle">AI-powered contract analysis and comparison</div>
</div>
""", unsafe_allow_html=True)

# Main container
st.markdown('<div class="container">', unsafe_allow_html=True)

# Mode selection tabs
st.markdown("""
<div class="section">
    <div class="section-title">🎯 Select Mode</div>
    <div class="mode-tabs">
        <div class="mode-tab" onclick="document.querySelector('#single').click()">🔍 Single Review</div>
        <div class="mode-tab" onclick="document.querySelector('#compare').click()">📚 Compare Review</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hidden mode buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Single", key="single", help="Single Review"):
        st.session_state.mode = "single"
        st.session_state.processing_step = 0
        st.session_state.categorized_clauses = None
        st.session_state.analysis_result = None
        st.rerun()

with col2:
    if st.button("Compare", key="compare", help="Compare Review"):
        st.session_state.mode = "compare"
        st.session_state.processing_step = 0
        st.session_state.categorized_clauses = None
        st.session_state.analysis_result = None
        st.rerun()

# File upload section
st.markdown("""
<div class="section">
    <div class="section-title">📄 Upload Files</div>
    <div class="upload-zone">
        <div class="upload-icon">📁</div>
        <div>Drag and drop your contract here or click to browse</div>
    </div>
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
    """Extract clauses from text with improved logic"""
    if not text:
        return []
    
    # Multiple patterns for clause detection
    patterns = [
        r'\n\s*(?=\d+\.)',  # Number followed by dot
        r'\n\s*(?=Article\s+\d+)',  # Article followed by number
        r'\n\s*(?=Section\s+\d+)',  # Section followed by number
        r'\n\s*(?=Clause\s+\d+)',   # Clause followed by number
    ]
    
    clauses = []
    for pattern in patterns:
        parts = re.split(pattern, text)
        if len(parts) > 1:
            for i, part in enumerate(parts[1:], 1):
                part = part.strip()
                if len(part) > 30:  # Minimum length
                    # Extract clause number
                    match = re.match(r'^(\d+\.?\s*|Article\s+\d+\.?\s*|Section\s+\d+\.?\s*|Clause\s+\d+\.?\s*)(.*)', part, re.DOTALL)
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
                            "number": f"Clause {i}",
                            "text": part,
                            "translated": None
                        })
            break  # Use the first pattern that finds clauses
    
    return clauses

def categorize_clauses_simple(clauses):
    """Simple keyword-based categorization"""
    categories = {
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
    
    # Keywords for each category
    keywords = {
        "Purpose & Scope": ["purpose", "scope", "objective", "intent", "agreement", "contract"],
        "Rights & Obligations": ["right", "obligation", "duty", "responsibility", "permit", "authorize"],
        "Payment & Settlement": ["payment", "fee", "price", "cost", "amount", "settlement", "compensation"],
        "Intellectual Property": ["intellectual", "property", "patent", "copyright", "trademark", "license"],
        "Confidentiality": ["confidential", "secret", "non-disclosure", "privacy", "proprietary"],
        "Termination": ["terminate", "end", "expire", "cancel", "discontinue"],
        "Liability & Indemnification": ["liability", "indemnify", "damage", "loss", "claim", "warranty"],
        "Dispute Resolution": ["dispute", "arbitration", "mediation", "court", "legal", "governing law"]
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
            categories["Others"].append(clause["number"])
    
    return {"categories": categories}

def translate_clause(text, client):
    """Translate clause to Korean"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional translator. Translate the contract clause into natural Korean."},
                {"role": "user", "content": f"Translate this contract clause to Korean:\n\n{text[:800]}"}
            ],
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Translation error: {str(e)}"

# File uploaders
target_file = st.file_uploader("Upload contract to review", type=['pdf'], key="target")

if target_file:
    st.session_state.target_file = target_file
    if st.session_state.target_text is None:
        st.session_state.target_text = extract_text_from_pdf(target_file)
        if st.session_state.target_text:
            st.session_state.clauses = extract_clauses_from_text(st.session_state.target_text)
            st.session_state.processing_step = 1

if st.session_state.mode == "compare":
    reference_file = st.file_uploader("Upload reference contract", type=['pdf'], key="reference")
    
    if reference_file:
        st.session_state.reference_file = reference_file
        if st.session_state.reference_text is None:
            st.session_state.reference_text = extract_text_from_pdf(reference_file)

# Status display
if st.session_state.target_text:
    st.markdown(f"""
    <div class="status success">
        ✅ Contract uploaded successfully
        📊 Found {len(st.session_state.clauses)} clauses
    </div>
    """, unsafe_allow_html=True)

if st.session_state.mode == "compare" and st.session_state.reference_text:
    st.markdown(f"""
    <div class="status success">
        ✅ Reference contract uploaded successfully
    </div>
    """, unsafe_allow_html=True)

# Progress bar
if st.session_state.target_text:
    progress = (st.session_state.processing_step / 4) * 100
    st.markdown(f"""
    <div class="section">
        <div class="section-title">📋 Processing Progress</div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%"></div>
        </div>
        <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.9rem; color: #64748b;">
            <span>Upload</span>
            <span>Extract</span>
            <span>Process</span>
            <span>Analyze</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Processing section
if st.session_state.target_text and st.session_state.processing_step >= 1:
    st.markdown("""
    <div class="section">
        <div class="section-title">🚀 Process Contract</div>
    """, unsafe_allow_html=True)
    
    # Check if ready for processing
    ready = True
    if st.session_state.mode == "compare" and not st.session_state.reference_text:
        ready = False
        st.markdown("""
        <div class="status warning">
            ⚠️ Please upload a reference contract for comparison
        </div>
        """, unsafe_allow_html=True)
    
    if ready:
        if st.button("🌍 Start Processing", type="primary", use_container_width=True):
            with st.spinner("Processing contract..."):
                try:
                    client = openai.OpenAI()
                    
                    # Translate clauses
                    for clause in st.session_state.clauses[:5]:
                        clause["translated"] = translate_clause(clause["text"], client)
                    
                    # Categorize clauses
                    st.session_state.categorized_clauses = categorize_clauses_simple(st.session_state.clauses)
                    st.session_state.processing_step = 3
                    
                    st.markdown("""
                    <div class="status success">
                        ✅ Processing completed successfully!
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Processing error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Display categorized clauses
if st.session_state.categorized_clauses:
    st.markdown("""
    <div class="section">
        <div class="section-title">📂 Categorized Clauses</div>
    """, unsafe_allow_html=True)
    
    categorized = st.session_state.categorized_clauses
    clauses_dict = {clause["number"]: clause for clause in st.session_state.clauses}
    
    total_clauses = 0
    for category, clause_numbers in categorized["categories"].items():
        if clause_numbers:
            total_clauses += len(clause_numbers)
            st.markdown(f"""
            <div class="category-card">
                <div class="category-header">
                    📂 {category} ({len(clause_numbers)})
                </div>
            """, unsafe_allow_html=True)
            
            for clause_num in clause_numbers:
                if clause_num in clauses_dict:
                    clause = clauses_dict[clause_num]
                    st.markdown(f"""
                    <div class="clause-item">
                        <div class="clause-title">{clause['number']}</div>
                        <div class="clause-text">
                            {clause['text'][:100]}{'...' if len(clause['text']) > 100 else ''}
                        </div>
                        {f'''
                        <div class="clause-text" style="margin-top: 0.5rem; color: #059669; font-style: italic;">
                            🇰🇷 {clause['translated'][:100]}{'...' if len(clause['translated']) > 100 else ''}
                        </div>
                        ''' if clause.get('translated') else ''}
                    </div>
                    """, unsafe_allow_html=True)
    
    if total_clauses == 0:
        st.markdown("""
        <div class="status warning">
            ⚠️ No clauses were categorized. The contract might not have clear clause structure.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Analysis section
if st.session_state.target_text and st.session_state.processing_step >= 3:
    st.markdown("""
    <div class="section">
        <div class="section-title">🤖 AI Analysis</div>
    """, unsafe_allow_html=True)
    
    ready_for_analysis = True
    if st.session_state.mode == "compare" and not st.session_state.reference_text:
        ready_for_analysis = False
        st.markdown("""
        <div class="status warning">
            ⚠️ Please upload a reference contract for comparison
        </div>
        """, unsafe_allow_html=True)
    
    if ready_for_analysis:
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            with st.spinner("AI is analyzing the contract..."):
                try:
                    # Prepare analysis prompt
                    if st.session_state.mode == "single":
                        prompt = f"""
Analyze this contract professionally:

Contract content:
{st.session_state.target_text[:4000]}

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
{st.session_state.target_text[:2000]}

[Reference Contract]
{st.session_state.reference_text[:2000]}

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
                        max_tokens=1500,
                        temperature=0.3
                    )
                    
                    st.session_state.analysis_result = response.choices[0].message.content
                    st.session_state.processing_step = 4
                    
                except Exception as e:
                    st.error(f"❌ Analysis error: {str(e)}")
                    st.info("Please check your OpenAI API key.")
        
        # Display analysis result
        if st.session_state.analysis_result:
            st.markdown("""
            <div class="analysis-box">
                <h4>📊 Analysis Result</h4>
            """, unsafe_allow_html=True)
            
            st.markdown(st.session_state.analysis_result)
            
            # Download analysis
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_filename = f"contract_analysis_{timestamp}.txt"
            
            st.download_button(
                label="📥 Download Analysis",
                data=st.session_state.analysis_result,
                file_name=analysis_filename,
                mime="text/plain",
                use_container_width=True
            )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Security notice
st.markdown("""
<div class="section">
    <div class="section-title">🔒 Security</div>
    <ul>
        <li>All files are deleted when session ends</li>
        <li>No external storage used</li>
        <li>Download results to secure location</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) 