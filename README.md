# workingAgent - RAG Chatbot

QA Chatbot with streaming responses and PDF upload.

## Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Configure OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Run the application
python run.py
```

**Access:**

- UI: http://localhost:8080
- API Docs: http://localhost:8000/docs

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
