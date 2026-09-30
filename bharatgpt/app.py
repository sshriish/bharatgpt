import os
import streamlit as st
from rag import *

st.set_page_config(page_title="BharatGPT", page_icon="🇮🇳", layout="centered")
st.title("🇮🇳 BharatGPT")
st.caption("Multilingual, source-grounded assistant for government services, schemes and grievances")

@st.cache_resource
def load_kb():
       return KnowledgeBase(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
kb = load_kb()
st.sidebar.write(f"Knowledge base: **{len(kb.chunks)}** chunks")
st.sidebar.warning("Student project. NOT an official government service. Verify every answer on the source link.")
st.sidebar.info("Answers come only from official documents in data/. Always verify on the source link.")

tab1, tab2 = st.tabs(["Ask a question", "File / track grievance"])
with tab1:
    q = st.text_input("Ask in English, Hindi, Tamil, Telugu, Kannada, Bengali, ...", placeholder="Am I eligible for PM-KISAN?")
    if q:
        lang = detect_lang(q)
        r = answer(kb, translate(q, lang, "en"))
        st.markdown(f"`Language: {LANG_NAMES[lang]}` · `Intent: {r['intent']}` · `Confidence: {r['confidence']:.2f}` · `{r['mode']}`")
        st.markdown(translate(r["answer"], "en", lang) if lang != "en" else r["answer"])
        for s in r["sources"]:
            st.markdown(f"Source: {s}")
        if r["intent"] == "grievance":
            st.warning("This looks like a complaint. Use the 'File / track grievance' tab.")
with tab2:
    st.warning("Demo only: complaints are NOT sent to any government body. Do not enter real personal details or sensitive information.")
    with st.form("g"):
        name = st.text_input("Your name"); dept = st.text_input("Department / scheme")
        text = st.text_area("Describe your issue")
        if st.form_submit_button("Register") and name and text:
            ref = register_grievance(name, dept or "Concerned Department", text, detect_lang(text))
            st.success(f"Registered. Reference ID: {ref}")
            st.code(draft_complaint(name, dept or "Concerned Department", text))
    ref = st.text_input("Track by reference ID")
    if ref:
        row = grievance_status(ref)
        st.write(f"Dept: {row[1]} · Status: **{row[2]}** · Filed: {row[3]}" if row else "Not found.")
