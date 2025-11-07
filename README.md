# MyAgent - RAG Chatbot

Minimal Document QA Chatbot with streaming responses and PDF upload.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env  # Add OPENAI_API_KEY
python run.py
```

Open http://localhost:8080

## Architecture

**Backend**: FastAPI with `/stream` (token streaming) and `/upload` (PDF parsing)  
**Agent**: Agno with OpenAI (gpt-4o-mini), session support  
**Parsing**: pypdf for text extraction, validation  
**UI**: NiceGUI with streaming display

**Design**: Simple RAG via context injection (first 8k chars). In-memory storage per session. Leverages Agno/FastAPI/Pydantic built-ins. Trade-off: no persistence, simple search. Next: vector DB, persistent storage.

follow the white rabbit

## Cursor Configuration

**Linters**: Ruff, Black, MyPy (configured in pyproject.toml)  
**Docs**: Used Cursor's built-in indexing for Agno/FastAPI/NiceGUI docs  
**No MCP servers or .cursorrules**: Built-in features sufficient  
**What helped**: Inline autocomplete, real-time linting, quick doc access

## Testing

```bash
pytest tests/ -v
```

