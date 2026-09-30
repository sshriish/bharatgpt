import os
import html
import streamlit as st
from rag import *

st.set_page_config(page_title="BharatGPT", page_icon="🇮🇳", layout="centered", initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@500;700;800&family=Noto+Sans:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Tamil:wght@400;600&family=Noto+Sans+Telugu:wght@400;600&family=Noto+Sans+Kannada:wght@400;600&family=Noto+Sans+Bengali:wght@400;600&display=swap');
:root{--ink:#1D2B64;--paper:#F5F7FC;--turmeric:#F5B301;--leaf:#0E7C4A;--line:#C9D1EA;--soft:#E7ECF9;}
.stApp,[data-testid="stHeader"]{background:var(--paper)!important;}
[data-testid="stSidebar"]{background:var(--soft)!important;}
.stApp,.stApp p,.stApp li,.stApp label,.stApp span,.stApp div{font-family:'Noto Sans','Noto Sans Devanagari','Noto Sans Tamil','Noto Sans Telugu','Noto Sans Kannada','Noto Sans Bengali',sans-serif;}
.stApp p,.stApp li,.stApp label,[data-testid="stSidebar"] *{color:var(--ink);}
footer,#MainMenu{visibility:hidden;}
.block-container{padding-top:2rem;max-width:760px;}
.hello{font-family:'Baloo 2',sans-serif;font-weight:700;font-size:1.05rem;color:var(--ink);opacity:.75;letter-spacing:.02em;}
.hello b{color:var(--turmeric);text-shadow:0 0 0 var(--ink);}
.hero h1{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:2.7rem;line-height:1.05;color:var(--ink);margin:.35rem 0 .5rem 0;}
.hero p{font-size:1.02rem;max-width:34rem;color:#3B4A85;margin:0 0 1.1rem 0;}
.flagbar{height:6px;border-radius:3px;background:linear-gradient(90deg,#FF9933 0 33.3%,#fff 33.3% 66.6%,#138808 66.6%);border:1px solid var(--line);margin:0 0 1.2rem 0;}
.stTabs [data-baseweb="tab-list"]{gap:.4rem;border-bottom:2px solid var(--line);}
.stTabs [data-baseweb="tab"]{font-family:'Baloo 2',sans-serif;font-weight:700;font-size:1.05rem;color:var(--ink);}
.stTabs [aria-selected="true"]{color:var(--ink)!important;border-bottom:4px solid var(--turmeric);}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"]{background:#fff!important;border-radius:14px!important;}
.stTextInput input,.stTextArea textarea{background:#fff!important;color:var(--ink)!important;font-size:1.1rem;}
[data-baseweb="input"],[data-baseweb="textarea"]{border:2px solid var(--ink)!important;}
.stButton>button,.stFormSubmitButton>button{background:#fff;color:var(--ink);border:1.5px dashed var(--ink);border-radius:10px;font-weight:600;text-align:left;min-height:3rem;}
.stButton>button:hover,.stFormSubmitButton>button:hover{background:var(--turmeric);border-style:solid;color:var(--ink);}
.stFormSubmitButton>button{background:var(--ink);color:#fff;border-style:solid;text-align:center;}
.stFormSubmitButton>button:hover{background:var(--leaf);color:#fff;}
.tryhead{font-family:'Baloo 2',sans-serif;font-weight:700;color:var(--ink);margin:.9rem 0 .2rem 0;}
.slip{background:#fff;border:2px solid var(--ink);border-radius:6px 6px 18px 18px;margin:1rem 0 .6rem 0;box-shadow:6px 6px 0 var(--turmeric);}
.slip-head{background:var(--ink);padding:.9rem 1.1rem;border-radius:3px 3px 0 0;}
.slip-title{font-family:'Baloo 2',sans-serif;font-weight:700;font-size:1.35rem;line-height:1.2;color:#fff;}
.chips{margin-top:.45rem;}
.chip{display:inline-block;background:rgba(255,255,255,.14);color:#fff;border-radius:99px;padding:.1rem .7rem;font-size:.78rem;margin-right:.4rem;}
.row{display:flex;gap:1rem;padding:.85rem 1.1rem;border-bottom:1.5px dotted var(--line);}
.lab{flex:0 0 8.2rem;font-family:'Baloo 2',sans-serif;font-weight:700;color:var(--ink);font-size:1rem;}
.txt{flex:1;color:#222B55;font-size:.95rem;line-height:1.55;white-space:pre-line;}
.foot{display:flex;flex-wrap:wrap;gap:.8rem;align-items:center;justify-content:space-between;padding:.8rem 1.1rem;}
.meter{font-size:.85rem;color:var(--ink);}
.dots i{display:inline-block;width:.7rem;height:.7rem;border-radius:50%;background:var(--line);margin-right:.2rem;vertical-align:middle;}
.dots i.on{background:var(--leaf);}
a.stamp{display:inline-block;background:var(--leaf);color:#fff!important;text-decoration:none;font-weight:600;padding:.45rem 1rem;border-radius:99px;border:2px solid var(--leaf);}
a.stamp:hover{background:#fff;color:var(--leaf)!important;}
.also{font-size:.88rem;color:#3B4A85;margin:.6rem 0 0 0;}
.sorry{background:#fff;border:2px dashed var(--ink);border-radius:14px;padding:1rem 1.2rem;margin-top:1rem;color:var(--ink);}
.steps{display:flex;gap:.6rem;margin:.6rem 0 1rem 0;flex-wrap:wrap;}
.step{flex:1;min-width:9rem;background:#fff;border:1.5px solid var(--line);border-radius:10px;padding:.55rem .8rem;color:var(--ink);font-size:.9rem;}
.step b{font-family:'Baloo 2',sans-serif;color:var(--leaf);}
.refbox{background:#fff;border:2px solid var(--leaf);border-radius:12px;padding:1rem 1.2rem;margin:.8rem 0;color:var(--ink);}
.refbox .id{font-family:'Baloo 2',sans-serif;font-weight:800;font-size:1.8rem;color:var(--leaf);}
.fine{font-size:.8rem;color:#5B6899;margin-top:1.5rem;}
@media(max-width:640px){.hero h1{font-size:2rem}.row{flex-direction:column;gap:.2rem}.lab{flex:none}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

LABELS = {"details": ("ℹ️", "About"), "description": ("ℹ️", "About"), "benefits": ("💰", "Benefits"),
          "eligibility": ("✅", "Who can apply"), "documents": ("📄", "Documents"), "documents_required": ("📄", "Documents"),
          "application": ("📝", "How to apply"), "how_to_apply": ("📝", "How to apply")}
EXAMPLES = ["PM Kisan eligibility", "Ayushman Bharat benefits", "Free LPG connection for women",
            "How to file an RTI?", "किसान योजना क्या है", "MGNREGA job card"]

@st.cache_resource
def load_kb():
    return KnowledgeBase(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
kb = load_kb()
e = html.escape

with st.sidebar:
    st.markdown("### How it works")
    st.markdown("1. Detects your language\n2. Finds the matching scheme in official data\n3. Shows the answer with its source link\n4. Says so when it does not know")
    st.markdown(f"**{len(kb.chunks):,}** text chunks from Central and State schemes (MyScheme.gov.in).")
    st.warning("Student project. Not an official government service. Always check the source link.")

st.markdown("""
<div class="hero">
  <div class="hello">नमस्ते &nbsp; வணக்கம் &nbsp; నమస్కారం &nbsp; ನಮಸ್ಕಾರ &nbsp; নমস্কার</div>
  <h1>Ask about any government scheme, in your language.</h1>
  <p>Find out who can apply, what you get and which papers you need. Every answer links to its source.</p>
  <div class="flagbar"></div>
</div>""", unsafe_allow_html=True)

def setq(t):
    st.session_state.q = t

def render_answer(q):
    lang = detect_lang(q)
    q_en = translate(q, lang, "en")
    r = answer(kb, q_en)
    if r["mode"] == "guardrail":
        st.markdown('<div class="sorry"><b>No matching scheme found.</b><br>I only answer from official scheme documents, so I will not guess. '
                    'Try the scheme name or a simple keyword such as farmer, pension, health or scholarship. '
                    'To report a problem, use the Grievance tab or CPGRAMS (pgportal.gov.in).</div>', unsafe_allow_html=True)
        return
    def tr(t): return translate(t, "en", lang) if lang != "en" else t
    merged = {}
    for f, t in r["sections"]:
        key = LABELS.get(f, ("📌", f.replace("_", " ").title()))
        merged[key] = (merged.get(key, "") + " " + t).strip()
    rows = ""
    for (ic, lab), t in merged.items():
        t = t if len(t) <= 600 else t[:600].rsplit(" ", 1)[0] + "…"
        rows += f'<div class="row"><div class="lab">{ic} {lab}</div><div class="txt">{e(tr(t))}</div></div>'
    if not rows:
        rows = f'<div class="row"><div class="lab">💬 Answer</div><div class="txt">{e(tr(r["answer"]))}</div></div>'
    c = r["confidence"]
    n, word = (3, "Strong match") if c >= 0.5 else (2, "Good match") if c >= 0.35 else (1, "Possible match. Check the source.")
    dots = "".join(f'<i class="{"on" if i < n else ""}"></i>' for i in range(3))
    links = "".join(f'<a class="stamp" href="{e(s)}" target="_blank" rel="noopener">Open official page</a> ' for s in r["sources"][:1] if s.startswith("http"))
    st.markdown(f"""<div class="slip"><div class="slip-head"><div class="slip-title">{e(r['title'] or '')}</div>
      <div class="chips"><span class="chip">{e(LANG_NAMES[lang])}</span><span class="chip">{e(r['intent'])}</span></div></div>
      {rows}<div class="foot"><div class="meter"><span class="dots">{dots}</span> {word}</div><div>{links}</div></div></div>""", unsafe_allow_html=True)
    also = [t for _, t in kb.top_schemes(expand_query(q_en), k=5) if t != r["title"]][:3]
    if also:
        st.markdown(f'<p class="also"><b>Also relevant:</b> {e(", ".join(also))}</p>', unsafe_allow_html=True)
    if r["intent"] == "grievance":
        st.info("This sounds like a complaint. Use the Grievance tab to write and track it.")

tab1, tab2 = st.tabs(["Ask a question", "Grievance"])
with tab1:
    q = st.text_input("Your question", key="q", placeholder="Type in English, हिंदी, தமிழ், తెలుగు, ಕನ್ನಡ, বাংলা...")
    if q.strip():
        render_answer(q.strip())
    else:
        st.markdown('<div class="tryhead">Try one of these</div>', unsafe_allow_html=True)
        cols = st.columns(2)
        for i, ex in enumerate(EXAMPLES):
            cols[i % 2].button(ex, key=f"ex{i}", on_click=setq, args=(ex,), use_container_width=True)

with tab2:
    st.markdown('<div class="steps"><div class="step"><b>1.</b> Describe the problem</div><div class="step"><b>2.</b> Get a ready letter</div><div class="step"><b>3.</b> Track with your ID</div></div>', unsafe_allow_html=True)
    st.warning("Demo only. Complaints are not sent to any government office. Do not enter real personal details.")
    with st.form("g"):
        name = st.text_input("Your name"); dept = st.text_input("Department or scheme")
        text = st.text_area("What went wrong?")
        if st.form_submit_button("Register complaint") and name and text:
            d = dept or "Concerned Department"
            ref = register_grievance(name, d, text, detect_lang(text))
            st.markdown(f'<div class="refbox">Complaint registered. Your reference ID:<div class="id">{ref}</div></div>', unsafe_allow_html=True)
            with st.expander("See your draft letter", expanded=True):
                st.code(draft_complaint(name, d, text), language=None)
    ref = st.text_input("Already registered? Enter your reference ID")
    if ref:
        row = grievance_status(ref)
        st.markdown(f'<div class="refbox">Department: {e(row[1])}<br>Status: <b>{e(row[2])}</b><br>Filed: {e(row[3])}</div>' if row else '<div class="sorry">No complaint found with that ID.</div>', unsafe_allow_html=True)

st.markdown('<div class="fine">Student project. Not an official government service. Data from MyScheme.gov.in (Kaggle). Verify every answer on the source page.</div>', unsafe_allow_html=True)
