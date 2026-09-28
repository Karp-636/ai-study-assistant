# RAG Document Q&A

Tonight's homework is to **finish and exercise the build from today's [RAG Pattern lesson](https://github.com/CP-Evenings-and-Weekends/curriculum/blob/main/Module_06_AI_LLMs/week17/day2/README.md)**: the start of the AI Study Assistant. This is the same codebase you will extend with conversations on Thursday and harden on Saturday, so getting it solid tonight pays off all week.

There is no new app to build here. If you finished the lesson in class, tonight is about proving it works and understanding *why* it works.

## Setup

This repo is the **starter you clone at the beginning of Tuesday's class**, and the codebase you keep working in tonight, Thursday, and Saturday. The Django scaffold is already wired up: `config/` project, an empty `assistant` app, PostgreSQL settings pointing at the Docker container, `.env` loading, and a first migration that enables the pgvector extension. Your job is the AI parts, not the plumbing.

```bash
cp .env.example .env
# Defaults work as-is on the class Ollama stack; make sure Ollama is running
# and Monday's models are pulled (ollama list should show nomic-embed-text and llama3.2)
docker compose up -d
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate     # smoke test: should apply cleanly, no edits needed
python manage.py runserver   # smoke test: http://localhost:8000/admin/ should load
```

If both smoke tests pass, your environment works. Then follow the lesson to build the models, `chunking.py`, `embeddings.py`, `rag.py`, the serializers, and the views. (When you run `makemigrations` after writing the models, the new migration automatically runs after the shipped `0001_enable_pgvector`, so there is no migration file to hand-edit this time.)

## Assignment 1 — Get the three endpoints working

Everything from the lesson's build, verified with curl:

| Method | Endpoint | Verifies |
|---|---|---|
| `POST` | `/api/documents/` | Upload → paragraph-chunk → batch-embed → save chunks |
| `GET`  | `/api/documents/` | List with `chunk_count` per document |
| `POST` | `/api/ask/` | Embed question → top-5 chunks via `CosineDistance` → grounded LLM answer |

### Required behavior

1. Ingestion chunks with the lesson's paragraph-based `chunk_text` (`max_chunk_size=800`)
2. Embeddings are generated with **one batch API call** per document (`generate_embeddings_batch`), not one call per chunk
3. Chunks are saved with `bulk_create`
4. The ask endpoint's system prompt instructs the LLM to **only** use the provided `<context>`, to **say so** if the context is insufficient, and **never** to fabricate
5. The response returns the answer AND the source chunks (title + ~200-char preview + a relevance score derived from distance)

## Assignment 2 — Exercise it

Upload **at least two documents on different topics** (paste in a long README, a blog post, your own study notes). Then ask **at least five questions** and save the questions + answers in a `NOTES.md` in your repo. Your five questions must include:

- **A question one document clearly covers** — the answer should come from the right source
- **A question the documents don't cover at all** — the LLM should admit it, not make something up
- **A question where the "wrong" document is a near-miss** — does retrieval pull chunks from the right one?

For each, note one line: did the answer come from the right chunks? (The `sources` array tells you.)

## Things to think about

- The lesson uses `temperature=0.3` on the generation step. What happens if you bump it to 0.9? Why is lower better for RAG?
- If the top-5 chunks are all from the same document, is that good or bad? When would you want diverse documents in your top-k?
- The system prompt explicitly says "do not make up information." Try **removing** that line and asking a question the docs don't cover. Does the LLM hallucinate?
- Why do we batch embeddings (one API call per document) instead of one call per chunk? How much faster is it? How much cheaper?

## Stretch

- **Chunk size experiment**: re-ingest one document with `max_chunk_size=200` and compare answers to the same questions against the 800-char version. Write 2-3 sentences in `NOTES.md` on what changed and why.
- **Metadata filter**: extend `POST /api/ask/` to accept an optional `document_id` so the user can scope the search to a single document.
- **Inline source citations**: change the prompt to ask the LLM to cite sources in the format `[Source: <title>]` after each claim it makes.
- **Chunk overlap**: add an `overlap` parameter to `chunk_text` so neighboring chunks share their boundary text. Does it help on questions whose answer straddles a paragraph break?

> Stuck? Have a code error? Use the ["4 Before Me"](https://docs.google.com/document/d/1nseOs5oabYBKNHfwJZNAR7GlU0zkZxNagsw63AD7XV0/edit) debugging checklist to help you solve it!
