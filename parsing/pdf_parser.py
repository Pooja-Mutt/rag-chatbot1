"""
PDF parsing functionality.
"""
from pypdf import PdfReader
from pydantic import BaseModel
from typing import BinaryIO
import io


class PDFMetadata(BaseModel):
    """Metadata extracted from PDF."""
    title: str | None = None
    author: str | None = None
    pages: int = 0
    text_length: int = 0


class PDFParser:
    """Parser for PDF files."""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_EXTENSIONS = {".pdf"}
    
    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> None:
        """
        Validate PDF file.
        
        Args:
            filename: Name of the file
            file_size: Size of the file in bytes
            
        Raises:
            ValueError: If file is invalid
        """
        # Check extension
        if not filename.lower().endswith(".pdf"):
            raise ValueError(f"Unsupported file type. Only PDF files are allowed.")
        
        # Check size
        if file_size == 0:
            raise ValueError("File is empty.")
        
        if file_size > cls.MAX_FILE_SIZE:
            raise ValueError(f"File too large. Maximum size is {cls.MAX_FILE_SIZE / (1024*1024):.1f}MB")
    
    @classmethod
    def parse(cls, file_content: bytes, filename: str) -> tuple[str, PDFMetadata]:
        """
        Parse PDF file and extract text and metadata.
        
        Args:
            file_content: Binary content of the PDF file
            filename: Name of the file
            
        Returns:
            Tuple of (extracted_text, metadata)
            
        Raises:
            ValueError: If file is invalid or corrupted
        """
        try:
            # Create file-like object
            pdf_file = io.BytesIO(file_content)
            
            # Read PDF
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text_parts: list[str] = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = "\n\n".join(text_parts).strip()
            
            if not full_text:
                raise ValueError("PDF contains no extractable text.")
            
            # Extract metadata
            metadata = reader.metadata or {}
            
            pdf_metadata = PDFMetadata(
                title=metadata.get("/Title", "").strip() or None,
                author=metadata.get("/Author", "").strip() or None,
                pages=len(reader.pages),
                text_length=len(full_text),
            )
            
            return full_text, pdf_metadata
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to parse PDF: {str(e)}")

