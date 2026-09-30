import os
import html
import hashlib
from urllib.parse import urlparse
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
CATEGORIES = {"Farmers": "schemes for farmers", "Health": "health insurance scheme", "Women and children": "schemes for women and children",
              "Students": "scholarship for students", "Housing": "housing scheme for poor", "Pension and seniors": "old age pension scheme"}

@st.cache_resource
def load_kb():
    return KnowledgeBase(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
kb = load_kb()

@st.cache_data(show_spinner=False, ttl=3600)
def run_query(q):
    """Runs the full pipeline once per question; reruns (feedback clicks etc.) are instant."""
    lang = detect_lang(q)
    r = answer(kb, translate(q, lang, "en"))
    if r["mode"] == "guardrail":
        return {"ok": False}
    tr = (lambda t: translate(t, "en", lang)) if lang != "en" else (lambda t: t)
    merged = {}
    for f, t in r["sections"]:
        lab = LABELS.get(f, f.replace("_", " ").title())
        merged[lab] = (merged.get(lab, "") + " " + t).strip()
    secs = [(lab, tr(t if len(t) <= 600 else t[:600].rsplit(" ", 1)[0] + "…")) for lab, t in merged.items()]
    if not secs:
        secs = [("Answer", tr(r["answer"]))]
    c = r["confidence"]
    n, word = (3, "Strong match") if c >= 0.5 else (2, "Good match") if c >= 0.35 else (1, "Possible match, please check the source")
    link = next((s for s in r["sources"] if s.startswith("http")), "")
    also = [t for _, t in kb.top_schemes(expand_query(translate(q, lang, "en")), k=5) if t != r["title"]][:3]
    return {"ok": True, "title": r["title"] or "", "lang": LANG_NAMES[lang], "intent": r["intent"],
            "secs": secs, "n": n, "word": word, "link": link, "also": also}

def setq(t):
    st.session_state.q = t

def render_answer(q):
    with st.spinner("Reading official scheme documents…"):
        d = run_query(q)
    if not d["ok"]:
        st.markdown(ui.note("<b>No matching scheme found.</b><br>BharatGPT answers only from official scheme documents, so it will not guess. "
                            "Try the scheme name or a simple keyword such as farmer, pension, health or scholarship. "
                            "To report a problem, use the Grievance tab or CPGRAMS (pgportal.gov.in)."), unsafe_allow_html=True)
        return
    host = urlparse(d["link"]).netloc.replace("www.", "") or "official site"
    st.markdown(ui.card(d["title"], d["lang"], d["intent"], d["secs"], d["n"], d["word"], host, d["link"]), unsafe_allow_html=True)
    k = hashlib.md5(q.encode()).hexdigest()[:8]
    txt = d["title"] + "\n\n" + "\n\n".join(f"{l}\n{t}" for l, t in d["secs"]) + f"\n\nSource: {d['link']}"
    c1, c2, c3 = st.columns([1, 1.2, 3])
    with c1:
        fb = st.feedback("thumbs", key=f"fb_{k}")
    with c2:
        st.download_button("Save answer", txt, file_name="bharatgpt-answer.txt", key=f"dl_{k}", use_container_width=True)
    if fb is not None:
        st.caption("Thanks, your feedback helps improve answers." if fb == 1 else "Sorry about that. Try the scheme's official name for a better match.")
    if d["also"]:
        st.markdown(ui.head("Also relevant"), unsafe_allow_html=True)
        cols = st.columns(len(d["also"]))
        for i, t in enumerate(d["also"]):
            cols[i].button(t, key=f"al{k}{i}", on_click=setq, args=(t,), use_container_width=True)
    if d["intent"] == "grievance":
        st.info("This sounds like a complaint. Use the Grievance tab to write and track it.")

st.markdown(ui.TOPBAR + ui.HERO, unsafe_allow_html=True)
st.session_state.setdefault("history", [])

tab1, tab2 = st.tabs(["Ask a question", "Grievance"])
with tab1:
    q = st.text_input("Your question", key="q", label_visibility="collapsed",
                      placeholder="Search a scheme or ask a question, in any language")
    if q.strip():
        q = q.strip()
        if q not in st.session_state.history:
            st.session_state.history = ([q] + st.session_state.history)[:4]
        st.button("Clear search", on_click=setq, args=("",))
        render_answer(q)
    else:
        st.markdown(ui.head("Browse by need"), unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (label, query) in enumerate(CATEGORIES.items()):
            cols[i % 3].button(label, key=f"cat{i}", on_click=setq, args=(query,), use_container_width=True)
        st.markdown(ui.head("Popular questions"), unsafe_allow_html=True)
        cols = st.columns(3)
        for i, ex in enumerate(EXAMPLES):
            cols[i % 3].button(ex, key=f"ex{i}", on_click=setq, args=(ex,), use_container_width=True)
        if st.session_state.history:
            st.markdown(ui.head("Your recent searches"), unsafe_allow_html=True)
            cols = st.columns(2)
            for i, h in enumerate(st.session_state.history):
                cols[i % 2].button(h, key=f"h{i}", on_click=setq, args=(h,), use_container_width=True)

with tab2:
    st.markdown(ui.note("<b>Demo only.</b> Complaints are not sent to any government office. Please do not enter real personal details."), unsafe_allow_html=True)
    with st.form("g"):
        a, b = st.columns(2)
        name = a.text_input("Your name")
        dept = b.text_input("Department or scheme")
        text = st.text_area("What went wrong?", height=140, placeholder="Describe the problem, when it happened and what you expected.")
        if st.form_submit_button("Register complaint"):
            if name and text:
                d = dept or "Concerned Department"
                ref = register_grievance(name, d, text, detect_lang(text))
                st.toast("Complaint registered", icon="✅")
                st.markdown(ui.refbox(f'Complaint registered. Save your reference ID<div class="id">{ref}</div>'), unsafe_allow_html=True)
                with st.expander("Draft letter", expanded=True):
                    st.code(draft_complaint(name, d, text), language=None)
            else:
                st.warning("Please enter your name and describe the problem.")
    st.markdown(ui.head("Track a complaint"), unsafe_allow_html=True)
    ref = st.text_input("Reference ID", label_visibility="collapsed", placeholder="Enter your reference ID")
    if ref:
        row = grievance_status(ref.strip())
        if row:
            steps = ["registered", "in review", "resolved"]
            idx = steps.index(str(row[2]).lower()) if str(row[2]).lower() in steps else 0
            st.markdown(ui.refbox(f'{e(row[1])}<br>Status: <b>{e(row[2])}</b> &nbsp;·&nbsp; Filed: {e(row[3])}' + ui.tracker(idx)), unsafe_allow_html=True)
        else:
            st.markdown(ui.note("No complaint found with that ID."), unsafe_allow_html=True)

st.markdown('<div class="fine">BharatGPT is a student project and not an official government service. Data: MyScheme.gov.in via Kaggle. Please verify every answer on the official page.</div>', unsafe_allow_html=True)
