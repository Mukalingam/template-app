import streamlit as st
from openai import OpenAI
import json
from concurrent.futures import ThreadPoolExecutor
import time
import base64

# Page config
st.set_page_config(
    page_title="AI Code Generator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 40px;
        margin: 20px 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .main-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .main-subtitle {
        color: #666;
        font-size: 1.3rem;
        font-weight: 400;
        margin-top: 10px;
    }
    
    /* Content cards */
    .content-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 35px;
        margin: 20px 0;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Primary button */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Text inputs */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 15px;
        font-size: 16px;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: white;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 20px;
        border: 2px dashed #e0e0e0;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 15px;
        font-weight: 600;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px 12px 0 0;
        padding: 15px 25px;
        font-weight: 600;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Success/Error/Info boxes */
    .stSuccess, .stError, .stInfo, .stWarning {
        border-radius: 12px;
        padding: 20px;
        border: none;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Quick example buttons */
    .example-btn {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .example-btn:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Audio recorder styling */
    [data-testid="stAudioInput"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Download buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        font-weight: 600;
    }
    
    /* Section headers */
    h1, h2, h3 {
        color: #1a202c;
        font-weight: 700;
    }
    
    /* Feature badges */
    .feature-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'specification' not in st.session_state:
    st.session_state.specification = None
if 'frontend_code' not in st.session_state:
    st.session_state.frontend_code = ""
if 'backend_code' not in st.session_state:
    st.session_state.backend_code = ""
if 'preview_html' not in st.session_state:
    st.session_state.preview_html = ""
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'trigger_generation' not in st.session_state:
    st.session_state.trigger_generation = False

# Beautiful Header
st.markdown("""
<div class="main-header">
    <h1 class="main-title">✨ AI Code Generator</h1>
    <p class="main-subtitle">Transform your voice or text into production-ready code instantly</p>
    <div style="margin-top: 20px;">
        <span class="feature-badge">🎤 Voice Input</span>
        <span class="feature-badge">⚡ Parallel Generation</span>
        <span class="feature-badge">🎬 Live Preview</span>
        <span class="feature-badge">📦 Full Stack</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: white;'>
        <h1 style='color: white; font-size: 2rem; margin-bottom: 10px;'>⚙️</h1>
        <h2 style='color: white; font-size: 1.5rem;'>Configuration</h2>
    </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input("🔑 OpenAI API Key", type="password", help="Enter your OpenAI API key")
    
    if api_key:
        st.success("✅ API Key Active")
    else:
        st.warning("⚠️ API Key Required")
    
    st.markdown("---")
    
    st.markdown("""
    <div style='color: white;'>
        <h3 style='color: white;'>📖 Quick Guide</h3>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <strong>🎤 Voice Mode:</strong><br/>
            1. Click record button<br/>
            2. Speak requirements<br/>
            3. Stop recording<br/>
            4. Auto-transcribe ✨<br/>
            5. Review & submit
        </div>
        <div style='background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin: 10px 0;'>
            <strong>⌨️ Text Mode:</strong><br/>
            1. Type requirements<br/>
            2. Click generate<br/>
            3. Get instant code!
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    <div style='background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; color: white;'>
        <h4 style='color: white; margin-top: 0;'>💡 Pro Tip</h4>
        <p style='margin: 0; font-size: 14px;'>
        Be specific! Include:<br/>
        • Module name<br/>
        • Key features<br/>
        • Data fields<br/>
        • Special requirements
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown('<div class="content-card">', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📝 Your Requirements")
    
    # Input method selection with better styling
    input_method = st.radio(
        "Choose your input method:",
        ["🎤 Voice Recording", "⌨️ Text Input"],
        horizontal=True,
        key="input_method"
    )
    
    if "Voice Recording" in input_method:
        st.markdown("### 🎙️ Voice Recorder")
        st.info("🎤 Click the microphone button below to start recording your requirements")
        
        try:
            audio_value = st.audio_input("Record your requirements", key="audio_recorder")
            
            if audio_value is not None:
                if not api_key:
                    st.error("⚠️ Please enter your OpenAI API key in the sidebar")
                else:
                    st.audio(audio_value)
                    
                    audio_bytes = audio_value.read()
                    audio_hash = hash(audio_bytes)
                    
                    if 'last_audio_hash' not in st.session_state or st.session_state.last_audio_hash != audio_hash:
                        st.session_state.last_audio_hash = audio_hash
                        
                        with st.spinner("✨ Converting your voice to text with AI magic..."):
                            try:
                                client = OpenAI(api_key=api_key)
                                audio_value.seek(0)
                                
                                transcript_response = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=audio_value
                                )
                                
                                st.session_state.transcript = transcript_response.text
                                st.session_state.user_input = transcript_response.text
                                
                                st.success("✅ Voice converted to text successfully!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Transcription failed: {str(e)}")
        
        except AttributeError:
            st.warning("""
            ⚠️ **Audio recording requires Streamlit 1.28.0+**
            
            Upgrade now: `pip install --upgrade streamlit`
            """)
            
            uploaded_audio = st.file_uploader(
                "Or upload an audio file",
                type=['mp3', 'wav', 'm4a', 'webm', 'ogg'],
                key="audio_uploader"
            )
            
            if uploaded_audio is not None:
                if not api_key:
                    st.error("⚠️ Please enter your OpenAI API key")
                else:
                    st.audio(uploaded_audio)
                    
                    if 'last_upload_name' not in st.session_state or st.session_state.last_upload_name != uploaded_audio.name:
                        st.session_state.last_upload_name = uploaded_audio.name
                        
                        with st.spinner("✨ Converting voice to text..."):
                            try:
                                client = OpenAI(api_key=api_key)
                                uploaded_audio.seek(0)
                                
                                transcript_response = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=uploaded_audio
                                )
                                
                                st.session_state.transcript = transcript_response.text
                                st.session_state.user_input = transcript_response.text
                                
                                st.success("✅ Voice converted!")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
        
        if st.session_state.transcript:
            st.markdown("---")
            st.markdown("### ✨ Your Requirements (Voice → Text)")
            st.success("✅ Voice successfully converted! You can edit the text below if needed.")
            
            user_input = st.text_area(
                "Review and edit your requirements:",
                value=st.session_state.transcript,
                height=150,
                key="transcript_editor",
                help="The AI has converted your voice to text. Edit if needed before generating."
            )
            st.session_state.user_input = user_input
            
            st.markdown("---")
            submit_col1, submit_col2, submit_col3 = st.columns([1, 2, 1])
            with submit_col2:
                submit_voice = st.button("✅ Submit & Generate Code", type="primary", use_container_width=True, key="submit_voice_btn")
                if submit_voice:
                    st.session_state.trigger_generation = True
    
    else:
        user_input = st.text_area(
            "Describe your module requirements:",
            height=200,
            placeholder="Example: Create an invoice module with customer details (name, email), line items with quantity and price, 18% tax calculation, and PDF download button",
            value=st.session_state.user_input,
            key="text_input_area"
        )
        st.session_state.user_input = user_input

st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("## 🎯 Quick Examples")
    st.markdown("Click any example to auto-fill:")
    
    examples = [
        {
            "icon": "📄",
            "title": "Invoice System",
            "desc": "Customer details, items, tax, PDF",
            "text": "I want an invoice module with customer details including name, email and address, a line items table with description, quantity and price columns, automatic tax calculation at 18 percent, total amount display, and a download as PDF button"
        },
        {
            "icon": "👤",
            "title": "User Management",
            "desc": "Auth, profiles, roles, search",
            "text": "I want a user management system with registration form, login authentication, profile editing page, password reset functionality, role-based access control with admin and user roles, and user list with search and filter"
        },
        {
            "icon": "📦",
            "title": "Product Catalog",
            "desc": "Grid, search, filters, cart",
            "text": "I want a product catalog with product grid layout, search bar, filters for category and price range, product detail page with image gallery, add to cart functionality, and inventory tracking"
        },
        {
            "icon": "📊",
            "title": "Analytics Dashboard",
            "desc": "Charts, stats, export data",
            "text": "I want an analytics dashboard with sales charts showing monthly revenue, user statistics with total and active users, recent transactions table, and export data to Excel button"
        }
    ]
    
    for idx, ex in enumerate(examples):
        if st.button(f"{ex['icon']} {ex['title']}", key=f"ex{idx+1}", use_container_width=True):
            st.session_state.user_input = ex['text']
            st.session_state.transcript = ""
            st.session_state.trigger_generation = False
            st.rerun()
        st.caption(ex['desc'])

# Generate button
if "Text Input" in input_method or not st.session_state.transcript:
    st.markdown("---")
    generate_col1, generate_col2, generate_col3 = st.columns([1, 2, 1])
    
    with generate_col2:
        generate_btn = st.button(
            "🚀 Generate Code + Preview",
            type="primary",
            use_container_width=True,
            key="generate_button"
        )
        if generate_btn:
            st.session_state.trigger_generation = True

# GENERATION LOGIC
if st.session_state.trigger_generation:
    st.session_state.trigger_generation = False
    current_input = st.session_state.user_input
    
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar")
    elif not current_input or len(current_input.strip()) < 10:
        st.error("⚠️ Please provide detailed requirements (minimum 10 characters)")
    else:
        client = OpenAI(api_key=api_key)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.markdown("### 🔍 Step 1/3: Analyzing requirements...")
            progress_bar.progress(15)
            
            spec_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a software architect. Convert user requirements into a structured specification.
                        Respond ONLY with valid JSON in this exact format:
                        {
                            "moduleName": "string",
                            "description": "string",
                            "features": ["feature1", "feature2", "feature3"],
                            "dataStructure": {
                                "field1": "type",
                                "field2": "type"
                            },
                            "endpoints": ["POST /api/endpoint1", "GET /api/endpoint2"],
                            "techStack": {
                                "frontend": "React + TypeScript + Tailwind CSS",
                                "backend": "Node.js + Express + MongoDB"
                            }
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Convert this requirement into a structured specification: {current_input}"
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            spec_text = spec_response.choices[0].message.content
            spec_text = spec_text.replace("```json", "").replace("```", "").strip()
            specification = json.loads(spec_text)
            st.session_state.specification = specification
            
            progress_bar.progress(30)
            status_text.markdown("### ✅ Specification created!")
            time.sleep(0.5)
            
            status_text.markdown("### ⚡ Step 2/3: Generating code in parallel...")
            
            def generate_frontend(spec):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert React developer. Generate complete, production-ready frontend code."},
                        {"role": "user", "content": f"""Generate a complete React TypeScript component for:

Module: {spec['moduleName']}
Features: {', '.join(spec['features'])}
Data Structure: {json.dumps(spec['dataStructure'], indent=2)}

Requirements: TypeScript, Tailwind CSS, form validation, error handling, responsive design, imports, comments."""}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            def generate_backend(spec):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert Node.js backend developer."},
                        {"role": "user", "content": f"""Generate complete Express.js TypeScript backend for:

Module: {spec['moduleName']}
Endpoints: {', '.join(spec['endpoints'])}
Data: {json.dumps(spec['dataStructure'], indent=2)}

Requirements: TypeScript, validation, error handling, Mongoose models, business logic, API docs."""}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            def generate_preview_html(spec):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Generate a complete working HTML demo."},
                        {"role": "user", "content": f"""Generate functional HTML for:

Module: {spec['moduleName']}
Features: {', '.join(spec['features'])}

Requirements: Single HTML file, Tailwind CDN, working features, mock data, modern design, responsive.
Start with <!DOCTYPE html>"""}
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
                return response.choices[0].message.content
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                future_frontend = executor.submit(generate_frontend, specification)
                future_backend = executor.submit(generate_backend, specification)
                future_preview = executor.submit(generate_preview_html, specification)
                
                progress_bar.progress(50)
                
                frontend_code = future_frontend.result()
                progress_bar.progress(65)
                status_text.markdown("### ⚡ Frontend done, backend in progress...")
                
                backend_code = future_backend.result()
                progress_bar.progress(80)
                status_text.markdown("### ⚡ Backend done, creating preview...")
                
                preview_html = future_preview.result()
                preview_html = preview_html.replace("```html", "").replace("```", "").strip()
                progress_bar.progress(100)
            
            st.session_state.frontend_code = frontend_code
            st.session_state.backend_code = backend_code
            st.session_state.preview_html = preview_html
            st.session_state.generated = True
            
            status_text.markdown("### ✅ Step 3/3: Complete!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            
            st.success("🎉 **Code Generated Successfully!** Scroll down to see results.")
            st.balloons()
            time.sleep(1)
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            progress_bar.empty()
            status_text.empty()

# Display Results
if st.session_state.generated:
    st.markdown("---")
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("# 🎉 Generated Results")
    
    with st.expander("📋 View Specification", expanded=False):
        if st.session_state.specification:
            spec_col1, spec_col2 = st.columns(2)
            
            with spec_col1:
                st.markdown(f"### {st.session_state.specification['moduleName']}")
                st.markdown(f"**Description:** {st.session_state.specification['description']}")
                
                st.markdown("**✨ Features:**")
                for idx, feature in enumerate(st.session_state.specification['features'], 1):
                    st.markdown(f"**{idx}.** {feature}")
            
            with spec_col2:
                st.markdown("**🛠️ Tech Stack:**")
                st.info(f"Frontend: {st.session_state.specification['techStack']['frontend']}")
                st.info(f"Backend: {st.session_state.specification['techStack']['backend']}")
                
                st.markdown("**🔌 Endpoints:**")
                for endpoint in st.session_state.specification['endpoints']:
                    st.code(endpoint)
            
            st.markdown("**📊 Data Structure:**")
            st.json(st.session_state.specification['dataStructure'])
    
    st.markdown("## 🎬 Live Preview")
    st.info("👇 This is your working application! Interact with it below.")
    
    if st.session_state.preview_html:
        try:
            b64_html = base64.b64encode(st.session_state.preview_html.encode()).decode()
            iframe_html = f'<iframe src="data:text/html;base64,{b64_html}" width="100%" height="800" style="border: 3px solid #667eea; border-radius: 15px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);"></iframe>'
            st.components.v1.html(iframe_html, height=820, scrolling=True)
        except Exception as e:
            st.error(f"Preview error: {str(e)}")
        
        st.download_button(
            label="📥 Download Live Preview HTML",
            data=st.session_state.preview_html,
            file_name=f"{st.session_state.specification['moduleName']}_preview.html",
            mime="text/html",
            use_container_width=True
        )
    
    st.markdown("---")
    st.markdown("## 💻 Source Code")
    
    tab1, tab2, tab3 = st.tabs(["⚛️ Frontend", "🖥️ Backend", "🌐 HTML Preview"])
    
    with tab1:
        st.markdown("### React TypeScript Component")
        st.code(st.session_state.frontend_code, language="typescript", line_numbers=True)
        st.download_button(
            "📥 Download Frontend",
            st.session_state.frontend_code,
            f"{st.session_state.specification['moduleName']}Component.tsx",
            "text/plain"
        )
    
    with tab2:
        st.markdown("### Express.js Backend")
        st.code(st.session_state.backend_code, language="typescript", line_numbers=True)
        st.download_button(
            "📥 Download Backend",
            st.session_state.backend_code,
            f"{st.session_state.specification['moduleName']}Routes.ts",
            "text/plain"
        )
    
    with tab3:
        st.markdown("### Standalone Demo")
        st.code(st.session_state.preview_html, language="html", line_numbers=True)
        st.download_button(
            "📥 Download HTML",
            st.session_state.preview_html,
            f"{st.session_state.specification['moduleName']}_demo.html",
            "text/html"
        )
    
    st.markdown("---")
    
    combined = f"""# {st.session_state.specification['moduleName']} - Complete Package

## Frontend Component
{st.session_state.frontend_code}

{'='*100}

## Backend API
{st.session_state.backend_code}

{'='*100}

## Preview HTML
{st.session_state.preview_html}

{'='*100}

## Specification
{json.dumps(st.session_state.specification, indent=2)}
"""
    
    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            "📦 Download Complete Package",
            combined,
            f"{st.session_state.specification['moduleName']}_complete.txt",
            "text/plain",
            use_container_width=True,
            type="primary"
        )
    
    with dl_col2:
        if st.button("🔄 Create New Project", use_container_width=True):
            st.session_state.generated = False
            st.session_state.user_input = ''
            st.session_state.transcript = ''
            st.session_state.trigger_generation = False
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 40px; background: rgba(255,255,255,0.95); border-radius: 20px; margin-top: 20px;'>
    <h3 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 1.8rem; margin-bottom: 15px;'>
        ✨ AI Code Generator
    </h3>
    <p style='color: #666; font-size: 1.1rem; margin: 10px 0;'>
        Voice → AI → Production-Ready Code
    </p>
    <p style='color: #999; font-size: 0.9rem;'>
        Powered by OpenAI GPT-4 & Whisper | Made with ❤️ using Streamlit
    </p>
</div>
""", unsafe_allow_html=True)