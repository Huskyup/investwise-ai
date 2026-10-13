# InvestWise AI

A Challenge 2 conversational risk-profile prototype. All 15 questions use question-specific TF-IDF, Logistic Regression and conformal prediction for free-text interpretation. Safety controls, business validation, confirmation and save consent remain explicit application gates.

Use fictional situations in the demo. This checkpoint is a working prototype with substantial free-text abstention; it does not establish real-customer accuracy or provide investment advice.

## Separate D5 company demonstration

The [D5 core browser demo](demos/d5/core/README.md) shows the existing ML + GPT conversation, business interpretation, follow-up, correction and explicit confirmation. Launch a reproducible, clearly labelled recorded walkthrough with `sh demos/d5/run_core_demo.sh replay`; use `live` explicitly for new fictional text and the existing ChatGPT connection. This does not change the main application below. The latest live browser attempt stopped on a provider overload; replay is not evidence of live interpretation. See the [delivery report](docs/d5-core-demo-2026-10-13/REPORT.md).

## Run locally

Python 3.12 is recommended for reproducing the tested environment (3.12.14).

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-snapshot.txt
python -m pip install -e . --no-deps
python -m pytest -q
python -m streamlit run frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

On Windows, create the environment with `py -3.12 -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1`. The pinned file records the tested dependency versions; verify platform availability rather than silently claiming equivalent results after changing versions. `requirements.txt` is the broader unpinned dependency list.

## Read next

- [Current implementation and safeguards](README_IMPLEMENTATION.md)
- [Preserved evaluation results and limitations](work/all-question-ml-2026-10-04/EVALUATION_README.md)
- [Continuation prompt for another computer](docs/CONTINUE_ML_IMPROVEMENT_PROMPT.md)
- [Fictional dataset and provenance](data/nlp/all_questions/README.md)

The 204-case evaluation has already been opened and reused for repairs. Treat it as a known regression set; do not present another run as fresh held-out validation. Existing D12-only/hybrid components remain explicitly archived comparisons, not the Streamlit default.
