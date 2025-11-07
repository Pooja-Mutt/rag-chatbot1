"""
Simple script to run the application.
Run FastAPI backend and NiceGUI UI together.
"""
import subprocess
import sys
import os

def main():
    """Run both FastAPI and NiceGUI."""
    print("Starting MyAgent application...")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists(".env"):
        print("⚠️  WARNING: .env file not found!")
        print("Please create .env file with your OPENAI_API_KEY")
        print("You can copy .env.example to .env and add your key")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n1. Starting FastAPI backend on http://localhost:8000")
    print("2. Starting NiceGUI UI on http://localhost:8080")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 50)
    
    # Start FastAPI in background
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    
    # Start NiceGUI
    try:
        from ui.app import main as ui_main
        ui_main()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        fastapi_process.terminate()
        fastapi_process.wait()


if __name__ == "__main__":
    main()

