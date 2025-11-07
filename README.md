# MyAgent - RAG Chatbot

A minimal Document QA Chatbot that streams responses and can answer questions about uploaded PDFs.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e ".[dev]"
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

4. Run the application:

**Option A: Run both backend and UI together:**
```bash
python run.py
```

**Option B: Run separately:**

Terminal 1 - Backend:
```bash
python -m uvicorn backend.main:app --reload
```

Terminal 2 - UI:
```bash
python ui/app.py
```

Then open http://localhost:8080 in your browser.

## Architecture

The application follows a clean separation of concerns:

### Components

- **Backend (`backend/`)**: FastAPI application handling API requests
  - `/stream`: Streaming endpoint for token-by-token responses
  - `/upload`: PDF upload and parsing endpoint
  - `/health`: Health check endpoint
  
- **Agent (`agent/`)**: Agno agent configuration
  - OpenAI model integration (gpt-4o-mini by default)
  - Session management for conversation history
  - Configurable via environment variables

- **Parsing (`parsing/`)**: PDF processing
  - File validation (type, size, empty checks)
  - Text extraction using pypdf
  - Metadata extraction

- **UI (`ui/`)**: NiceGUI interface
  - Streaming chat display
  - PDF upload component
  - Async status signals

### Design Decisions

**Simple RAG Implementation**: PDF content is injected directly into the prompt context (first 8000 characters). This is the simplest approach that works for the assignment requirements. For production, a vector database would be more efficient.

**In-Memory Storage**: PDF content is stored in memory per session. This is sufficient for the assignment scope. Production would use a database or vector store.

**Streaming First**: The streaming endpoint was built first, then PDF upload was added. This follows the assignment requirement to "streaming comes first."

**Minimal Abstractions**: We leverage Agno, FastAPI, and Pydantic's built-in features rather than creating custom abstractions. Only added thin layers where necessary (PDF storage) with documented rationale.

### Trade-offs

- **Pros**: Simple, maintainable, leverages libraries effectively
- **Limitations**: 
  - In-memory storage (lost on restart)
  - Simple context injection (not semantic search)
  - Single session support (no multi-user)
- **What to add next**: Vector database, persistent storage, multi-session support, rate limiting

follow the white rabbit

## Cursor Configuration

This project was developed using Cursor IDE with the following configuration:

### MCP Servers

No custom MCP servers were configured. Instead, I leveraged:
- Cursor's built-in documentation indexing for Agno, FastAPI, and NiceGUI
- Web search capabilities for library documentation
- Inline code suggestions and autocomplete

### Linters and Formatters

- **Ruff**: Configured in `pyproject.toml` with line length 100, Python 3.13 target
- **Black**: Configured for code formatting (line length 100)
- **MyPy**: Type checking enabled (Python 3.13, strict return types)

Linter errors are surfaced directly in the IDE with inline highlighting.

### .cursorrules

No custom `.cursorrules` file was used. The project structure and clear separation of concerns made the codebase self-documenting.

### Documentation Indexing

Cursor's built-in documentation indexing was used for:
- Agno library (https://docs.agno.com)
- FastAPI (https://fastapi.tiangolo.com)
- NiceGUI (https://nicegui.io/documentation)

### What Helped Move Faster

1. **Inline Suggestions**: Cursor's autocomplete helped quickly implement Pydantic models and FastAPI endpoints
2. **Code Navigation**: Easy jumping between files helped maintain consistency
3. **Error Detection**: Real-time linting caught type errors early
4. **Documentation Access**: Quick access to library docs without leaving the IDE

The combination of Cursor's AI assistance and traditional IDE features allowed for rapid development while maintaining code quality.

## Testing

```bash
pytest tests/ -v
```

## License

MIT

