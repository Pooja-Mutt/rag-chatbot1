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

[To be completed]

## Cursor Configuration

[To be completed]

## Testing

```bash
pytest tests/ -v
```

## License

MIT

