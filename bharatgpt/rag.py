"""BharatGPT core: knowledge base, retrieval (RAG), intent, guardrails, grievances."""
import glob, os, sqlite3, uuid, datetime
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SCRIPTS = {"hi": (0x0900, 0x097F), "bn": (0x0980, 0x09FF), "pa": (0x0A00, 0x0A7F),
           "gu": (0x0A80, 0x0AFF), "or": (0x0B00, 0x0B7F), "ta": (0x0B80, 0x0BFF),
           "te": (0x0C00, 0x0C7F), "kn": (0x0C80, 0x0CFF), "ml": (0x0D00, 0x0D7F)}
LANG_NAMES = {"en": "English", "hi": "Hindi", "bn": "Bengali", "pa": "Punjabi", "gu": "Gujarati",
              "or": "Odia", "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam"}
TITLE_COLS = ["scheme_name", "name", "title", "scheme"]
SOURCE_COLS = ["source_url", "source", "url", "link"]

def detect_lang(text):
    counts = {l: sum(lo <= ord(c) <= hi for c in text) for l, (lo, hi) in SCRIPTS.items()}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "en"

def translate(text, src, dest):
    """Uses deep-translator (Google) if installed and online; otherwise returns text unchanged."""
    if src == dest or not text.strip():
        return text
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source=src, target=dest).translate(text)
    except Exception:
        return text

ALIASES = {"pm": "pradhan mantri", "pmjay": "ayushman bharat pradhan mantri jan arogya", "cm": "chief minister",
           "mgnrega": "mahatma gandhi national rural employment guarantee", "nrega": "mahatma gandhi national rural employment guarantee",
           "rti": "right to information", "lpg": "lpg gas", "pmay": "pradhan mantri awas yojana", "pmfby": "pradhan mantri fasal bima"}

def expand_query(q):
    return " ".join(ALIASES.get(w.lower().strip("?.,!"), w) for w in q.split())

def classify_intent(q):
    q = q.lower()
    if any(w in q for w in ["complaint", "grievance", "not received", "bribe", "corrupt", "harass", "delay", "cheated"]):
        return "grievance"
    if any(w in q for w in ["eligible", "eligibility", "qualify", "who can"]):
        return "eligibility"
    if any(w in q for w in ["rti", "policy", "act ", "law", "rule"]):
        return "policy"
    return "scheme/service"

FIELD_ORDER = ["details", "description", "benefits", "eligibility", "documents", "documents_required", "application", "how_to_apply"]
SKIP_COLS = {"slug", "level", "schemecategory", "tags"}
MYSCHEME = "https://www.myscheme.gov.in/schemes/"

class KnowledgeBase:
    """One chunk per (scheme, field), long fields split into <=chunk_words pieces."""
    def __init__(self, data_dir="data", chunk_words=120):
        self.chunks = []
        for f in sorted(glob.glob(os.path.join(data_dir, "*.csv"))):
            try:
                df = pd.read_csv(f, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(f, encoding="latin-1")
            df = df.loc[:, ~df.columns.str.startswith("Unnamed")].fillna("")
            cols = {c.lower().strip(): c for c in df.columns}
            tcol = next((cols[c] for c in TITLE_COLS if c in cols), df.columns[0])
            scol = next((cols[c] for c in SOURCE_COLS if c in cols), None)
            slug = cols.get("slug")
            for _, r in df.iterrows():
                title = str(r[tcol])
                src = str(r[scol]) if scol else (MYSCHEME + str(r[slug]) if slug else os.path.basename(f))
                meta = " ".join(str(r[cols[k]]) for k in ("schemecategory", "tags", "level") if k in cols)
                lvl = str(r[cols["level"]]) if "level" in cols else "Central"
                self.chunks.append({"title": title, "source": src, "field": "category", "text": meta, "level": lvl})
                for c in df.columns:
                    if c in (tcol, scol) or c.lower() in SKIP_COLS or not str(r[c]).strip():
                        continue
                    w = " ".join(str(r[c]).split()).split(" ")
                    for i in range(0, len(w), chunk_words):
                        self.chunks.append({"title": title, "source": src, "field": c.lower(), "level": lvl, "text": " ".join(w[i:i + chunk_words])})
        if not self.chunks:
            raise RuntimeError(f"No CSV data found in '{data_dir}/'")
        self.vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True, min_df=2)
        self.matrix = self.vec.fit_transform([f"{c['title']} {c['title']} {c['text']}" for c in self.chunks])

    def search(self, query, k=3, central_boost=0.06):
        """Cosine similarity + small boost for national (Central) schemes and for title-word overlap."""
        q = query.lower()
        sims = cosine_similarity(self.vec.transform([query]), self.matrix)[0].copy()
        qw = set(w for w in q.replace("-", " ").split() if len(w) > 3)
        if not hasattr(self, "_boost"):
            self._boost = np.array([central_boost if c["level"] == "Central" else 0.0 for c in self.chunks])
            self._tw = [set(c["title"].lower().replace("-", " ").split()) for c in self.chunks]
        overlap = np.array([len(qw & t) for t in self._tw])
        sims = sims + self._boost * (sims > 0.05) + 0.04 * np.minimum(overlap, 3)
        idx = sims.argsort()[::-1][:k]
        return [(float(sims[i]), self.chunks[i]) for i in idx]

    def top_schemes(self, query, k=3, pool=40):
        """Best chunk score per scheme -> ranked list of (score, title)."""
        best = {}
        for s, c in self.search(query, k=pool):
            best.setdefault(c["title"], s)
        return sorted(((s, t) for t, s in best.items()), reverse=True)[:k]

def _llm_answer(question, hits):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
        ctx = "\n\n".join(f"[{i+1}] {c['title']}: {c['text']}" for i, (_, c) in enumerate(hits))
        msg = anthropic.Anthropic(api_key=key).messages.create(
            model=os.getenv("BHARATGPT_MODEL", "claude-sonnet-5-5"), max_tokens=600,
            system="You are BharatGPT, a citizen help assistant. Answer ONLY from the numbered context. "
                   "If the context lacks the answer, say so. Be brief, use simple language, cite like [1].",
            messages=[{"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {question}"}])
        return msg.content[0].text
    except Exception:
        return None

def answer(kb, question, threshold=0.30):
    """Returns dict(answer, sources, confidence, intent, mode)."""
    intent = classify_intent(question)
    question = expand_query(question)
    hits = kb.search(question, k=12)
    top = hits[0][0]
    GENERIC = {"scheme", "yojana", "eligibility", "benefits", "benefit", "apply", "documents", "government", "what", "which", "where", "when", "does", "about", "tell", "help", "need", "with", "from", "have", "that", "this", "your", "world"}
    qw = set(w for w in question.lower().replace('-', ' ').split() if len(w) > 3 and w not in GENERIC)
    tw = set(w for _, c in hits[:5] for w in c['title'].lower().replace('-', ' ').split())
    if top < threshold and not (qw & tw):
        return {"answer": "I could not find this in my official-document knowledge base, so I will not guess. "
                          "For complaints you can use the Grievance tab or CPGRAMS (pgportal.gov.in).",
                "sources": [], "confidence": top, "intent": intent, "mode": "guardrail", "title": None, "sections": []}
    best_title = hits[0][1]["title"]
    good = [h for h in hits if h[1]["title"] == best_title]
    good.sort(key=lambda h: FIELD_ORDER.index(h[1]["field"]) if h[1]["field"] in FIELD_ORDER else 99)
    text = _llm_answer(question, good)
    mode = "llm-rag"
    if text is None:
        mode = "extractive-rag"
        text = f"**{best_title}**\n\n" + "\n\n".join(
            f"**{c['field'].replace('_', ' ').title()}:** {c['text'][:700]}" for _, c in good if c["field"] != "category")
    srcs = list(dict.fromkeys(c["source"] for _, c in good))
    return {"answer": text, "sources": srcs, "confidence": top, "intent": intent, "mode": mode,
            "title": best_title, "sections": [(c["field"], c["text"]) for _, c in good if c["field"] != "category"]}

# ---------- grievance module (SQLite) ----------
def _db(path="grievances.db"):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE IF NOT EXISTS g(ref TEXT PRIMARY KEY, name TEXT, dept TEXT, text TEXT, lang TEXT, status TEXT, created TEXT)")
    return con

def register_grievance(name, dept, text, lang="en", path="grievances.db"):
    ref = "BGPT-" + uuid.uuid4().hex[:8].upper()
    con = _db(path)
    con.execute("INSERT INTO g VALUES(?,?,?,?,?,?,?)", (ref, name, dept, text, lang, "Registered", datetime.datetime.now().isoformat(timespec="seconds")))
    con.commit(); con.close()
    return ref

def grievance_status(ref, path="grievances.db"):
    con = _db(path)
    row = con.execute("SELECT ref,dept,status,created FROM g WHERE ref=?", (ref.strip(),)).fetchone()
    con.close()
    return row

def draft_complaint(name, dept, text):
    return (f"To,\nThe Grievance Officer, {dept}\n\nSubject: Grievance regarding {dept}\n\nRespected Sir/Madam,\n\n"
            f"I, {name}, wish to bring the following issue to your attention:\n\n{text}\n\n"
            "I request you to look into the matter and take appropriate action at the earliest.\n\nYours faithfully,\n" + name)
