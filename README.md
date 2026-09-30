# BharatGPT - Multilingual RAG assistant for digital governance
Run: `pip install -r requirements.txt` then `streamlit run app.py`

## Pipeline
User text -> language detection (Unicode script) -> translate to English -> intent classification -> TF-IDF retrieval over `data/*.csv`
-> grounded answer (Claude via `ANTHROPIC_API_KEY` if set, else extractive answer) -> confidence guardrail -> translate back -> answer + source link.
Grievance tab: form -> draft complaint letter -> SQLite reference ID -> status lookup.

## Dataset (already installed)
`data/myscheme_kaggle.csv` = Kaggle 'Indian Government Schemes' (jainamgada45), 3,400 schemes scraped from myscheme.gov.in (columns: scheme_name, slug, details, benefits, eligibility, application, documents, level, schemeCategory, tags). Source links are built from the slug. `data/governance_extra.csv` adds CPGRAMS and RTI. Cite the dataset and MyScheme.gov.in; check the Kaggle license.

## Using a different dataset
1. Search Kaggle for "Indian government schemes" and download a CSV (login needed; I could not download it for you).
2. Put the CSV in `data/`. The loader auto-detects a title column (scheme_name/name/title), an optional source column (url/link), and indexes all other text columns.
3. Run `python evaluate.py` after editing the TESTS list to match your dataset. Cite the dataset in your paper.

## Data note
`data/schemes_sample.csv` was compiled from general knowledge of public schemes for demo purposes. Verify amounts and rules on each source_url before presenting them as facts.

## Survey
Use `survey/google_form_questions.md`, export responses, then `python survey/survey_analysis.py survey/survey_responses.csv`.

## Known limitations (state these in your review)
TF-IDF retrieval is English-only, so other languages depend on translation. No voice input yet (extension: Whisper/Bhashini). TF-IDF gets ~57% top-1 / ~71% top-3 on 21 self-written questions because 2,859 state schemes compete with national ones; embedding retrieval is the planned fix.

## Publish
1. `git init && git add . && git commit -m "BharatGPT" ` then push to a new GitHub repo.
2. Go to share.streamlit.io, sign in with GitHub, pick the repo, main file `app.py`, Deploy. You get a public link.
3. Optional LLM answers: in the app's Settings > Secrets add `ANTHROPIC_API_KEY = "..."`. Never commit keys. Leave it off if you do not want public traffic using your credit.
Note: hosted disk is temporary, so registered grievances may disappear on restart (fine for a demo).
