# How to Run the App

## Simple Method: Run in Two Terminals

### Terminal 1 - Backend:
```bash
cd "C:\Users\Pooja Mutt\projects\MyAgent"
venv\Scripts\activate
python -m uvicorn backend.main:app --reload
```

### Terminal 2 - UI:
```bash
cd "C:\Users\Pooja Mutt\projects\MyAgent"
venv\Scripts\activate
python ui/app.py
```

Then open http://localhost:8080 in your browser.

## Alternative: Use run.py (if it works)

```bash
python run.py
```

