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
# Run all tests
pytest tests/ -v

# Expected: 17 tests passing
# - 9 unit tests (agent, PDF parser)
# - 8 integration tests (endpoints, streaming, upload flow)
```

**Quick Test:**

1. Start app: `python run.py`
2. Open: http://localhost:8080
3. Upload PDF → Ask question → Verify streaming works

## Enhancements

- Clear Chat & Remove PDF buttons
- Better error messages & input validation
- PDF metadata display (pages, size, chars)
- Enhanced async status updates
- Performance optimizations

See [CHANGELOG.md](CHANGELOG.md) for details.

## Deployment

See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) for AWS deployment options.

**Quick AWS Test:**

1. Deploy to EC2 (follow AWS_DEPLOYMENT.md)
2. Open: `http://YOUR_EC2_IP:8080`
3. Test: Upload PDF → Ask question → Verify streaming
