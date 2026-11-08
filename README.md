# SG Car Copilot

A small RAG (Retrieval-Augmented Generation) app that answers questions about buying and owning a car in Singapore, using official explainer pages, COE bidding data and a hand-made list of car models. It cites its sources and says "I don't know" when it can't find an answer.

> Full beginner walkthrough: see the step-by-step guide that came with this folder.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then put your free API key inside
# fill in data/docs/*.md, data/cars.csv (and optionally data/raw/coe.csv)
python -m src.coe_to_text          # only if you downloaded the COE csv
python -m src.ingest               # builds the search index
python -m src.retrieve             # test search by itself
streamlit run app.py               # launch the app
python -m eval.run_eval            # report card
```

## How it works

1. **Ingest** - text is cut into small chunks, turned into numbers (embeddings) and stored in a local ChromaDB index.
2. **Retrieve** - your question is turned into numbers too, and the closest chunks are fetched.
3. **Generate** - a free LLM (Groq or Gemini) answers using only those chunks, with citations. If nothing is close enough, the app refuses instead of guessing.

## Evaluation

(Fill in after Step 7 of the guide: a table of settings vs. score.)

## Data

Data as of: (date). Always verify rules on official LTA / OneMotoring pages.
