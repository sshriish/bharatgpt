import os
import html
import hashlib
from urllib.parse import urlparse
import streamlit as st
from rag import *
import ui

st.set_page_config(
    page_title="BharatGPT",
    page_icon="🇮🇳",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(ui.CSS, unsafe_allow_html=True)
e = html.escape

LABELS = {
    "details": "About the scheme",
    "description": "About the scheme",
    "benefits": "Benefits",
    "eligibility": "Who can apply",
    "documents": "Documents needed",
    "documents_required": "Documents needed",
    "application": "How to apply",
    "how_to_apply": "How to apply"
}

EXAMPLES = [
    "PM Kisan eligibility",
    "Ayushman Bharat benefits",
    "Free LPG connection for women",
    "How to file an RTI",
    "किसान योजना क्या है",
    "MGNREGA job card"
]

CATEGORIES = {
    "Farmers": "schemes for farmers",
    "Health": "health insurance scheme",
    "Women and children": "schemes for women and children",
    "Students": "scholarship for students",
    "Housing": "housing scheme for poor",
    "Pension and seniors": "old age pension scheme"
}


@st.cache_resource
def load_kb():
    return KnowledgeBase(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "data"
        )
    )


kb = load_kb()


def tx_many(items, src, dest):
    """
    Batch translate.

    This RAISES on failure so errors are visible
    and never cached.
    """
    if src == dest:
        return items

    from deep_translator import GoogleTranslator

    out = GoogleTranslator(
        source=src,
        target=dest
    ).translate_batch(items)

    return [o or i for o, i in zip(out, items)]


@st.cache_data(show_spinner=False, ttl=3600)
def run_query(q):
    lang = detect_lang(q)

    # Translate user's question to English
    q_en = tx_many([q], lang, "en")[0]

    # Run RAG pipeline
    r = answer(kb, q_en)

    if r["mode"] == "guardrail":
        return {"ok": False}

    # Merge sections with the same label
    merged = {}

    for f, t in r["sections"]:
        lab = LABELS.get(
            f,
            f.replace("_", " ").title()
        )

        merged[lab] = (
            merged.get(lab, "") + " " + t
        ).strip()

    # Prepare answer sections
    items = list(merged.items()) or [
        ("Answer", r["answer"])
    ]

    # For eligibility questions, show "Who can apply" first
    if r["intent"] == "eligibility":
        items.sort(key=lambda x: x[0] != "Who can apply")

    # LLM summary (only exists when ANTHROPIC_API_KEY is set)
    summary = r["answer"] if r["mode"] == "llm-rag" else ""

    labels = [l for l, _ in items]

    texts = [
        t if len(t) <= 1500
        else t[:1500].rsplit(" ", 1)[0] + "…"
        for _, t in items
    ]

    # Confidence
    c = r["confidence"]

    n, word = (
        (3, "Strong match")
        if c >= 0.5
        else (2, "Good match")
        if c >= 0.35
        else (1, "Possible match, please check the source")
    )

    # Get human-readable intent label
    intent_label = ui.INTENTS.get(
        r["intent"],
        r["intent"]
    )

    # Translate title, confidence text, intent,
    # section labels, section contents and summary together
    out = tx_many(
        [r["title"] or "Answer", word, intent_label]
        + labels
        + texts
        + ([summary] if summary else []),
        "en",
        lang
    )

    title, word_t, intent_t = out[:3]

    labels_t = out[
        3:3 + len(labels)
    ]

    texts_t = out[
        3 + len(labels):
        3 + len(labels) + len(texts)
    ]

    summary_t = out[-1] if summary else ""

    # Find official source link
    link = next(
        (
            s
            for s in r["sources"]
            if s.startswith("http")
        ),
        ""
    )

    # Find related schemes
    also = [
        t
        for _, t in kb.top_schemes(
            expand_query(q_en),
            k=5
        )
        if t != r["title"]
    ][:3]

    return {
        "ok": True,
        "title": title,
        "title_en": r["title"],
        "summary": summary_t,
        "lang": LANG_NAMES[lang],
        "intent": r["intent"],
        "intent_label": intent_t,
        "secs": list(
            zip(labels_t, texts_t)
        ),
        "n": n,
        "word": word_t,
        "link": link,
        "also": also
    }


def setq(t):
    st.session_state.q = t


def render_answer(q):
    try:
        with st.spinner(
            "Reading official scheme documents…"
        ):
            d = run_query(q)

    except Exception as ex:
        st.markdown(
            ui.note(
                "<b>Translation is not working.</b><br>"
                "BharatGPT needs the "
                "<code>deep-translator</code> package "
                "and an internet connection to answer in "
                "other languages. Run "
                "<code>pip install -r bharatgpt/requirements.txt</code>, "
                "or try again in a minute if Google is "
                "rate-limiting."
            ),
            unsafe_allow_html=True
        )

        st.caption(
            f"Technical detail: "
            f"{type(ex).__name__}: {ex}"
        )

        return

    if not d["ok"]:
        st.markdown(
            ui.note(
                "<b>No matching scheme found.</b><br>"
                "BharatGPT answers only from official scheme "
                "documents, so it will not guess. "
                "Try the scheme name or a simple keyword such "
                "as farmer, pension, health or scholarship. "
                "To report a problem, use the Grievance tab "
                "or CPGRAMS (pgportal.gov.in)."
            ),
            unsafe_allow_html=True
        )
        return

    host = (
        urlparse(d["link"])
        .netloc
        .replace("www.", "")
        or "official site"
    )

    # Use translated intent label here
    st.markdown(
        ui.card(
            d["title"],
            d["lang"],
            d["intent_label"],
            d["secs"],
            d["n"],
            d["word"],
            host,
            d["link"],
            d["summary"]
        ),
        unsafe_allow_html=True
    )

    # Unique key for feedback/download/related buttons
    k = hashlib.md5(
        q.encode()
    ).hexdigest()[:8]

    txt = (
        d["title"]
        + "\n\n"
        + "\n\n".join(
            f"{l}\n{t}"
            for l, t in d["secs"]
        )
        + f"\n\nSource: {d['link']}"
    )

    c1, c2, c3 = st.columns(
        [1, 1.2, 3]
    )

    with c1:
        fb = st.feedback(
            "thumbs",
            key=f"fb_{k}"
        )

    with c2:
        st.download_button(
            "Save answer",
            txt,
            file_name="bharatgpt-answer.txt",
            key=f"dl_{k}",
            use_container_width=True
        )

    if fb is not None:
        if st.session_state.get(f"fbd_{k}") != fb:
            log_feedback(q, d["title_en"], fb)
            st.session_state[f"fbd_{k}"] = fb

        st.caption(
            "Thanks, your feedback helps improve answers."
            if fb == 1
            else
            "Sorry about that. Try the scheme's official "
            "name for a better match."
        )

    # Related schemes
    if d["also"]:
        st.markdown(
            ui.head("Also relevant"),
            unsafe_allow_html=True
        )

        cols = st.columns(
            len(d["also"])
        )

        for i, t in enumerate(d["also"]):
            cols[i].button(
                t,
                key=f"al{k}{i}",
                on_click=setq,
                args=(t,),
                use_container_width=True
            )

    # Grievance information
    if d["intent"] == "grievance":
        st.info(
            "This sounds like a complaint. "
            "Use the Grievance tab to write and track it."
        )


# ---------------------------------------------------------
# MAIN UI
# ---------------------------------------------------------

st.markdown(
    ui.TOPBAR + ui.hero(kb.n_schemes, len(LANG_NAMES) - 1),
    unsafe_allow_html=True
)

st.session_state.setdefault(
    "history",
    []
)


tab1, tab2 = st.tabs(
    ["Ask a question", "Grievance"]
)


# =========================================================
# TAB 1: ASK A QUESTION
# =========================================================

with tab1:

    q = st.text_input(
        "Your question",
        key="q",
        label_visibility="collapsed",
        placeholder=(
            "Search a scheme or ask a question, "
            "in any language"
        )
    )

    if q.strip():

        q = q.strip()

        # Add to recent searches
        if q not in st.session_state.history:
            st.session_state.history = (
                [q] + st.session_state.history
            )[:4]

        st.button(
            "Clear search",
            on_click=setq,
            args=("")
        )

        render_answer(q)

    else:

        # Browse by need
        st.markdown(
            ui.head("Browse by need"),
            unsafe_allow_html=True
        )

        cols = st.columns(3)

        for i, (label, query) in enumerate(
            CATEGORIES.items()
        ):
            cols[i % 3].button(
                label,
                key=f"cat{i}",
                on_click=setq,
                args=(query,),
                use_container_width=True
            )

        # Popular questions
        st.markdown(
            ui.head("Popular questions"),
            unsafe_allow_html=True
        )

        cols = st.columns(3)

        for i, ex in enumerate(EXAMPLES):
            cols[i % 3].button(
                ex,
                key=f"ex{i}",
                on_click=setq,
                args=(ex,),
                use_container_width=True
            )

        # Recent searches
        if st.session_state.history:

            st.markdown(
                ui.head("Your recent searches"),
                unsafe_allow_html=True
            )

            cols = st.columns(2)

            for i, h in enumerate(
                st.session_state.history
            ):
                cols[i % 2].button(
                    h,
                    key=f"h{i}",
                    on_click=setq,
                    args=(h,),
                    use_container_width=True
                )


# =========================================================
# TAB 2: GRIEVANCE
# =========================================================

with tab2:

    st.markdown(
        ui.note(
            "<b>Demo only.</b> Complaints are not sent to "
            "any government office. Please do not enter "
            "real personal details."
        ),
        unsafe_allow_html=True
    )

    with st.form("g"):

        a, b = st.columns(2)

        name = a.text_input(
            "Your name"
        )

        dept = b.text_input(
            "Department or scheme"
        )

        text = st.text_area(
            "What went wrong?",
            height=140,
            placeholder=(
                "Describe the problem, when it happened "
                "and what you expected."
            )
        )

        if st.form_submit_button(
            "Register complaint"
        ):

            if name and text:

                d = dept or "Concerned Department"

                ref = register_grievance(
                    name,
                    d,
                    text,
                    detect_lang(text)
                )

                st.toast(
                    "Complaint registered",
                    icon="✅"
                )

                st.markdown(
                    ui.refbox(
                        f'Complaint registered. '
                        f'Save your reference ID'
                        f'<div class="id">{ref}</div>'
                    ),
                    unsafe_allow_html=True
                )

                with st.expander(
                    "Draft letter",
                    expanded=True
                ):
                    st.code(
                        draft_complaint(
                            name,
                            d,
                            text
                        ),
                        language=None
                    )

            else:

                st.warning(
                    "Please enter your name and "
                    "describe the problem."
                )

    # Track complaint
    st.markdown(
        ui.head("Track a complaint"),
        unsafe_allow_html=True
    )

    ref = st.text_input(
        "Reference ID",
        label_visibility="collapsed",
        placeholder="Enter your reference ID"
    )

    if ref:

        row = grievance_status(
            ref.strip()
        )

        if row:

            steps = [
                "registered",
                "in review",
                "resolved"
            ]

            idx = (
                steps.index(
                    str(row[2]).lower()
                )
                if str(row[2]).lower() in steps
                else 0
            )

            st.markdown(
                ui.refbox(
                    f'{e(row[1])}<br>'
                    f'Status: <b>{e(row[2])}</b>'
                    f' &nbsp;·&nbsp; '
                    f'Filed: {e(row[3])}'
                    + ui.tracker(idx)
                ),
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                ui.note(
                    "No complaint found with that ID."
                ),
                unsafe_allow_html=True
            )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="fine">'
    'BharatGPT is a student project and not an official '
    'government service. Data: MyScheme.gov.in via Kaggle. '
    'Please verify every answer on the official page.'
    '</div>',
    unsafe_allow_html=True
)
