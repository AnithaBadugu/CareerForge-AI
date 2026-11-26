# CareerForge AI

CareerForge AI is a Streamlit career development app using LangGraph, Agno agents, and an MCP server. It now includes **resume upload and local RAG retrieval**.

## Features
- Career profile, skill-gap analysis, six-week roadmap, interview practice, and downloadable report.
- Upload a PDF, DOCX, or TXT resume.
- Extract resume text, split it into overlapping chunks, and retrieve relevant chunks using local TF-IDF similarity.
- Ask questions about the uploaded resume; answers are instructed to use retrieved resume passages only.
- MCP tools provide job-role skills, skill comparison, and learning suggestions.
- Uses Groq and/or OpenAI. Configure at least one provider; if the preferred provider fails, the app tries the other configured provider.

## Setup (Windows)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add at least one valid key:

```env
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key
```

Run:

```bash
streamlit run app.py
```

## Resume RAG
The app supports text-based PDF, DOCX, and TXT. It uses TF-IDF and cosine similarity locally, so resume retrieval does not require a separate embedding key or vector database. Scanned image-only PDFs need OCR before text can be retrieved.

## Troubleshooting
- Add at least one working provider key.
- If generation fails, the app displays the exception; check whether the model is available and whether the provider quota is exhausted.
- MCP starts as a local stdio subprocess; run the app from the project root with dependencies installed.
- Do not commit `.env` or upload private resumes to public repositories.

## Deploy on Render
Use the included `render.yaml`, then add one or both API keys in Render's environment settings. Keep API keys private.


## Account and dashboard upgrade
- Register/login/logout with password hashes (Werkzeug) and SQLite storage.
- Career analyses are stored per account and are only retrieved for that account.
- Dashboard graphs use the actual MCP matched/missing skill results.
- Download the full Markdown report, PDF report, or skill-status CSV.
- Existing LangGraph, agents, MCP server, and resume RAG implementation are retained.

First run creates `careerforge.db` automatically. Do not commit this database or private resume data.


## Fast career plan mode

This version uses one Groq model request for the complete career plan, with a 15-second request timeout and no automatic retries. MCP skill matching has an 8-second timeout and falls back to the local role-skill list if MCP is unavailable. Set `GROQ_MODEL=openai/gpt-oss-20b` in `.env`. Total completion time depends on API response speed and network conditions; no external API workflow can be guaranteed to finish within a fixed number of seconds.


## Study profile and visual dashboard update
- The career form now accepts education level, degree, specialization, institution, graduation year, certifications, academic projects, career interests, weekly study hours, and learning preference.
- These study details are included in the LangGraph career-plan prompt and displayed in the profile tab.
- Dashboard and career-plan pages include Plotly skill coverage pie charts and skill comparison bar charts.
- Resume Q&A uses plain-text completion, while the structured career-plan request keeps JSON mode. This avoids the Groq error that requires a message to contain the word JSON when `response_format` is `json_object`.
