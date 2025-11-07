"""
FastAPI application with streaming endpoint for RAG chatbot.
"""
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from agent.agent import create_agent
from parsing.pdf_parser import PDFParser, PDFMetadata

# Load environment variables
load_dotenv()

# Check for required environment variables at startup
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables!")
    print("Please create a .env file with your OPENAI_API_KEY")
    print("You can copy .env.example to .env and add your key")

app = FastAPI(
    title="workingAgent - RAG Chatbot",
    description="Document QA Chatbot with streaming responses",
    version="0.1.0",
)

# Allow CORS for NiceGUI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str
    session_id: str | None = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "workingAgent API is running"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


async def stream_agent_response(prompt: str, session_id: str | None = None) -> str:
    """
    Stream agent response token by token.
    
    Args:
        prompt: User's question
        session_id: Optional session ID for conversation history
        
    Yields:
        Text chunks as they are generated
    """
    try:
        agent = create_agent()
        
        # Get PDF content if available for this session
        storage_key = session_id or "default"
        pdf_context = ""
        if storage_key in pdf_storage:
            pdf_text = pdf_storage[storage_key]
            # Add PDF context to prompt (simple RAG approach)
            pdf_context = f"\n\n--- Document Content ---\n{pdf_text[:8000]}\n--- End Document ---\n\n"
            # Truncate to avoid token limits, keeping most recent content
        
        # Combine PDF context with user prompt
        enhanced_prompt = pdf_context + prompt if pdf_context else prompt
        
        # Run agent with streaming enabled
        response = agent.run(
            enhanced_prompt,
            stream=True,
            session_id=session_id,
        )
        
        # Stream the response
        for event in response:
            if hasattr(event, "content") and event.content:
                yield event.content
            elif hasattr(event, "messages") and event.messages:
                for message in event.messages:
                    if hasattr(message, "content") and message.content:
                        yield message.content
                        
    except Exception as e:
        yield f"\n\nError: {str(e)}"


@app.post("/stream")
async def stream_chat(request: ChatRequest):
    """
    Stream chatbot response endpoint.
    
    Returns streaming response with agent's answer.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    return StreamingResponse(
        stream_agent_response(request.message, request.session_id),
        media_type="text/plain",
    )


class UploadResponse(BaseModel):
    """Response model for PDF upload."""
    success: bool
    message: str
    metadata: PDFMetadata | None = None


# In-memory storage for PDF content (simple implementation)
# In production, use a proper database or vector store
pdf_storage: dict[str, str] = {}  # session_id -> pdf_text


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str | None = None,
):
    """
    Upload and parse PDF file.
    
    Returns parsed text and metadata.
    """
    try:
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file
        PDFParser.validate_file(file.filename or "unknown.pdf", file_size)
        
        # Parse PDF
        text, metadata = PDFParser.parse(file_content, file.filename or "unknown.pdf")
        
        # Store PDF content (use session_id or default)
        storage_key = session_id or "default"
        pdf_storage[storage_key] = text
        
        return UploadResponse(
            success=True,
            message=f"PDF uploaded and parsed successfully. {metadata.pages} pages, {metadata.text_length} characters.",
            metadata=metadata,
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")


@app.get("/pdf/info")
async def get_pdf_info(session_id: str | None = None):
    """
    Get information about uploaded PDF.
    """
    storage_key = session_id or "default"
    if storage_key not in pdf_storage:
        return {"has_pdf": False, "message": "No PDF uploaded for this session"}
    
    text = pdf_storage[storage_key]
    return {
        "has_pdf": True,
        "text_length": len(text),
        "message": f"PDF available with {len(text)} characters",
    }

