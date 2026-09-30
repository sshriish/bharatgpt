"""All styling and HTML for the BharatGPT interface."""
import html
e = html.escape

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Noto+Sans:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Tamil:wght@400;600&family=Noto+Sans+Telugu:wght@400;600&family=Noto+Sans+Kannada:wght@400;600&family=Noto+Sans+Bengali:wght@400;600&display=swap');
:root{--ink:#0F1B3D;--muted:#5A6480;--line:#E3E7F0;--accent:#D9480F;--soft:#F7F8FB;}
.stApp,[data-testid="stHeader"]{background:#fff!important;}
[data-testid="stSidebar"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"]{display:none!important;}
footer,#MainMenu{visibility:hidden;}
.stApp,.stApp p,.stApp li,.stApp label,.stApp span,.stApp div{font-family:'Noto Sans','Noto Sans Devanagari','Noto Sans Tamil','Noto Sans Telugu','Noto Sans Kannada','Noto Sans Bengali',sans-serif;}
.stApp p,.stApp li,.stApp label{color:var(--ink);}
.block-container{max-width:720px;padding-top:2.2rem;padding-bottom:3rem;}
.brand{font-family:'Manrope',sans-serif;font-weight:800;font-size:1.05rem;color:var(--ink);display:flex;align-items:center;gap:.5rem;}
.brand .dot{width:.7rem;height:.7rem;border-radius:50%;background:var(--accent);display:inline-block;}
.h{font-family:'Manrope',sans-serif;font-weight:800;font-size:3rem;line-height:1.08;letter-spacing:-.02em;color:var(--ink);margin:2.2rem 0 1rem 0;}
.sub{font-size:1.1rem;line-height:1.6;color:var(--muted);max-width:32rem;margin:0 0 1.4rem 0;}
.langs{font-size:.95rem;color:var(--muted);margin:.7rem 0 0 0;}
.langs span{margin-right:1.1rem;}
.stTabs [data-baseweb="tab-list"]{gap:1.6rem;border-bottom:1px solid var(--line);}
.stTabs [data-baseweb="tab"]{font-family:'Manrope',sans-serif;font-weight:700;color:var(--muted);padding-left:0;padding-right:0;}
.stTabs [aria-selected="true"]{color:var(--ink)!important;}
.stTabs [data-baseweb="tab-highlight"]{background:var(--accent)!important;}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"]{background:#fff!important;border-radius:12px!important;}
[data-baseweb="input"],[data-baseweb="textarea"]{border:1.5px solid var(--line)!important;}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within{border-color:var(--accent)!important;}
.stTextInput input,.stTextArea textarea{background:#fff!important;color:var(--ink)!important;font-size:1.1rem;padding:.9rem 1rem;}
.stButton>button{background:#fff;color:var(--ink);border:1px solid var(--line);border-radius:999px;font-weight:600;font-size:.92rem;padding:.35rem 1rem;}
.stButton>button:hover{border-color:var(--accent);color:var(--accent);background:#fff;}
.stFormSubmitButton>button{background:var(--ink);color:#fff;border:0;border-radius:10px;font-weight:700;padding:.55rem 1.4rem;}
.stFormSubmitButton>button:hover{background:var(--accent);color:#fff;}
.tryhead{font-size:.9rem;color:var(--muted);margin:1.3rem 0 .4rem 0;}
.card{border:1px solid var(--line);border-radius:14px;margin:1.4rem 0 .8rem 0;overflow:hidden;background:#fff;}
.card-top{padding:1.4rem 1.6rem 1.1rem 1.6rem;border-bottom:1px solid var(--line);background:var(--soft);}
.card-title{font-family:'Manrope',sans-serif;font-weight:800;font-size:1.5rem;line-height:1.25;color:var(--ink);margin:0;}
.card-sub{font-size:.85rem;color:var(--muted);margin-top:.4rem;}
.card-sub span{margin-right:1rem;}
.sec{padding:1.1rem 1.6rem 0 1.6rem;}
.sec-l{font-family:'Manrope',sans-serif;font-weight:700;font-size:.95rem;color:var(--accent);margin-bottom:.25rem;}
.sec-t{font-size:.98rem;line-height:1.65;color:var(--ink);white-space:pre-line;}
.card-foot{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between;padding:1.2rem 1.6rem 1.4rem 1.6rem;}
.match{white-space:nowrap;font-size:.88rem;color:var(--muted);display:flex;align-items:center;gap:.5rem;}
.match i{width:.6rem;height:.6rem;border-radius:50%;display:inline-block;}
a.src{background:var(--ink);color:#fff!important;text-decoration:none;font-weight:700;font-size:.92rem;padding:.6rem 1.2rem;border-radius:10px;}
a.src:hover{background:var(--accent);}
.also{font-size:.9rem;color:var(--muted);}
.note{border:1px solid var(--line);border-radius:12px;padding:1.1rem 1.3rem;margin-top:1.2rem;color:var(--ink);background:var(--soft);line-height:1.6;}
.ref{border:1px solid var(--line);border-radius:12px;padding:1.1rem 1.3rem;margin:1rem 0;color:var(--ink);}
.ref .id{font-family:'Manrope',sans-serif;font-weight:800;font-size:1.7rem;color:var(--accent);}
.fine{font-size:.82rem;color:var(--muted);margin-top:2.5rem;line-height:1.6;}
@media(max-width:640px){.h{font-size:2.15rem}}
</style>
"""

HERO = """
<div class="brand"><span class="dot"></span>BharatGPT</div>
<h1 class="h">Schemes made for you should reach you.</h1>
<p class="sub">Ask in your own language. Get a clear answer and the official source, from over 3,400 Central and State schemes.</p>
"""
LANGS = ('<div class="langs"><span>English</span><span>हिन्दी</span><span>தமிழ்</span><span>తెలుగు</span>'
         '<span>ಕನ್ನಡ</span><span>বাংলা</span><span>and more</span></div>')

COLORS = {3: "#1A7F4B", 2: "#B7791F", 1: "#C53030"}

def card(title, lang, intent, sections, strength, word, link):
    body = "".join(f'<div class="sec"><div class="sec-l">{e(l)}</div><div class="sec-t">{e(t)}</div></div>' for l, t in sections)
    btn = f'<a class="src" href="{e(link)}" target="_blank" rel="noopener">View official page</a>' if link else ""
    return (f'<div class="card"><div class="card-top"><h2 class="card-title">{e(title)}</h2>'
            f'<div class="card-sub"><span>{e(lang)}</span><span>{e(intent)}</span></div></div>{body}'
            f'<div class="card-foot"><div class="match"><i style="background:{COLORS[strength]}"></i>{e(word)}</div>{btn}</div></div>')

def note(msg):
    return f'<div class="note">{msg}</div>'

def refbox(inner):
    return f'<div class="ref">{inner}</div>'
