"""All styling and HTML for the BharatGPT interface."""
import html
e = html.escape

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700;800&family=Noto+Sans:wght@400;500;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Tamil:wght@400;600&family=Noto+Sans+Telugu:wght@400;600&family=Noto+Sans+Kannada:wght@400;600&family=Noto+Sans+Bengali:wght@400;600&display=swap');
:root{--ink:#14213D;--muted:#5B6785;--line:#E1E6F0;--bg:#F4F6FB;--navy:#0E1B4D;--blue:#1F3A93;--saffron:#F28C28;--green:#138808;}
.stApp{background:var(--bg)!important;}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"]{display:none!important;}
[data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"]{display:none!important;}
footer,#MainMenu{visibility:hidden;}
.stApp,.stApp p,.stApp li,.stApp label,.stApp span,.stApp div{font-family:'Noto Sans','Noto Sans Devanagari','Noto Sans Tamil','Noto Sans Telugu','Noto Sans Kannada','Noto Sans Bengali',sans-serif;}
.stApp p,.stApp li,.stApp label{color:var(--ink);}
.block-container{max-width:820px;padding-top:1.2rem;padding-bottom:3rem;}

/* top bar */
.topbar{display:flex;justify-content:space-between;align-items:center;padding:.4rem 0 1rem 0;}
.brand{font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:1.15rem;color:var(--ink);display:flex;align-items:center;gap:.6rem;}
.logo{width:26px;height:26px;}
.pill{font-size:.78rem;font-weight:600;color:var(--blue);background:#E8EDFB;border-radius:999px;padding:.25rem .75rem;}

/* hero */
.hero{background:var(--navy);border-radius:20px;overflow:hidden;box-shadow:0 12px 32px rgba(14,27,77,.18);}
.flag{height:5px;background:linear-gradient(90deg,#F28C28 0 33.3%,#fff 33.3% 66.6%,#138808 66.6% 100%);}
.hero-in{padding:2.2rem 2.2rem 1.6rem 2.2rem;}
.h{font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:2.6rem;line-height:1.12;letter-spacing:-.02em;color:#fff;margin:0 0 .9rem 0;max-width:34rem;}
.sub{font-size:1.05rem;line-height:1.6;color:#C6CFEE;max-width:34rem;margin:0 0 1.2rem 0;}
.langs{display:flex;flex-wrap:wrap;gap:.45rem;}
.langs span{font-size:.85rem;color:#fff;background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.18);border-radius:999px;padding:.2rem .75rem;}
.stats{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid rgba(255,255,255,.12);}
.stats div{padding:1rem 2.2rem;color:#AEB9E3;font-size:.82rem;}
.stats div+div{border-left:1px solid rgba(255,255,255,.12);}
.stats b{display:block;font-family:'Plus Jakarta Sans',sans-serif;font-size:1.3rem;color:#fff;}

/* tabs */
.stTabs [data-baseweb="tab-list"]{gap:.4rem;background:#E9EDF6;border-radius:12px;padding:.3rem;margin-top:1.4rem;border:0;}
.stTabs [data-baseweb="tab"]{font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;color:var(--muted);border-radius:9px;padding:.5rem 1.2rem;height:auto;}
.stTabs [aria-selected="true"]{background:#fff!important;color:var(--ink)!important;box-shadow:0 1px 4px rgba(20,33,61,.12);}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none!important;}

/* inputs */
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"]{background:#fff!important;border-radius:14px!important;}
[data-baseweb="input"],[data-baseweb="textarea"]{border:1.5px solid var(--line)!important;box-shadow:0 4px 18px rgba(20,33,61,.06);transition:border-color .15s,box-shadow .15s;}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within{border-color:var(--blue)!important;box-shadow:0 0 0 4px rgba(31,58,147,.13);}
.stTextInput input,.stTextArea textarea{background:#fff!important;color:var(--ink)!important;font-size:1.05rem;padding:.95rem 1rem;}
.stTextInput input[aria-label="Your question"]{padding-left:3rem!important;background:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="%235B6785" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="9" r="6.5"/><path d="M14 14l4.5 4.5"/></svg>') no-repeat 1rem center!important;}

/* buttons: chips and tiles */
.stButton>button{background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:12px;font-weight:600;font-size:.92rem;padding:.55rem 1rem;justify-content:flex-start;text-align:left;box-shadow:0 1px 2px rgba(20,33,61,.04);transition:transform .15s,border-color .15s,box-shadow .15s;}
.stButton>button:hover{border-color:var(--blue);color:var(--blue);background:#fff;transform:translateY(-1px);box-shadow:0 6px 16px rgba(31,58,147,.12);}
.stButton>button:focus-visible,.stFormSubmitButton>button:focus-visible{outline:3px solid rgba(31,58,147,.35);outline-offset:2px;}
.stFormSubmitButton>button,.stDownloadButton>button{background:var(--navy);color:#fff;border:0;border-radius:12px;font-weight:700;padding:.6rem 1.5rem;}
.stFormSubmitButton>button:hover,.stDownloadButton>button:hover{background:var(--blue);color:#fff;}
.stDownloadButton>button{background:#fff;color:var(--ink);border:1px solid var(--line);}
.stDownloadButton>button:hover{background:#fff;color:var(--blue);border:1px solid var(--blue);}
.tryhead{font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:.95rem;color:var(--ink);margin:1.6rem 0 .6rem 0;}

/* answer card */
.card{border:1px solid var(--line);border-radius:16px;margin:1.4rem 0 .8rem 0;overflow:hidden;background:#fff;box-shadow:0 8px 28px rgba(20,33,61,.07);animation:rise .35s ease-out;}
@keyframes rise{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:none;}}
.card-top{padding:1.5rem 1.7rem 1.2rem 1.7rem;border-left:5px solid var(--saffron);}
.card-title{font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:1.5rem;line-height:1.25;color:var(--ink);margin:0 0 .7rem 0;}
.badges{display:flex;flex-wrap:wrap;gap:.4rem;}
.badge{font-size:.78rem;font-weight:600;color:var(--blue);background:#E8EDFB;border-radius:999px;padding:.2rem .7rem;}
details.sec{border-top:1px solid var(--line);}
details.sec summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;padding:1rem 1.7rem;font-family:'Plus Jakarta Sans',sans-serif;font-weight:700;font-size:.98rem;color:var(--ink);transition:background .15s;}
details.sec summary::-webkit-details-marker{display:none;}
details.sec summary:hover{background:var(--bg);}
details.sec summary::after{content:"";width:.5rem;height:.5rem;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg);transition:transform .2s;margin-right:.2rem;}
details.sec[open] summary::after{transform:rotate(-135deg);}
.sec-t{padding:0 1.7rem 1.2rem 1.7rem;font-size:.97rem;line-height:1.7;color:var(--ink);white-space:pre-line;}
.card-foot{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between;padding:1.1rem 1.7rem;border-top:1px solid var(--line);background:var(--bg);}
.match{display:flex;align-items:center;gap:.6rem;font-size:.86rem;color:var(--muted);}
.meter{display:flex;gap:3px;}
.meter b{width:1.4rem;height:.4rem;border-radius:3px;background:#D5DBE9;}
.meter b.on.c3{background:var(--green);}.meter b.on.c2{background:#D69E2E;}.meter b.on.c1{background:#C53030;}
a.src{background:var(--navy);color:#fff!important;text-decoration:none;font-weight:700;font-size:.9rem;padding:.6rem 1.2rem;border-radius:10px;transition:background .15s;}
a.src:hover{background:var(--blue);}
.also{font-size:.9rem;color:var(--muted);}

/* notes, reference, tracker */
.note{border:1px solid var(--line);border-left:5px solid var(--saffron);border-radius:12px;padding:1.1rem 1.3rem;margin-top:1.2rem;color:var(--ink);background:#fff;line-height:1.6;}
.ref{border:1px solid #BFE3C6;background:#F1FAF3;border-radius:14px;padding:1.2rem 1.4rem;margin:1rem 0;color:var(--ink);}
.ref .id{font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:1.8rem;color:var(--green);letter-spacing:.02em;}
.track{display:flex;margin:.9rem 0 .2rem 0;}
.track div{flex:1;text-align:center;font-size:.82rem;color:var(--muted);position:relative;}
.track div::before{content:"";display:block;width:1.1rem;height:1.1rem;border-radius:50%;background:#D5DBE9;margin:0 auto .4rem auto;position:relative;z-index:1;}
.track div::after{content:"";position:absolute;top:.5rem;left:-50%;width:100%;height:2px;background:#D5DBE9;}
.track div:first-child::after{display:none;}
.track div.done::before{background:var(--green);}.track div.done::after{background:var(--green);}
.track div.done{color:var(--ink);font-weight:600;}
.fine{font-size:.8rem;color:var(--muted);margin-top:2.5rem;line-height:1.6;text-align:center;}
@media(max-width:640px){.h{font-size:1.9rem}.hero-in{padding:1.6rem 1.3rem 1.2rem 1.3rem}.stats div{padding:.8rem 1rem}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;}}
</style>
"""

TOPBAR = ('<div class="topbar"><div class="brand"><svg class="logo" viewBox="0 0 24 24"><rect y="3" width="24" height="5" rx="2.5" fill="#F28C28"/>'
          '<rect y="9.5" width="24" height="5" rx="2.5" fill="#1F3A93"/><rect y="16" width="24" height="5" rx="2.5" fill="#138808"/></svg>BharatGPT</div>'
          '<span class="pill">Student project</span></div>')

HERO = ('<div class="hero"><div class="flag"></div><div class="hero-in">'
        '<h1 class="h">Government schemes, explained in your language.</h1>'
        '<p class="sub">Ask a question and get a clear answer with the official source, drawn from Central and State scheme documents.</p>'
        '<div class="langs"><span>English</span><span>हिन्दी</span><span>தமிழ்</span><span>తెలుగు</span><span>ಕನ್ನಡ</span><span>বাংলা</span><span>and more</span></div></div>'
        '<div class="stats"><div><b>3,400+</b>schemes indexed</div><div><b>10</b>languages detected</div><div><b>Official</b>source on every answer</div></div></div>')

COLORS = {3: "#1A7F4B", 2: "#B7791F", 1: "#C53030"}
INTENTS = {"scheme/service": "Scheme information", "eligibility": "Eligibility", "policy": "Policy and rights", "grievance": "Grievance"}

def head(t):
    return f'<div class="tryhead">{e(t)}</div>'

def card(title, lang, intent, sections, strength, word, host, link):
    body = ""
    for i, (l, t) in enumerate(sections):
        op = " open" if i < 2 else ""
        body += f'<details class="sec"{op}><summary>{e(l)}</summary><div class="sec-t">{e(t)}</div></details>'
    bars = "".join('<b class="on c%d"></b>' % strength if i < strength else "<b></b>" for i in range(3))
    btn = f'<a class="src" href="{e(link)}" target="_blank" rel="noopener">Open on {e(host)}</a>' if link else ""
    return (f'<div class="card"><div class="card-top"><h2 class="card-title">{e(title)}</h2>'
            f'<div class="badges"><span class="badge">{e(lang)}</span><span class="badge">{e(INTENTS.get(intent, intent))}</span></div></div>{body}'
            f'<div class="card-foot"><div class="match"><div class="meter">{bars}</div>{e(word)}</div>{btn}</div></div>')

def note(msg):
    return f'<div class="note">{msg}</div>'

def refbox(inner):
    return f'<div class="ref">{inner}</div>'

def tracker(idx, steps=("Registered", "In review", "Resolved")):
    return '<div class="track">' + "".join(f'<div class="{"done" if i <= idx else ""}">{e(s)}</div>' for i, s in enumerate(steps)) + '</div>'
