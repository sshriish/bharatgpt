import os
import html
import streamlit as st
from rag import *
import ui

st.set_page_config(page_title="BharatGPT", page_icon="🇮🇳", layout="centered", initial_sidebar_state="collapsed")
st.markdown(ui.CSS, unsafe_allow_html=True)
e = html.escape

LABELS = {"details": "About the scheme", "description": "About the scheme", "benefits": "Benefits",
          "eligibility": "Who can apply", "documents": "Documents needed", "documents_required": "Documents needed",
          "application": "How to apply", "how_to_apply": "How to apply"}
EXAMPLES = ["PM Kisan eligibility", "Ayushman Bharat benefits", "Free LPG connection for women",
            "How to file an RTI", "किसान योजना क्या है", "MGNREGA job card"]

@st.cache_resource
def load_kb():
    return KnowledgeBase(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
kb = load_kb()

st.markdown(ui.HERO, unsafe_allow_html=True)

def setq(t):
    st.session_state.q = t

def render_answer(q):
    lang = detect_lang(q)
    q_en = translate(q, lang, "en")
    r = answer(kb, q_en)
    if r["mode"] == "guardrail":
        st.markdown(ui.note("<b>No matching scheme found.</b><br>BharatGPT answers only from official scheme documents, so it will not guess. "
                            "Try the scheme name or a simple keyword such as farmer, pension, health or scholarship. "
                            "To report a problem, use the Grievance tab or CPGRAMS (pgportal.gov.in)."), unsafe_allow_html=True)
        return
    tr = (lambda t: translate(t, "en", lang)) if lang != "en" else (lambda t: t)
    merged = {}
    for f, t in r["sections"]:
        lab = LABELS.get(f, f.replace("_", " ").title())
        merged[lab] = (merged.get(lab, "") + " " + t).strip()
    secs = []
    for lab, t in merged.items():
        t = t if len(t) <= 600 else t[:600].rsplit(" ", 1)[0] + "…"
        secs.append((lab, tr(t)))
    if not secs:
        secs = [("Answer", tr(r["answer"]))]
    c = r["confidence"]
    n, word = (3, "Strong match") if c >= 0.5 else (2, "Good match") if c >= 0.35 else (1, "Possible match. Please check the source.")
    link = next((s for s in r["sources"] if s.startswith("http")), "")
    st.markdown(ui.card(r["title"] or "", LANG_NAMES[lang], r["intent"], secs, n, word, link), unsafe_allow_html=True)
    also = [t for _, t in kb.top_schemes(expand_query(q_en), k=5) if t != r["title"]][:3]
    if also:
        st.markdown(f'<p class="also">Also relevant: {e(", ".join(also))}</p>', unsafe_allow_html=True)
    if r["intent"] == "grievance":
        st.info("This sounds like a complaint. Use the Grievance tab to write and track it.")

tab1, tab2 = st.tabs(["Ask a question", "Grievance"])
with tab1:
    q = st.text_input("Your question", key="q", label_visibility="collapsed",
                      placeholder="Ask about a scheme, in any language")
    if q.strip():
        render_answer(q.strip())
    else:
        st.markdown(ui.LANGS, unsafe_allow_html=True)
        st.markdown('<div class="tryhead">Try asking</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, ex in enumerate(EXAMPLES):
            cols[i % 3].button(ex, key=f"ex{i}", on_click=setq, args=(ex,), use_container_width=True)

with tab2:
    st.markdown(ui.note("<b>Demo only.</b> Complaints are not sent to any government office. Please do not enter real personal details."), unsafe_allow_html=True)
    with st.form("g"):
        name = st.text_input("Your name"); dept = st.text_input("Department or scheme")
        text = st.text_area("What went wrong?")
        if st.form_submit_button("Register complaint") and name and text:
            d = dept or "Concerned Department"
            ref = register_grievance(name, d, text, detect_lang(text))
            st.markdown(ui.refbox(f'Complaint registered. Your reference ID<div class="id">{ref}</div>'), unsafe_allow_html=True)
            with st.expander("Draft letter", expanded=True):
                st.code(draft_complaint(name, d, text), language=None)
    ref = st.text_input("Track a complaint", placeholder="Enter your reference ID")
    if ref:
        row = grievance_status(ref)
        st.markdown(ui.refbox(f'{e(row[1])}<br>Status: <b>{e(row[2])}</b><br>Filed: {e(row[3])}') if row else ui.note("No complaint found with that ID."), unsafe_allow_html=True)

st.markdown('<div class="fine">BharatGPT is a student project and not an official government service. Data: MyScheme.gov.in via Kaggle. Please verify every answer on the official page.</div>', unsafe_allow_html=True)
