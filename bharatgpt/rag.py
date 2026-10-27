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


_LAST_ERR = ["unknown"]
SEP = "\n###\n"


MM_CODES = {"en": "en-GB", "hi": "hi-IN", "bn": "bn-IN", "pa": "pa-IN", "gu": "gu-IN",
            "or": "or-IN", "ta": "ta-IN", "te": "te-IN", "kn": "kn-IN", "ml": "ml-IN",
            "mr": "mr-IN", "ur": "ur-PK"}


def _tx_google(text, src, dest):
    from deep_translator import GoogleTranslator
    return GoogleTranslator(source=src, target=dest).translate(text) or text


def _tx_claude(text, src, dest):
    """Used only if ANTHROPIC_API_KEY is set. Keeps the ### separators."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("no ANTHROPIC_API_KEY")
    import anthropic
    msg = anthropic.Anthropic(api_key=key).messages.create(
        model=os.getenv("BHARATGPT_MODEL", "claude-sonnet-5-5"), max_tokens=4000,
        system=f"Translate the user's text from {LANG_NAMES[src]} to {LANG_NAMES[dest]}. "
               "Keep every line that is exactly ### unchanged. Output only the translation.",
        messages=[{"role": "user", "content": text}])
    return msg.content[0].text


def _tx_mymemory(text, src, dest):
    """Free backup (no key). 500-char limit per request, so split into pieces."""
    import re
    from deep_translator import MyMemoryTranslator
    tr = MyMemoryTranslator(source=MM_CODES[src], target=MM_CODES[dest])
    out = []
    for block in text.split(SEP):
        pieces, cur = [], ""
        for sent in re.split(r"(?<=[.!?।])\s+", block):
            while len(sent) > 450:
                pieces.append(sent[:450]); sent = sent[450:]
            if len(cur) + len(sent) > 450:
                pieces.append(cur); cur = sent
            else:
                cur = (cur + " " + sent).strip()
        if cur:
            pieces.append(cur)
        out.append(" ".join(tr.translate(p) for p in pieces if p.strip()))
    return SEP.join(out)


@st.cache_data(show_spinner=False, ttl=86400, max_entries=2000)
def _tx_cached(text, src, dest):
    """Try Google, then Claude (if key set), then MyMemory. Raises if all fail,
    so failures are never cached."""
    errs = []
    for fn in (_tx_google, _tx_claude, _tx_mymemory):
        try:
            return fn(text, src, dest)
        except Exception as ex:
            if fn is not _tx_claude:
                errs.append(f"{fn.__name__[4:]}: {type(ex).__name__}")
    _LAST_ERR[0] = " | ".join(errs)
    raise RuntimeError(_LAST_ERR[0])


def tx_many(items, src, dest):
    """
    Fast translation: strings are packed into a few big requests (about 1-2 per
    answer instead of ~12). Stops at the first hard failure and falls back to
    English for the rest; raises only if nothing could be translated.
    """
    import re

    if src == dest:
        return items

    out = list(items)
    todo = [i for i, t in enumerate(items) if t and t.strip() and not t.strip().isdigit()]

    # pack into chunks of <= 4000 chars
    chunks, cur, size = [], [], 0
    for i in todo:
        if cur and size + len(items[i]) > 4000:
            chunks.append(cur)
            cur, size = [], 0
        cur.append(i)
        size += len(items[i]) + len(SEP)
    if cur:
        chunks.append(cur)

    done = 0
    for ch in chunks:
        try:
            res = _tx_cached(SEP.join(items[i] for i in ch), src, dest)
            parts = [p.strip() for p in re.split(r"\s*#{2,}\s*", res)]
            if len(parts) == len(ch):
                for i, p in zip(ch, parts):
                    out[i] = p or items[i]
            else:  # separator got mangled: translate one by one
                for i in ch:
                    out[i] = _tx_cached(items[i], src, dest)
            done += 1
        except Exception:
            break  # blocked or offline: stop, don't wait on every item

    if todo and done == 0:
        raise RuntimeError(f"Translation failed ({src}->{dest}): {_LAST_ERR[0]}")
    return out


@st.cache_data(show_spinner=False, ttl=3600)
def run_query(q, out_lang="auto"):
    lang = detect_lang(q)
    target = lang if out_lang == "auto" else out_lang

    # Translate user's question to English
    q_en = tx_many([q], lang, "en")[0]

    # Run RAG pipeline
    r = answer(kb, q_en)

    # v2: vague query, several schemes match -> ask the user to choose
    if r["mode"] == "clarify":
        return {"ok": False, "options": r["options"]}

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
        t if len(t) <= 700
        else t[:700].rsplit(" ", 1)[0] + "…"
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
        target
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
        "lang": LANG_NAMES[target],
        "lang_code": target,
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


TTS_LANGS = {"en", "hi", "bn", "pa", "gu", "ta", "te", "kn", "ml", "mr", "ur"}  # gTTS has no Odia


@st.cache_data(show_spinner=False, ttl=86400, max_entries=200)
def speak(text, lang):
    """Return MP3 bytes. Raises on failure so errors are never cached."""
    import io
    from gtts import gTTS

    buf = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(buf)
    return buf.getvalue()


def setq(t):
    st.session_state.q = t


def render_answer(q, out_lang="auto"):
    try:
        with st.spinner(
            "Reading official scheme documents…"
        ):
            d = run_query(q, out_lang)

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

    # v2: vague query -> show the top schemes as buttons
    if not d["ok"] and d.get("options"):
        st.markdown(
            ui.note("<b>Several schemes match. Which one do you mean?</b>"),
            unsafe_allow_html=True
        )
        kq = hashlib.md5(q.encode()).hexdigest()[:8]
        for i, (t, lvl) in enumerate(d["options"]):
            st.button(
                f"{t} ({lvl})",
                key=f"opt{kq}{i}",
                on_click=setq,
                args=(t,),
                use_container_width=True
            )
        return

    if not d["ok"]:
        st.markdown(
            ui.note(
                "<b>No matching scheme found.</b><br>"
                "BharatGPT answers only from official scheme "
                "documents, so it will not guess. "
                "Try the scheme name, for example "
                "PM Kisan or Ayushman Bharat. "
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

    with c3:
        if d["lang_code"] in TTS_LANGS:
            listen = st.button("🔊 Listen", key=f"tts_{k}")
        else:
            listen = False
            st.caption("Audio is not available for this language.")

    if listen:
        body = d["summary"] or " ".join(t for _, t in d["secs"])
        speech = (d["title"] + ". " + body)[:600]
        try:
            with st.spinner("Preparing audio…"):
                st.audio(speak(speech, d["lang_code"]), format="audio/mp3", autoplay=True)
        except Exception as ex:
            st.caption(
                f"Server audio failed ({type(ex).__name__}: {str(ex)[:120]}). "
                "Using your browser's built-in voice instead."
            )
            import json
            import streamlit.components.v1 as components
            components.html(
                f"""
                <button id="b" style="padding:8px 16px;font-size:15px;cursor:pointer">
                  ▶ Play in browser</button>
                <script>
                  document.getElementById('b').onclick = () => {{
                    const u = new SpeechSynthesisUtterance({json.dumps(speech)});
                    u.lang = {json.dumps(MM_CODES.get(d["lang_code"], "en-GB"))};
                    speechSynthesis.cancel();
                    speechSynthesis.speak(u);
                  }};
                </script>
                """,
                height=50,
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

    lang_opts = {"Auto (reply in my language)": "auto"}
    lang_opts.update({n: c for c, n in LANG_NAMES.items()})
    out_choice = st.selectbox(
        "Answer language",
        list(lang_opts),
        key="out_lang"
    )
    out_lang = lang_opts[out_choice]

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
            args=("",)
        )

        render_answer(q, out_lang)

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
