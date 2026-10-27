# BharatGPT: Multilingual assistant for digital governance

BharatGPT answers questions about Indian government schemes in the user's own language, using only official scheme documents and always showing a source link. It also helps draft and track grievances.

**Live demo:** https://bharatgpt-india.streamlit.app/

Micro Project | CSE | 2026-27
Team: [Student name(s)] | Guide: [Faculty name]

## What it does
- Answers questions on 3,399 central and state schemes (benefits, eligibility, documents, how to apply).
- Detects the user's language and replies in it: 11 Indian languages plus English.
- Refuses to guess: low-confidence queries are declined, and every answer shows a confidence level and an official link.
- Asks "which scheme do you mean?" when a query is vague and several schemes match (prompt v2).
- Grievance tab: complaint form, auto-drafted letter, reference ID and status lookup. This is a demo and nothing is sent to any office. For real complaints use CPGRAMS (pgportal.gov.in) or RTI.

## How it works
1. Detect language (Unicode script check)
2. Translate the question to English
3. Classify intent (scheme, eligibility, policy, grievance)
4. Retrieve with TF-IDF over 28,000+ text chunks
5. Check for a vague, near-tied query and ask the user to choose (v2)
6. Generate the answer: Claude via the Anthropic API if `ANTHROPIC_API_KEY` is set, otherwise extracted text from the same source
7. Confidence guardrail, translate back, add the source link

Built with Python, Streamlit, scikit-learn, SQLite, deep-translator and the Anthropic API.

## Prompt design and testing (instructions -> test -> fix -> retest)

**Prompt v1** (system instruction in `rag.py`):
> You are BharatGPT, a citizen help assistant. Answer ONLY from the numbered context. If the context lacks the answer, say so. Be brief, use simple language, plain text only, and do not include citation numbers or markdown.

It is combined with a retrieval guardrail: refuse when the best match score is below 0.30 and no title word matches.

**Test results for v1**

| Query | Result |
|---|---|
| What is the capital of France | Refused (correct) |
| PM Kisan eligibility | Correct scheme, score 0.69 |
| health insurance scheme | One state scheme at 0.67; two others within 0.03 |
| farmer scheme | Obscure scheme at 0.17, not refused |

**Failure found:** on 6 of 6 vague queries (farmer scheme, pension scheme, health insurance scheme, scholarship for students, loan for women, housing scheme) the bot picked a single scheme and answered confidently instead of asking which one.

**Prompt v2 changes**
- Code rule: if the query has 2 or fewer specific words and the top two schemes score within 0.15 of each other, list the top 3 (Central or State) and ask which one. Constants: `CLARIFY_GAP`, `CLARIFY_MAX_WORDS` in `rag.py`.
- Prompt line added: "If the context covers more than one scheme, name the scheme you are answering about and never mix details."

**Retest results for v2**

| Check | v1 | v2 |
|---|---|---|
| Vague queries that ask for clarification | 0 / 6 | 6 / 6 |
| Specific questions still answered directly (21 questions) | 21 / 21 | 19 / 21 |
| Retrieval top-1 / top-3 | 57.1% / 71.4% | 57.1% / 71.4% |

Trade-off: "Ujjwala Yojana eligibility" and "What is the fee to file RTI?" now get a follow-up question instead of a direct answer.

Not yet done: the v2 prompt line has not been tested in LLM mode (needs `ANTHROPIC_API_KEY`). The thresholds were tuned on a small set of 6 vague and 21 specific queries, so they may not generalise.

## Retrieval evaluation
`python bharatgpt/evaluate.py` runs 21 self-written labelled questions: top-1 57.1%, top-3 71.4%, MRR 0.643. Accuracy is limited because 2,859 state schemes compete with national ones. The questions were written by the team, so treat the numbers as a rough indicator.

## Known limitations
- TF-IDF retrieval is English-only, so other languages depend on translation.
- The dataset is a scraped copy of MyScheme.gov.in; amounts and rules may be outdated. Always confirm on the official link. This is not legal advice.
- Grievances are not sent to any office, and hosted storage is temporary.
- No voice input yet.
- Vague queries longer than 2 specific words can still pick the wrong scheme.
- The citizen survey (`survey/google_form_questions.md`) is designed but responses have not been collected.

## Future scope
Multilingual embedding retrieval, voice input (Whisper / Bhashini), live CPGRAMS integration, a larger test set, and an LLM-mode check of prompt v2.

## Run locally
```
pip install -r bharatgpt/requirements.txt
streamlit run bharatgpt/app.py
```
Optional LLM answers: set `ANTHROPIC_API_KEY` in your environment (locally) or in Streamlit Settings > Secrets (hosted). Never commit keys.

## Dataset
`data/myscheme_kaggle.csv`: Kaggle "Indian Government Schemes" (jainamgada45), 3,400 rows scraped from myscheme.gov.in (columns: scheme_name, slug, details, benefits, eligibility, application, documents, level, schemeCategory, tags). `data/governance_extra.csv` adds CPGRAMS and RTI entries. Check the Kaggle licence before reuse. `data_sample/schemes_sample.csv` is a small demo set compiled from general knowledge; verify it against the source URLs.

## Publish
Push to GitHub, then deploy at share.streamlit.io with main file `bharatgpt/app.py`.
