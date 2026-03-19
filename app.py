import pathlib
import streamlit as st
from main import _make_llm, _research, _write_blog, _optimize_linkedin_post, _slug
from tools.image_tool import generate_thumbnail
from tools.whatsapp_tool import send_whatsapp
from tools.linkedin_tool import post_to_linkedin

st.set_page_config(
    page_title="Wersec — Blog Generator",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system ──────────────────────────────────────────────────────────────
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: #f8fafc;
    color: #334155;
    -webkit-font-smoothing: antialiased;
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.35; }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
@keyframes borderGlow {
    0%, 100% { box-shadow: 0 0 12px rgba(139, 92, 246, 0.25); }
    50%       { box-shadow: 0 0 24px rgba(34, 211, 238, 0.25); }
}
@keyframes gridFade {
    from { opacity: 0; }
    to   { opacity: 1; }
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 2rem 3rem !important;
    max-width: 80rem !important;
    animation: fadeIn 0.4s ease;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e2e8f0;
    width: 16rem;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Sidebar brand ── */
.brand-header {
    padding: 1.75rem 1.5rem 1.25rem;
    border-bottom: 1px solid #e2e8f0;
}
.brand-name {
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #1D4ED8;
    background: none;
    -webkit-text-fill-color: initial;
    animation: none;
}
.brand-sub {
    font-size: 0.72rem;
    color: #64748b;
    margin-top: 0.2rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── Sidebar section label ── */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 1.25rem 1.5rem 0.5rem;
}

/* ── Input fields ── */
.stTextArea textarea {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 0.375rem !important;
    color: #1f2937 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: #1D4ED8 !important;
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.2) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #94a3b8 !important; }

.stSelectbox > div > div {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 0.375rem !important;
    color: #1f2937 !important;
    font-size: 0.875rem !important;
}

label, .stSelectbox label {
    color: #334155 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    border-radius: 0.375rem !important;
    transition: all 0.2s ease !important;
    border: 1px solid transparent !important;
    letter-spacing: 0.01em !important;
}

.stButton > button:focus-visible {
    outline: none !important;
    border-color: #1D4ED8 !important;
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.2) !important;
}

.stButton > button:disabled {
    opacity: 0.5 !important;
    cursor: not-allowed !important;
}

/* Primary — purple gradient */
.stButton > button[kind="primary"] {
    background: #1D4ED8 !important;
    border-color: #1D4ED8 !important;
    color: #ffffff !important;
    padding: 0.65rem 1.5rem !important;
    width: 100% !important;
    box-shadow: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1E40AF !important;
    border-color: #1E40AF !important;
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.18) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"]:disabled {
    background: #1D4ED8 !important;
    border-color: #1D4ED8 !important;
    color: #ffffff !important;
    opacity: 0.5 !important;
    cursor: not-allowed !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Secondary */
.stButton > button[kind="secondary"] {
    background-color: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #cbd5e1 !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #f1f5f9 !important;
    color: #1f2937 !important;
    border-color: #cbd5e1 !important;
}

/* LinkedIn button */
.btn-linkedin .stButton > button {
    background: #1D4ED8 !important;
    color: #ffffff !important;
    border: 1px solid #1D4ED8 !important;
    width: 100% !important;
    box-shadow: none !important;
}
.btn-linkedin .stButton > button:hover {
    background: #1E40AF !important;
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.18) !important;
    transform: translateY(-1px) !important;
}

/* WhatsApp button */
.btn-whatsapp .stButton > button {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #cbd5e1 !important;
    width: 100% !important;
    box-shadow: none !important;
}
.btn-whatsapp .stButton > button:hover {
    background: #f1f5f9 !important;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08) !important;
    transform: translateY(-1px) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    font-family: 'Inter', sans-serif !important;
    background-color: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 0.375rem !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stDownloadButton > button:hover {
    background-color: #f1f5f9 !important;
    color: #1f2937 !important;
    border-color: #cbd5e1 !important;
}

/* ── Page header ── */
.page-header {
    padding: 2rem 0 1.75rem;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 2rem;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    animation: fadeInUp 0.4s ease;
}
.page-header h1 {
    font-size: 1.875rem;
    font-weight: 700;
    color: #1f2937;
    letter-spacing: -0.03em;
    margin-bottom: 0.3rem;
    line-height: 1.2;
}
.page-header p { font-size: 0.875rem; color: #64748b; }

/* ── Status badges ── */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.125rem 0.625rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.badge-ready {
    background: #ECFDF5;
    color: #047857;
    border: 1px solid #6EE7B7;
}
.badge-ready::before {
    content: '';
    width: 6px; height: 6px;
    background: #10B981;
    border-radius: 50%;
    animation: pulse 2s ease infinite;
    display: inline-block;
}
.badge-idle {
    background: #FFFBEB;
    color: #B45309;
    border: 1px solid #FCD34D;
}
.badge-idle::before {
    content: '';
    width: 6px; height: 6px;
    background: #FBBF24;
    border-radius: 50%;
    display: inline-block;
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 1.5rem;
    animation: fadeInUp 0.4s ease;
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
}
.card:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.08);
}
.card-label {
    font-size: 1rem;
    font-weight: 600;
    color: #334155;
    letter-spacing: -0.01em;
    padding-bottom: 1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid #f1f5f9;
}

/* ── Gradient card (featured) ── */
.card-gradient {
    background: linear-gradient(135deg, #0d0d24, #080818);
    border: 1px solid transparent;
    background-clip: padding-box;
    border-radius: 14px;
    padding: 1.5rem;
    position: relative;
    animation: fadeInUp 0.4s ease;
    animation: borderGlow 4s ease infinite;
}

/* ── Blog content typography ── */
.blog-content { line-height: 1.75; color: #334155; }
.blog-content h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1f2937;
    margin: 0 0 1.25rem;
    letter-spacing: -0.025em;
}
.blog-content h2 {
    font-size: 1.15rem;
    font-weight: 600;
    color: #0f172a;
    margin: 2rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #e2e8f0;
}
.blog-content h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #1f2937;
    margin: 1.5rem 0 0.5rem;
}
.blog-content p  { margin: 0 0 1rem; color: #64748b; }
.blog-content ul, .blog-content ol { padding-left: 1.5rem; margin: 0 0 1rem; color: #64748b; }
.blog-content li { margin-bottom: 0.5rem; }
.blog-content strong { color: #0f172a; font-weight: 600; }
.blog-content em    { color: #1D4ED8; font-style: italic; }
.blog-content code  {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    padding: 0.15rem 0.45rem;
    border-radius: 5px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82em;
    color: #1D4ED8;
}
.blog-content blockquote {
    border-left: 3px solid #1D4ED8;
    padding: 0.5rem 0 0.5rem 1.25rem;
    margin: 1.25rem 0;
    color: #475569;
    font-style: italic;
}
.blog-content a { color: #1D4ED8; text-decoration: none; }
.blog-content a:hover { color: #1E40AF; }

/* ── LinkedIn post editor ── */
.linkedin-editor textarea {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 0.375rem !important;
    color: #1f2937 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    line-height: 1.65 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.linkedin-editor textarea:focus {
    border-color: #1D4ED8 !important;
    box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.2) !important;
}
.char-count {
    font-size: 0.72rem;
    color: #334155;
    text-align: right;
    margin-top: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
}
.char-count.warn { color: #fbbf24; }
.char-count.over { color: #ef4444; }

/* ── Empty state ── */
.empty-root {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 72vh;
    text-align: center;
    animation: fadeIn 0.6s ease;
    position: relative;
}
.empty-grid {
    position: absolute;
    inset: 0;
    background: #f8fafc;
    border-radius: 12px;
    pointer-events: none;
}
.empty-icon {
    width: 72px; height: 72px;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 20px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1.5rem;
    font-size: 1.75rem;
    position: relative;
    z-index: 1;
    box-shadow: 0 4px 14px rgba(29, 78, 216, 0.08);
}
.empty-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1f2937;
    letter-spacing: -0.025em;
    margin-bottom: 0.6rem;
    position: relative;
    z-index: 1;
}
.empty-sub {
    font-size: 0.9rem;
    color: #64748b;
    margin-bottom: 2.5rem;
    max-width: 400px;
    line-height: 1.65;
    position: relative;
    z-index: 1;
}
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    max-width: 560px;
    position: relative;
    z-index: 1;
}
.feature-card {
    background: #080818;
    border: 1px solid #1a1a40;
    border-radius: 12px;
    padding: 1rem;
    text-align: left;
    transition: border-color 0.2s, transform 0.2s;
}
.feature-card:hover {
    border-color: #252560;
    transform: translateY(-2px);
}
.feature-card-label {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    margin-bottom: 0.2rem;
}
.feature-card-desc {
    font-size: 0.7rem;
    color: #334155;
    line-height: 1.4;
}
.fc-purple .feature-card-label { color: #a78bfa; }
.fc-cyan   .feature-card-label { color: #22d3ee; }
.fc-green  .feature-card-label { color: #34d399; }
.fc-amber  .feature-card-label { color: #fbbf24; }
.fc-blue   .feature-card-label { color: #60a5fa; }
.fc-rose   .feature-card-label { color: #fb7185; }

/* ── Thumbnail placeholder ── */
.thumb-placeholder {
    background: #f8fafc;
    border: 1px dashed #cbd5e1;
    border-radius: 0.375rem;
    padding: 3rem 1rem;
    text-align: center;
    color: #64748b;
    font-size: 0.8rem;
    line-height: 1.5;
}

/* ── Meta tag ── */
.meta-tag {
    display: inline-flex; align-items: center;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 6px;
    padding: 0.25rem 0.6rem;
    font-size: 0.75rem;
    color: #1D4ED8;
    margin: 0.2rem 0.2rem 0.2rem 0;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Dividers ── */
hr { border: none; border-top: 1px solid #e2e8f0 !important; margin: 1rem 0 !important; }

/* ── Alerts ── */
.stSuccess > div {
    background: #ECFDF5 !important;
    border: 1px solid #6EE7B7 !important;
    color: #047857 !important;
    border-radius: 0.75rem !important;
}
.stError > div {
    background: #FEF2F2 !important;
    border: 1px solid #FECACA !important;
    color: #B91C1C !important;
    border-radius: 0.75rem !important;
}
.stWarning > div {
    background: #FFFBEB !important;
    border: 1px solid #FCD34D !important;
    color: #B45309 !important;
    border-radius: 0.75rem !important;
}
.stInfo > div {
    background: #EFF6FF !important;
    border: 1px solid #BFDBFE !important;
    color: #1D4ED8 !important;
    border-radius: 0.75rem !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div > div {
    background: #1D4ED8 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #1D4ED8 !important; }

/* ── Status widget ── */
[data-testid="stStatusWidget"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 0.75rem !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 0.75rem !important;
    color: #475569 !important;
    font-size: 0.82rem !important;
}
.streamlit-expanderContent {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-top: none !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f8fafc; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

@media (max-width: 640px) {
    [data-testid="stSidebar"] { display: none; }
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {
    "blog_result": None,
    "blog_content": "",
    "thumbnail_path": None,
    "blog_ready": False,
    "linkedin_post_text": "",
    "topic_input": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-header">
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-md bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 font-bold text-sm">
                W
            </div>
            <div>
                <div class="brand-name">WERSEC</div>
                <div class="brand-sub">Content Intelligence Platform</div>
            </div>
        </div>
    </div>
    <div class="px-6 pt-6">
        <div class="text-xs font-semibold uppercase tracking-widest text-slate-400">Workspace</div>
        <div class="mt-4 space-y-2">
            <div class="flex items-center gap-4 px-4 py-2 rounded-md bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-700">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 18h6M10 22h4a2 2 0 0 0 2-2v-1H8v1a2 2 0 0 0 2 2ZM7 14V4a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v10l-4 4-4-4Z" />
                </svg>
                <span class="text-sm font-semibold">Generate</span>
            </div>
            <div class="flex items-center gap-4 px-4 py-2 rounded-md text-slate-600 hover:bg-slate-50 font-medium border-l-4 border-transparent transition-colors">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 7h8M8 12h8M8 17h8M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
                </svg>
                <span class="text-sm font-medium">Posts</span>
            </div>
            <div class="flex items-center gap-4 px-4 py-2 rounded-md text-slate-600 hover:bg-slate-50 font-medium border-l-4 border-transparent transition-colors">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.757.426 1.757 2.924 0 3.35a1.724 1.724 0 0 0-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 0 0-2.572 1.065c-.426 1.757-2.924 1.757-3.35 0a1.724 1.724 0 0 0-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 0 0-1.065-2.572c-1.757-.426-1.757-2.924 0-3.35a1.724 1.724 0 0 0 1.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.61 2.296.07 2.572-1.065Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                </svg>
                <span class="text-sm font-medium">Analytics</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="px-6 pt-6 text-xs uppercase tracking-widest font-semibold text-slate-400">Content</div>', unsafe_allow_html=True)

    topic = st.text_area(
        "Topic",
        placeholder="e.g. The rise of AI-powered phishing attacks in 2025",
        height=120,
        label_visibility="visible",
        key="topic_input",
    )
    st.caption("Enter a cybersecurity topic to generate a full blog post.")

    st.markdown('<div class="px-6 pt-6 text-xs uppercase tracking-widest font-semibold text-slate-400">Settings</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        tone = st.selectbox("Tone", ["Professional", "Technical", "Casual"], index=0)
    with col_b:
        length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)

    length_map = {"Short": "300-500 words", "Medium": "600-900 words", "Long": "1000-1400 words"}
    word_count = length_map[length]

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("Generate Blog Post", type="primary", disabled=not topic.strip())

    if st.session_state["blog_ready"]:
        st.markdown('<div class="px-6 pt-6 text-xs uppercase tracking-widest font-semibold text-slate-400">Publish</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-linkedin">', unsafe_allow_html=True)
        linkedin_btn = st.button("Post to LinkedIn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-whatsapp">', unsafe_allow_html=True)
        whatsapp_btn = st.button("Send via WhatsApp", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        result = st.session_state["blog_result"]
        if result and (result.sources or result.tools_used):
            st.markdown('<div class="px-6 pt-6 text-xs uppercase tracking-widest font-semibold text-slate-400">Metadata</div>', unsafe_allow_html=True)
            with st.expander("Sources & Tools", expanded=False):
                if result.sources:
                    st.markdown("**Sources**")
                    for s in result.sources:
                        st.markdown(f'<span class="meta-tag">{s}</span>', unsafe_allow_html=True)
                if result.tools_used:
                    st.markdown("<br>**Tools Used**", unsafe_allow_html=True)
                    for t in result.tools_used:
                        st.markdown(f'<span class="meta-tag">{t}</span>', unsafe_allow_html=True)
    else:
        linkedin_btn = False
        whatsapp_btn = False

    st.markdown("""
    <div class="px-6 pt-8 mt-6 border-t border-slate-200">
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 font-semibold">
                VK
            </div>
            <div class="min-w-0">
                <div class="text-sm font-semibold text-slate-800 truncate">Vasanth Kumar</div>
                <div class="text-xs font-medium text-slate-500 truncate">Admin</div>
            </div>
        </div>
          <div class="mt-4 flex items-center gap-4">
            <div class="w-10 h-10 rounded-md border border-slate-200 bg-white flex items-center justify-center text-slate-600 hover:bg-slate-50 transition" title="Settings" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.757.426 1.757 2.924 0 3.35a1.724 1.724 0 0 0-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 0 0-2.572 1.065c-.426 1.757-2.924 1.757-3.35 0a1.724 1.724 0 0 0-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 0 0-1.065-2.572c-1.757-.426-1.757-2.924 0-3.35a1.724 1.724 0 0 0 1.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.61 2.296.07 2.572-1.065Z" />
                </svg>
            </div>
            <div class="w-10 h-10 rounded-md border border-slate-200 bg-white flex items-center justify-center text-slate-600 hover:bg-slate-50 transition" title="Logout" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0-4-4m4 4H7m6 4v1a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-8a2 2 0 0 0-2 2v1" />
                </svg>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Main area ──────────────────────────────────────────────────────────────────
blog_ready = st.session_state["blog_ready"]
result = st.session_state.get("blog_result")

st.markdown("""
<div class="bg-white border-b border-slate-200">
  <div class="flex items-center justify-between max-w-7xl mx-auto px-8 py-4">
    <div class="flex items-center gap-4">
      <button class="sidebar-toggle md:hidden w-10 h-10 rounded-md border border-slate-200 bg-white text-slate-700 flex items-center justify-center hover:bg-slate-50 transition" onclick="window.__wersToggleSidebar && window.__wersToggleSidebar()"
        aria-label="Open sidebar" type="button">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <div class="hidden sm:block">
        <div class="text-sm font-semibold text-slate-700">Wersec</div>
        <div class="text-xs font-medium text-slate-500">Blog Generator</div>
      </div>
    </div>

    <div class="flex items-center gap-4">
      <div class="relative hidden lg:block w-96 max-w-full">
        <input type="text" placeholder="Search" aria-label="Search"
          class="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 bg-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
        />
      </div>

      <button type="button"
        class="relative w-10 h-10 rounded-md border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 transition"
        aria-label="Notifications">
        <span class="absolute -top-1 -right-1 bg-blue-700 text-white text-xs font-semibold rounded-full px-1.5 py-0.5">
          3
        </span>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5 mx-auto" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0 1 18 14.158V11a6.002 6.002 0 0 0-4-5.659V4a2 2 0 1 0-4 0v1.341C7.01 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0a3 3 0 0 1-6 0" />
        </svg>
      </button>

      <div class="w-10 h-10 rounded-full bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-700 font-semibold text-sm">
        VK
      </div>
    </div>
  </div>
</div>

<script>
  window.__wersToggleSidebar = function () {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (!sidebar) return;
    const isHidden = window.getComputedStyle(sidebar).display === 'none';
    sidebar.style.display = isHidden ? 'block' : 'none';
  }
</script>
""", unsafe_allow_html=True)

# Page header
badge_html = (
    '<span class="badge badge-ready">Ready</span>'
    if blog_ready else
    '<span class="badge badge-idle">Idle</span>'
)
header_title = result.topic if (blog_ready and result) else "New Blog Post"
st.markdown(f"""
<div class="page-header">
    <div>
        <h1>{header_title}</h1>
        <p>AI-generated cybersecurity content — Wersec</p>
    </div>
    <div>{badge_html}</div>
</div>
""", unsafe_allow_html=True)


# ── Empty state ────────────────────────────────────────────────────────────────
if not blog_ready:
    st.markdown("""
    <div class="empty-root">
        <div class="empty-icon">✦</div>
        <div class="empty-title">Generate your next blog post</div>
        <div class="empty-sub">
            Enter a cybersecurity topic in the sidebar, select your tone and length, then generate.
            Wersec will research, write the blog, optimize the LinkedIn post, and create a thumbnail.
        </div>
    </div>
    """, unsafe_allow_html=True)

    sample_topic = "The rise of AI-powered phishing attacks in 2025"
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Try sample topic", type="primary", use_container_width=True):
            st.session_state["topic_input"] = sample_topic
            st.rerun()


# ── Blog view ──────────────────────────────────────────────────────────────────
else:
    if result is None:
        st.session_state["blog_ready"] = False
        st.rerun()
    sources_count = len(result.sources) if result.sources else 0
    tools_count = len(result.tools_used) if result.tools_used else 0
    words_count = len(result.full_content.split()) if result.full_content else 0
    linkedin_chars = len(result.linkedin_post or "") if result.linkedin_post is not None else 0

    st.markdown(f"""
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-blue-50 rounded-md p-2 border border-blue-100 text-blue-700">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 14l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-sm text-slate-500 font-medium">Sources</div>
            </div>
          </div>
          <div class="text-xs font-medium text-green-700 flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 10l5-5 5 5M12 5v14"/>
            </svg>
            +{max(1, sources_count // 2)}%
          </div>
        </div>
        <div class="mt-4 text-2xl font-bold text-slate-800">{sources_count}</div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-blue-50 rounded-md p-2 border border-blue-100 text-blue-700">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m2 5H7a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2Z"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-sm text-slate-500 font-medium">Tools used</div>
            </div>
          </div>
          <div class="text-xs font-medium text-green-700 flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 10l5-5 5 5M12 5v14"/>
            </svg>
            +{max(1, tools_count // 2)}%
          </div>
        </div>
        <div class="mt-4 text-2xl font-bold text-slate-800">{tools_count}</div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-blue-50 rounded-md p-2 border border-blue-100 text-blue-700">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-sm text-slate-500 font-medium">Blog length</div>
            </div>
          </div>
          <div class="text-xs font-medium text-green-700 flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 10l5-5 5 5M12 5v14"/>
            </svg>
            On track
          </div>
        </div>
        <div class="mt-4 text-2xl font-bold text-slate-800">{words_count}</div>
      </div>

      <div class="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-blue-50 rounded-md p-2 border border-blue-100 text-blue-700">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M8 12h8M8 16h8M10 4h10a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1h6Z"/>
              </svg>
            </div>
            <div class="min-w-0">
              <div class="text-sm text-slate-500 font-medium">LinkedIn chars</div>
            </div>
          </div>
          <div class="text-xs font-medium text-green-700 flex items-center gap-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 10l5-5 5 5M12 5v14"/>
            </svg>
            Ready
          </div>
        </div>
        <div class="mt-4 text-2xl font-bold text-slate-800">{linkedin_chars}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([3, 1], gap="large")

    with col_main:
        st.markdown('<div class="card"><div class="card-label">Blog Post</div><div class="blog-content">', unsafe_allow_html=True)
        st.markdown(st.session_state["blog_content"])
        st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="Download as Markdown",
            data=st.session_state["blog_content"],
            file_name=f"{_slug(result.topic)}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_side:
        # Thumbnail
        st.markdown('<div class="card"><div class="card-label">Thumbnail</div>', unsafe_allow_html=True)
        if st.session_state["thumbnail_path"]:
            st.image(st.session_state["thumbnail_path"], use_container_width=True)
        else:
            st.markdown("""
            <div class="thumb-placeholder">
                No thumbnail generated.<br>
                Check GOOGLE_API_KEY in .env
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # LinkedIn post editor
        if st.session_state["linkedin_post_text"]:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="card"><div class="card-label">LinkedIn Post — Edit before publishing</div>', unsafe_allow_html=True)
            st.markdown('<div class="linkedin-editor">', unsafe_allow_html=True)
            edited_post = st.text_area(
                "LinkedIn post",
                value=st.session_state["linkedin_post_text"],
                height=320,
                label_visibility="visible",
                key="linkedin_post_editor",
            )
            char_count = len(edited_post)
            char_class = "over" if char_count > 3000 else "warn" if char_count > 2500 else ""
            st.markdown(
                f'<div class="char-count {char_class}">{char_count} / 3000 characters</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div></div>", unsafe_allow_html=True)

        # Summary
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card"><div class="card-label">Summary</div>', unsafe_allow_html=True)
        st.markdown(
            f'<p style="font-size:0.875rem; color:#94a3b8; line-height:1.7; margin:0">{result.summary}</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-sm">
          <div class="flex items-center justify-between gap-4 p-4 border-b border-slate-200">
            <div class="flex-1">
              <input
                type="text"
                placeholder="Search status"
                aria-label="Search status"
                class="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 bg-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              />
            </div>
            <div class="w-40">
              <select
                aria-label="Filter status"
                class="w-full border border-slate-300 rounded-md px-3 py-2 text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              >
                <option>All stages</option>
                <option>Active</option>
                <option>Pending</option>
                <option>In progress</option>
              </select>
            </div>
          </div>

          <div class="overflow-x-auto">
            <table class="min-w-full">
              <thead class="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500 border-b border-slate-200">
                <tr>
                  <th class="text-left px-4 py-3">Stage</th>
                  <th class="text-left px-4 py-3">Status</th>
                  <th class="text-right px-4 py-3 w-20">Action</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr class="group hover:bg-blue-50 transition">
                  <td class="px-4 py-3 text-sm text-slate-700">Research</td>
                  <td class="px-4 py-3 text-sm text-slate-700">
                    <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200">Active</span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <button type="button" class="text-slate-400 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white p-1 rounded-md" aria-label="View stage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M1.5 12s4.5-7.5 10.5-7.5S22.5 12 22.5 12s-4.5 7.5-10.5 7.5S1.5 12 1.5 12Z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr class="group hover:bg-blue-50 transition">
                  <td class="px-4 py-3 text-sm text-slate-700">Writing</td>
                  <td class="px-4 py-3 text-sm text-slate-700">
                    <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200">Active</span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <button type="button" class="text-slate-400 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white p-1 rounded-md" aria-label="View stage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M1.5 12s4.5-7.5 10.5-7.5S22.5 12 22.5 12s-4.5 7.5-10.5 7.5S1.5 12 1.5 12Z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr class="group hover:bg-blue-50 transition">
                  <td class="px-4 py-3 text-sm text-slate-700">Optimization</td>
                  <td class="px-4 py-3 text-sm text-slate-700">
                    <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200">Active</span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <button type="button" class="text-slate-400 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white p-1 rounded-md" aria-label="View stage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M1.5 12s4.5-7.5 10.5-7.5S22.5 12 22.5 12s-4.5 7.5-10.5 7.5S1.5 12 1.5 12Z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
                <tr class="group hover:bg-blue-50 transition">
                  <td class="px-4 py-3 text-sm text-slate-700">Thumbnail</td>
                  <td class="px-4 py-3 text-sm text-slate-700">
                    <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-green-50 text-green-700 border border-green-200">Active</span>
                  </td>
                  <td class="px-4 py-3 text-right">
                    <div class="flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <button type="button" class="text-slate-400 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-white p-1 rounded-md" aria-label="View stage">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-4 h-4" aria-hidden="true">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M1.5 12s4.5-7.5 10.5-7.5S22.5 12 22.5 12s-4.5 7.5-10.5 7.5S1.5 12 1.5 12Z"/>
                          <path stroke-linecap="round" stroke-linejoin="round" d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/>
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="flex items-center justify-end gap-4 p-4 text-sm text-slate-600">
            <button type="button" class="border border-slate-300 rounded-md px-3 py-2 bg-white hover:bg-slate-50 transition focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Previous page">Prev</button>
            <button type="button" class="border border-slate-300 rounded-md px-3 py-2 bg-white hover:bg-slate-50 transition focus:outline-none focus:ring-2 focus:ring-blue-500" aria-label="Next page">Next</button>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── Generate handler ───────────────────────────────────────────────────────────
if generate_btn and topic.strip():
    st.session_state["blog_ready"] = False
    st.session_state["linkedin_post_text"] = ""

    prog = st.progress(0)
    try:
        with st.status("Running agents...", expanded=True) as gen_status:
            st.write("Agent 1 — Researching topic across the web...")
            prog.progress(10)
            llm = _make_llm()
            research = _research(topic.strip(), llm)
            prog.progress(35)

            st.write("Agent 2 — Writing the blog post...")
            result = _write_blog(topic.strip(), tone.lower(), word_count, research, llm)
            prog.progress(65)

            st.write("Agent 3 — Optimising post for LinkedIn...")
            result.linkedin_post = _optimize_linkedin_post(
                result.topic, result.summary, result.full_content, llm
            )
            prog.progress(80)

            st.write("Generating thumbnail with Google Imagen 3...")
            img_path = generate_thumbnail(topic.strip(), _slug(result.topic))
            prog.progress(95)

            # Save markdown output
            pathlib.Path("outputs").mkdir(exist_ok=True)
            (pathlib.Path("outputs") / f"{_slug(result.topic)}.md").write_text(
                result.full_content, encoding="utf-8"
            )
            prog.progress(100)
            gen_status.update(label="Blog generated successfully", state="complete", expanded=False)

        st.session_state.update({
            "blog_result": result,
            "blog_content": result.full_content,
            "thumbnail_path": img_path,
            "blog_ready": True,
            "linkedin_post_text": result.linkedin_post,
        })
        prog.empty()
        st.success("Blog generated. Review the LinkedIn post on the right before publishing.")
        st.rerun()

    except Exception as e:
        prog.empty()
        st.error(f"Generation failed: {e}")


# ── LinkedIn handler ───────────────────────────────────────────────────────────
if linkedin_btn and st.session_state["blog_ready"]:
    r = st.session_state["blog_result"]
    # Use the edited post text if the editor exists, otherwise the stored one
    post_text = st.session_state.get("linkedin_post_editor") or st.session_state["linkedin_post_text"]
    thumbnail = st.session_state.get("thumbnail_path")

    with st.status("Posting to LinkedIn...", expanded=True) as post_status:
        ok = post_to_linkedin(
            topic=r.topic,
            full_content=r.full_content,
            summary=r.summary,
            linkedin_post=post_text,
            image_path=thumbnail,
        )
        post_status.update(label="Posting finished", state="complete", expanded=False)
    if ok:
        st.success("Posted to LinkedIn successfully.")
    else:
        st.error("LinkedIn failed — check LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN in .env")


# ── WhatsApp handler ───────────────────────────────────────────────────────────
if whatsapp_btn and st.session_state["blog_ready"]:
    r = st.session_state["blog_result"]
    with st.status("Sending to WhatsApp...", expanded=True) as wa_status:
        ok = send_whatsapp(r.topic, r.summary, r.sources)
        wa_status.update(label="Message delivery status received", state="complete", expanded=False)
    if ok:
        st.success("Sent to WhatsApp.")
    else:
        st.error("WhatsApp failed — check TWILIO_* credentials in .env")


if __name__ == "__main__":
    import sys
    print("Run the app with: streamlit run app.py", file=sys.stderr)
    print("Or use: ./run.sh", file=sys.stderr)
    sys.exit(1)
