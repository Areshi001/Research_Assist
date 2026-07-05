import streamlit as st
from ai_researcher_2 import INITIAL_PROMPT, advanced_graph, simple_graph
from pathlib import Path
import logging
import re
import uuid
from langchain_core.messages import AIMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Research AI Agent", page_icon="document", layout="wide")

# ── Custom CSS for Premium Academic UI ──
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    * { font-family: 'Inter', sans-serif; }

    /* CSS Variables for Dark/Light (Streamlit defaults to matching system preference if configured) */
    :root {
        --bg-color: #0D0D0D;
        --panel-bg: #17181B;
        --border-color: #2B2C2F;
        --gold: #E6B84C;
        --gold-glow: rgba(230, 184, 76, 0.2);
        --text-primary: #F5F5F5;
        --text-secondary: #777777;
        --user-msg-bg: rgba(255, 255, 255, 0.03);
    }
    
    @media (prefers-color-scheme: light) {
        :root {
            --bg-color: #FAF8F5;
            --panel-bg: #FFFFFF;
            --border-color: #E6D8B5;
            --gold: #D9A93E;
            --gold-glow: rgba(217, 169, 62, 0.2);
            --text-primary: #222222;
            --text-secondary: #666666;
            --user-msg-bg: rgba(0, 0, 0, 0.02);
        }
    }

    .stApp { 
        background: var(--bg-color) !important; 
    }
    
    .main .block-container { 
        max-width: 1000px; 
        padding-top: 2rem; 
        padding-bottom: 6rem;
    }

    /* ── Top Navigation (Simulated via standard container) ── */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--border-color);
    }
    .top-nav-left { font-weight: 600; color: var(--gold); display: flex; align-items: center; gap: 8px;}
    .top-nav-right { display: flex; gap: 15px; align-items: center; color: var(--text-secondary); font-size: 0.9rem;}
    .session-badge { background: rgba(16,185,129,0.1); border: 1px solid #10b981; color: #10b981; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; }
    .avatar-circle { width: 32px; height: 32px; border-radius: 50%; background: linear-gradient(135deg, var(--gold), #a855f7); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem;}

    /* ── Chat Input Restyling ── */
    .stChatInputContainer {
        background: var(--panel-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 18px !important;
        padding: 5px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    }
    .stChatInputContainer:focus-within {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 2px var(--gold-glow), 0 4px 20px rgba(0,0,0,0.2) !important;
    }
    .stChatInputContainer textarea { color: var(--text-primary) !important; font-size: 1rem !important; }

    /* ── Chat Messages ── */
    .stChatMessage { background: transparent !important; padding: 0 !important; margin-bottom: 1.5rem !important; }
    
    /* Assistant Messages */
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, var(--gold), #D4A63A) !important;
        border-radius: 50% !important;
    }
    [data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) [data-testid="stChatMessageContent"] {
        background: var(--panel-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        border-top-left-radius: 4px !important;
        padding: 1.2rem 1.5rem !important;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }
    
    /* User Messages (Right aligned) */
    [data-testid="chatAvatarIcon-user"] { display: none !important; } /* Hide user avatar for cleaner look */
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
    }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
        background: var(--user-msg-bg) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--gold) !important;
        border-radius: 16px !important;
        border-top-right-radius: 4px !important;
        padding: 1rem 1.25rem !important;
        color: var(--text-primary) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        margin-left: auto;
        max-width: 85%;
    }

    [data-testid="stChatMessageContent"] a { color: var(--gold) !important; text-decoration: none !important; border-bottom: 1px dashed var(--gold); }
    [data-testid="stChatMessageContent"] a:hover { color: #fff !important; }

    /* ── Hero Section (Animated) ── */
    .hero-container {
        text-align: center;
        padding: 4rem 0 3rem 0;
        position: relative;
    }
    .hero-icon {
        font-size: 2.2rem;
        font-weight: bold;
        color: var(--gold);
        animation: float 4s ease-in-out infinite;
        text-shadow: 0 0 20px var(--gold-glow);
        margin-bottom: 1rem;
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -1px;
        margin: 0;
    }
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }

    /* ── Popular Cards (Custom Buttons) ── */
    .popular-title { text-align: center; color: var(--gold); margin-bottom: 1.5rem; font-weight: 500;}
    
    div[data-testid="stButton"] button {
        background: var(--panel-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px !important;
        padding: 1.5rem 1rem !important;
        color: var(--text-primary) !important;
        height: 100% !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
        text-align: center !important;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stButton"] button p { font-size: 1rem !important; white-space: pre-wrap !important; line-height: 1.4 !important; }
    
    /* Hover Card Effects */
    div[data-testid="stButton"] button:hover {
        transform: translateY(-4px) !important;
        border-color: var(--gold) !important;
        box-shadow: 0 8px 25px var(--gold-glow) !important;
    }
    div[data-testid="stButton"] button:hover p { color: var(--gold) !important; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] { background: var(--bg-color) !important; border-right: 1px solid var(--border-color) !important; }
    .sidebar-logo { color: var(--gold); font-size: 1.2rem; font-weight: 600; margin-bottom: 2rem; display: flex; align-items: center; gap: 8px;}
    .sidebar-section { color: var(--text-secondary); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 2rem; margin-bottom: 0.8rem; font-weight: 600;}
    .sidebar-item { color: var(--text-primary); font-size: 0.9rem; padding: 8px 12px; border-radius: 8px; cursor: pointer; transition: 0.2s; display: flex; align-items: center; gap: 8px; margin-bottom: 2px;}
    .sidebar-item:hover { background: var(--panel-bg); color: var(--gold); }
    .sidebar-item.history:hover { background: rgba(255,255,255,0.05); }
    
    /* Mode badge styling */
    .stToggle label { color: var(--text-primary) !important; font-weight: 500 !important; }
    
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Session State Init ──
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "tool_log" not in st.session_state:
    st.session_state.tool_log = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "use_advanced" not in st.session_state:
    st.session_state.use_advanced = True
if "queued_prompt" not in st.session_state:
    st.session_state.queued_prompt = None
if "session_history" not in st.session_state:
    st.session_state.session_history = [] # Real history tracker

# ── Top Navigation ──
st.markdown("""
<div class="top-nav">
    <div class="top-nav-left">Research AI Agent</div>
    <div class="top-nav-right">
        <span class="session-badge">Session Active</span>
        <span>Theme</span>
        <div class="avatar-circle">RA</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──
with st.sidebar:
    st.markdown('<div class="sidebar-logo">Research AI</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="sidebar-section">AGENT MODE</div>', unsafe_allow_html=True)
    use_advanced = st.toggle(
        "Advanced — StateGraph",
        value=st.session_state.use_advanced,
        key="mode_toggle"
    )
    if use_advanced != st.session_state.use_advanced:
        st.session_state.use_advanced = use_advanced
        st.session_state.chat_history = []
        st.session_state.pdf_path = None
        st.session_state.tool_log = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("New Session", use_container_width=True):
        if st.session_state.chat_history:
             # Save current session to history before clearing
             title = st.session_state.chat_history[0]["content"][:30] + "..."
             st.session_state.session_history.insert(0, title)
        st.session_state.chat_history = []
        st.session_state.pdf_path = None
        st.session_state.tool_log = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    st.markdown('<div class="sidebar-section">HISTORY</div>', unsafe_allow_html=True)
    if len(st.session_state.session_history) == 0 and not st.session_state.chat_history:
        st.markdown('<div style="color:var(--text-secondary);font-size:0.8rem;padding-left:12px;">No recent history</div>', unsafe_allow_html=True)
    else:
        # Show active session if exists
        if st.session_state.chat_history:
            active_title = st.session_state.chat_history[0]["content"][:25] + "..."
            st.markdown(f'<div class="sidebar-item history">Document: {active_title} <span style="margin-left:auto;font-size:0.75rem;color:var(--text-secondary)">Now</span></div>', unsafe_allow_html=True)
        # Show previous sessions
        for hist in st.session_state.session_history[:5]:
            st.markdown(f'<div class="sidebar-item history">Document: {hist} <span style="margin-left:auto;font-size:0.75rem;color:var(--text-secondary)">Past</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">TOOLS</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-item">Search arXiv</div>
    <div class="sidebar-item">Read PDF</div>
    <div class="sidebar-item">Extract Text</div>
    <div class="sidebar-item">Write Paper (LaTeX)</div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="position:absolute;bottom:20px;width:100%;"><div class="sidebar-item">Settings</div></div>', unsafe_allow_html=True)


# ── Landing Page (Hero + Cards) ──
if len(st.session_state.chat_history) == 0:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-icon">Research AI</div>
        <h1 class="hero-title">Research AI Agent</h1>
        <p class="hero-subtitle">Your autonomous academic research assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="popular-title">Popular Options</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Literature Review\n\nSurvey and analyze\nexisting research", use_container_width=True):
            st.session_state.queued_prompt = "Conduct a comprehensive literature review on the latest advancements in "
            st.rerun()
        if st.button("Write Survey\n\nGenerate structured\nsurvey paper", use_container_width=True):
            st.session_state.queued_prompt = "Generate a structured survey paper on "
            st.rerun()
    with c2:
        if st.button("Explain Paper\n\nGet detailed\nexplanations", use_container_width=True):
            st.session_state.queued_prompt = "Please explain the key findings and methodology of the following paper: "
            st.rerun()
        if st.button("Generate BibTeX\n\nCreate citations\ninstantly", use_container_width=True):
            st.session_state.queued_prompt = "Generate BibTeX citations for the following research topics or papers: "
            st.rerun()
    with c3:
        if st.button("Compare Papers\n\nCompare methods,\nresults, and more", use_container_width=True):
            st.session_state.queued_prompt = "Compare the methods and results of the following approaches: "
            st.rerun()
        if st.button("Summarize PDF\n\nExtract key insights\nfrom PDFs", use_container_width=True):
            st.session_state.queued_prompt = "Read the following PDF and extract the key insights and conclusions: "
            st.rerun()

# ── Render Chat History ──
else:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # PDF download button
    if st.session_state.pdf_path and Path(st.session_state.pdf_path).exists():
        pdf_path = st.session_state.pdf_path
        pdf_name = Path(pdf_path).name
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        st.download_button(
            label=f"Download {pdf_name}",
            data=pdf_bytes,
            file_name=pdf_name,
            mime="application/pdf"
        )


# ── Handle Input ──
user_input = st.chat_input("What would you like to research?", disabled=st.session_state.processing)

# If a card was clicked, use its prompt instead of chat_input
if st.session_state.queued_prompt:
    user_input = st.session_state.queued_prompt
    st.session_state.queued_prompt = None

# If new input arrives, store it and rerun to clear the landing page
if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.pending_response = True
    st.session_state.tool_log = []
    st.session_state.pdf_path = None
    st.rerun()

# After rerun, if we have a pending response, stream it
if st.session_state.get("pending_response", False):
    st.session_state.pending_response = False
    st.session_state.processing = True

    chat_input_data = {
        "messages": [{"role": "system", "content": INITIAL_PROMPT}] + st.session_state.chat_history
    }

    graph = advanced_graph if st.session_state.use_advanced else simple_graph
    run_config = {"configurable": {"thread_id": st.session_state.thread_id}} if st.session_state.use_advanced else {}

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            for chunk, metadata in graph.stream(chat_input_data, run_config, stream_mode="messages"):
                # Accept both AIMessage and AIMessageChunk
                if hasattr(chunk, "content") and not hasattr(chunk, "tool_call_id"):
                    text_content = ""
                    if isinstance(chunk.content, str):
                        text_content = chunk.content
                    elif isinstance(chunk.content, list):
                        for block in chunk.content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                text_content += block.get("text", "")

                    if text_content:
                        full_response += text_content
                        response_placeholder.markdown(full_response + "|")

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            logger.error(error_msg, exc_info=True)
            response_placeholder.markdown(f"_{error_msg}_")
            full_response = error_msg

        if full_response:
            response_placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    # Check for generated PDF in final string
    if isinstance(full_response, str):
        pdf_matches = re.findall(r'output[\\/]paper_\d+_?\d*\.pdf', full_response)
        if pdf_matches:
            st.session_state.pdf_path = pdf_matches[-1].replace("\\", "/")

    st.session_state.processing = False
    st.rerun()
