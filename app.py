import re
import streamlit as st
from main import generate_blog
from tools.image_tool import generate_thumbnail
from tools.whatsapp_tool import send_whatsapp
from tools.linkedin_tool import post_to_linkedin

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wersec Blog Generator",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #09090b;
    color: #fafafa;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #111113;
    border-right: 1px solid #27272a;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }

/* ── Sidebar brand header ── */
.sidebar-brand {
    padding: 1.5rem 1.25rem 1rem;
    border-bottom: 1px solid #27272a;
    margin-bottom: 1.25rem;
}
.sidebar-brand .brand-logo {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.25rem;
}
.sidebar-brand .brand-logo span {
    font-size: 1.15rem;
    font-weight: 700;
    color: #fafafa;
    letter-spacing: -0.02em;
}
.sidebar-brand p {
    font-size: 0.75rem;
    color: #71717a;
    margin: 0;
}

/* ── Sidebar section labels ── */
.sidebar-section {
    padding: 0 1.25rem;
    margin-bottom: 0.35rem;
}
.sidebar-section-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #52525b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.6rem;
    margin-top: 1.25rem;
}

/* ── Input fields ── */
.stTextArea textarea, .stSelectbox > div > div {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    color: #fafafa !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color 0.15s ease !important;
}
.stTextArea textarea:focus, .stSelectbox > div > div:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}
.stTextArea textarea::placeholder { color: #52525b !important; }
label { color: #a1a1aa !important; font-size: 0.8rem !important; font-weight: 500 !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
    border: none !important;
    cursor: pointer !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    padding: 0.6rem 1.25rem !important;
    width: 100% !important;
    box-shadow: 0 1px 3px rgba(37, 99, 235, 0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"]:disabled {
    background: #27272a !important;
    color: #52525b !important;
    box-shadow: none !important;
    transform: none !important;
}
.stButton > button[kind="secondary"] {
    background-color: #18181b !important;
    color: #a1a1aa !important;
    border: 1px solid #27272a !important;
    width: 100% !important;
}
.stButton > button[kind="secondary"]:hover {
    background-color: #27272a !important;
    color: #fafafa !important;
    border-color: #3f3f46 !important;
}

/* ── Publish buttons ── */
.btn-whatsapp > button {
    background-color: #14532d !important;
    color: #4ade80 !important;
    border: 1px solid #166534 !important;
}
.btn-whatsapp > button:hover {
    background-color: #166534 !important;
    color: #86efac !important;
}
.btn-linkedin > button {
    background-color: #1e3a5f !important;
    color: #60a5fa !important;
    border: 1px solid #1e40af !important;
}
.btn-linkedin > button:hover {
    background-color: #1e40af !important;
    color: #bfdbfe !important;
}

/* ── Download button ── */
.stDownloadButton > button {
    font-family: 'Inter', sans-serif !important;
    background-color: #18181b !important;
    color: #a1a1aa !important;
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}
.stDownloadButton > button:hover {
    background-color: #27272a !important;
    color: #fafafa !important;
}

/* ── Page header ── */
.page-header {
    padding: 2rem 0 1.5rem;
    border-bottom: 1px solid #27272a;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.page-header-left h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #fafafa;
    margin: 0 0 0.25rem;
    letter-spacing: -0.025em;
}
.page-header-left p { font-size: 0.875rem; color: #71717a; margin: 0; }
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}
.status-ready { background-color: #052e16; color: #4ade80; border: 1px solid #166534; }
.status-idle   { background-color: #18181b; color: #52525b; border: 1px solid #27272a; }

/* ── Cards ── */
.card {
    background-color: #111113;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 1.5rem;
}
.card-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #52525b;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

/* ── Blog content typography ── */
.blog-content { line-height: 1.75; color: #e4e4e7; }
.blog-content h1 { font-size: 1.5rem; font-weight: 700; color: #fafafa; margin: 0 0 1rem; letter-spacing: -0.025em; }
.blog-content h2 { font-size: 1.2rem; font-weight: 600; color: #fafafa; margin: 1.75rem 0 0.75rem; border-bottom: 1px solid #27272a; padding-bottom: 0.5rem; }
.blog-content h3 { font-size: 1rem; font-weight: 600; color: #d4d4d8; margin: 1.25rem 0 0.5rem; }
.blog-content p  { margin: 0 0 1rem; color: #a1a1aa; }
.blog-content ul, .blog-content ol { padding-left: 1.5rem; margin: 0 0 1rem; color: #a1a1aa; }
.blog-content li { margin-bottom: 0.4rem; }
.blog-content strong { color: #fafafa; font-weight: 600; }
.blog-content code { background: #27272a; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.85em; color: #7dd3fc; }
.blog-content blockquote { border-left: 3px solid #3b82f6; padding-left: 1rem; margin: 1rem 0; color: #71717a; font-style: italic; }

/* ── Empty state ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 5rem 2rem;
    text-align: center;
}
.empty-state-icon {
    width: 64px; height: 64px;
    background: linear-gradient(135deg, #1e3a5f, #1e40af);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.75rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 24px rgba(37, 99, 235, 0.2);
}
.empty-state h2 { font-size: 1.25rem; font-weight: 600; color: #fafafa; margin: 0 0 0.5rem; letter-spacing: -0.02em; }
.empty-state p  { font-size: 0.875rem; color: #71717a; margin: 0 0 2.5rem; max-width: 380px; }

/* ── Feature pills ── */
.feature-pills { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
.feature-pill {
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 999px;
    padding: 0.35rem 0.85rem;
    font-size: 0.75rem;
    color: #71717a;
    display: inline-flex; align-items: center; gap: 0.35rem;
}

/* ── Thumbnail placeholder ── */
.thumb-placeholder {
    background: linear-gradient(135deg, #18181b, #111113);
    border: 1px dashed #27272a;
    border-radius: 8px;
    padding: 2.5rem 1rem;
    text-align: center;
    color: #3f3f46;
    font-size: 0.8rem;
}

/* ── Meta tags ── */
.meta-tag {
    display: inline-flex; align-items: center; gap: 0.35rem;
    background-color: #18181b;
    border: 1px solid #27272a;
    border-radius: 6px;
    padding: 0.3rem 0.6rem;
    font-size: 0.78rem;
    color: #71717a;
    margin: 0.2rem 0.2rem 0.2rem 0;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #27272a !important; margin: 1rem 0 !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background-color: #18181b !important;
    border: 1px solid #27272a !important;
    border-radius: 8px !important;
    color: #a1a1aa !important;
    font-size: 0.875rem !important;
}
.streamlit-expanderContent { background-color: #111113 !important; border: 1px solid #27272a !important; border-top: none !important; }

/* ── Alerts ── */
.stSuccess > div { background-color: #052e16 !important; border: 1px solid #166534 !important; color: #4ade80 !important; border-radius: 8px !important; }
.stError   > div { background-color: #450a0a !important; border: 1px solid #991b1b !important; color: #f87171 !important; border-radius: 8px !important; }

/* ── Progress bar ── */
.stProgress > div > div > div > div { background: linear-gradient(90deg, #2563eb, #7c3aed) !important; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #3b82f6 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #09090b; }
::-webkit-scrollbar-thumb { background: #27272a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3f3f46; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _init_state():
    for k, v in {
        "blog_result": None,
        "blog_content": "",
        "thumbnail_path": None,
        "blog_ready": False,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-logo">
            <span>🔐 Wersec</span>
        </div>
        <p>Blog Generator — Internal Tool</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section"><div class="sidebar-section-label">Content</div></div>', unsafe_allow_html=True)

    topic = st.text_area(
        "Topic",
        placeholder="e.g. The rise of AI-powered phishing attacks in 2024",
        height=110,
        label_visibility="collapsed",
    )
    st.caption("Describe the cybersecurity topic to write about")

    st.markdown('<div class="sidebar-section"><div class="sidebar-section-label">Settings</div></div>', unsafe_allow_html=True)

    tone = st.selectbox("Tone", ["Professional", "Technical", "Casual"], index=0, label_visibility="visible")
    length = st.selectbox(
        "Length",
        ["Short  ·  300–500 words", "Medium  ·  600–900 words", "Long  ·  1000–1400 words"],
        index=1,
        label_visibility="visible",
    )
    length_key = length.split()[0].lower()

    st.markdown("<br>", unsafe_allow_html=True)
    generate_btn = st.button("Generate Blog Post", type="primary", disabled=not topic.strip())

    if st.session_state["blog_ready"]:
        st.markdown('<div class="sidebar-section"><div class="sidebar-section-label">Publish</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-whatsapp">', unsafe_allow_html=True)
        whatsapp_btn = st.button("Send via WhatsApp", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="btn-linkedin">', unsafe_allow_html=True)
        linkedin_btn = st.button("Post to LinkedIn", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        result = st.session_state["blog_result"]
        if result:
            st.markdown('<div class="sidebar-section"><div class="sidebar-section-label">Metadata</div></div>', unsafe_allow_html=True)
            with st.expander("Sources & Tools", expanded=False):
                if result.sources:
                    st.markdown("**Sources**")
                    for s in result.sources:
                        st.markdown(f'<span class="meta-tag">↗ {s}</span>', unsafe_allow_html=True)
                if result.tools_used:
                    st.markdown("<br>**Tools Used**", unsafe_allow_html=True)
                    for t in result.tools_used:
                        st.markdown(f'<span class="meta-tag">⚙ {t}</span>', unsafe_allow_html=True)
    else:
        whatsapp_btn = False
        linkedin_btn = False


# ── Main area ─────────────────────────────────────────────────────────────────
blog_ready = st.session_state["blog_ready"]
result = st.session_state.get("blog_result")

# Page header
status_html = (
    '<span class="status-pill status-ready">● Ready</span>'
    if blog_ready else
    '<span class="status-pill status-idle">● Idle</span>'
)
header_title = result.topic if (blog_ready and result) else "New Blog Post"
st.markdown(f"""
<div class="page-header">
    <div class="page-header-left">
        <h1>{header_title}</h1>
        <p>AI-generated cybersecurity content for LinkedIn</p>
    </div>
    <div>{status_html}</div>
</div>
""", unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
if not blog_ready:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-state-icon">✦</div>
        <h2>Start generating your blog post</h2>
        <p>Enter a topic in the sidebar, choose your tone and length, then hit Generate.</p>
        <div class="feature-pills">
            <span class="feature-pill">🔍 Web Research</span>
            <span class="feature-pill">🤖 Llama 3.3 70B</span>
            <span class="feature-pill">🎨 AI Thumbnail</span>
            <span class="feature-pill">💬 WhatsApp</span>
            <span class="feature-pill">💼 LinkedIn</span>
            <span class="feature-pill">⬇ Markdown Export</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Blog view ─────────────────────────────────────────────────────────────────
else:
    col_main, col_panel = st.columns([3, 1], gap="large")

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

    with col_panel:
        # Thumbnail
        st.markdown('<div class="card"><div class="card-label">Thumbnail</div>', unsafe_allow_html=True)
        if st.session_state["thumbnail_path"]:
            st.image(st.session_state["thumbnail_path"], use_container_width=True)
        else:
            st.markdown("""
            <div class="thumb-placeholder">
                <div style="font-size:2rem; margin-bottom:0.5rem;">🖼</div>
                <div>Add <code>TOGETHER_API_KEY</code> to .env to enable thumbnails</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Summary
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card"><div class="card-label">Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size:0.875rem; color:#a1a1aa; line-height:1.6; margin:0">{result.summary}</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ── Generate handler ──────────────────────────────────────────────────────────
if generate_btn and topic.strip():
    st.session_state["blog_ready"] = False
    prog = st.progress(0, text="Researching topic…")
    try:
        with st.spinner("Writing with Llama 3.3 70B…"):
            result = generate_blog(topic.strip(), tone.lower(), length_key)
        prog.progress(70, text="Generating thumbnail…")
        img_path = generate_thumbnail(topic.strip(), _slug(result.topic))
        prog.progress(100, text="Done!")

        st.session_state.update({
            "blog_result": result,
            "blog_content": result.full_content,
            "thumbnail_path": img_path,
            "blog_ready": True,
        })
        prog.empty()
        st.success("Blog generated successfully.")
        st.rerun()
    except Exception as e:
        prog.empty()
        st.error(f"Generation failed: {e}")


# ── WhatsApp handler ──────────────────────────────────────────────────────────
if whatsapp_btn and st.session_state["blog_ready"]:
    r = st.session_state["blog_result"]
    with st.spinner("Sending to WhatsApp…"):
        ok = send_whatsapp(r.topic, r.summary, r.sources)
    st.success("Sent to WhatsApp.") if ok else st.error("WhatsApp failed — check Twilio credentials in .env")


# ── LinkedIn handler ──────────────────────────────────────────────────────────
if linkedin_btn and st.session_state["blog_ready"]:
    r = st.session_state["blog_result"]
    with st.spinner("Posting to LinkedIn…"):
        ok = post_to_linkedin(r.topic, r.full_content, r.summary)
    st.success("Posted to LinkedIn.") if ok else st.error("LinkedIn failed — token may be expired (regenerate every 60 days)")
