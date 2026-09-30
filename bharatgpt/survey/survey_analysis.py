"""Turns the Google Form CSV into charts + analysis text. Run: python survey/survey_analysis.py survey/survey_responses.csv"""
import sys, pandas as pd, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
f = sys.argv[1] if len(sys.argv) > 1 else "survey/survey_responses.csv"
df = pd.read_csv(f)
c = {i: df.columns[i] for i in range(1, 11)}      # column 0 = timestamp
n = len(df); pct = lambda s: 100 * s / n
def share(col, val): return pct(df[col].astype(str).str.contains(val, case=False).sum())
diff = share(c[5], "Yes|Sometimes"); reg = 100 - share(c[4], "English")
use = pct((pd.to_numeric(df[c[8]], errors="coerce") >= 4).sum())
voice = share(c[9], "Voice|Both"); mid = share(c[6], "Agent|Relative")
late = share(c[7], "delayed")
for i, title in [(4, "Preferred language"), (5, "Difficulty finding information"), (6, "Current sources"), (9, "Preferred input"), (10, "Biggest concern")]:
    ax = df[c[i]].value_counts().plot(kind="barh", color="#138808", figsize=(6, 3.2), title=title)
    ax.invert_yaxis(); plt.tight_layout(); plt.savefig(f"survey/chart_q{i}.png", dpi=200); plt.close()
txt = (f"Of N = {n} respondents, {diff:.0f}% reported difficulty finding scheme or service information, "
       f"{reg:.0f}% preferred a language other than English, {mid:.0f}% relied on agents or relatives, "
       f"{late:.0f}% had a delayed or unresolved grievance, {voice:.0f}% wanted voice input, and "
       f"{use:.0f}% rated their likelihood of using a native-language chatbot 4 or 5 out of 5.")
open("survey/analysis.txt", "w").write(txt); print(txt)
