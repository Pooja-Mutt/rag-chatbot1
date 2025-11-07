"""
NiceGUI application for RAG chatbot interface.
"""
from nicegui import ui
import httpx
import asyncio
from typing import Any


# API endpoint
API_BASE_URL = "http://localhost:8000"


class ChatApp:
    """Chat application with streaming support."""
    
    def __init__(self) -> None:
        """Initialize the chat app."""
        self.messages: list[dict[str, Any]] = []
        self.session_id: str | None = None
        self.chat_container: ui.column | None = None
        
    def create_ui(self) -> None:
        """Create the main UI."""
        ui.page_title("workingAgent - RAG Chatbot")
        
        with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4"):
            # Header
            ui.label("workingAgent - Document QA Chatbot").classes("text-2xl font-bold")
            ui.label("Ask questions and get streaming responses").classes("text-gray-600")
            
            # PDF Upload section
            with ui.card().classes("w-full p-4"):
                ui.label("Upload PDF Document").classes("font-bold mb-2")
                with ui.row().classes("w-full gap-2 items-center"):
                    self.upload_label = ui.label("No PDF uploaded").classes("text-sm text-gray-600")
                    self.upload_component = ui.upload(
                        on_upload=self.handle_pdf_upload,
                        auto_upload=True,
                        max_file_size=10 * 1024 * 1024,  # 10MB
                    ).props("accept=.pdf").classes("flex-1")
            
            # Chat container with scrollable area
            with ui.card().classes("w-full h-96"):
                self.chat_container = ui.column().classes("w-full h-full overflow-y-auto p-4 gap-2")
                
            # Input area
            with ui.row().classes("w-full gap-2"):
                self.input_field = ui.input(
                    placeholder="Type your message...",
                ).classes("flex-1").on("keydown.enter", self.send_message)
                ui.button("Send", on_click=self.send_message).classes("px-6")
                ui.button("Clear Chat", on_click=self.clear_chat).classes("px-4 bg-gray-200")
            
            # Status indicator
            self.status_label = ui.label("").classes("text-sm text-gray-500")
            
    async def send_message(self) -> None:
        """Send message and stream response."""
        message = self.input_field.value.strip()
        if not message:
            self.status_label.text = "Please enter a message"
            await asyncio.sleep(2)
            self.status_label.text = ""
            return
        
        # Clear input
        self.input_field.value = ""
        
        # Add user message to chat
        self.add_message("user", message)
        
        # Update status with async steps
        self.update_status_async("Analyzing question...")
        
        try:
            # Call streaming endpoint
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{API_BASE_URL}/stream",
                    json={"message": message, "session_id": self.session_id},
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        error_msg = error_text.decode()
                        # User-friendly error messages
                        if response.status_code == 400:
                            friendly_msg = f"Invalid request: {error_msg}. Please check your message and try again."
                        elif response.status_code == 500:
                            friendly_msg = f"Server error occurred. Please try again in a moment."
                        else:
                            friendly_msg = f"Error ({response.status_code}): {error_msg}"
                        self.add_message("error", friendly_msg)
                        self.status_label.text = "Error occurred"
                        return
                    
                    # Update status
                    self.update_status_async("Searching document...")
                    await asyncio.sleep(0.5)  # Brief delay to show status
                    
                    # Add assistant message container
                    assistant_label = self.add_streaming_message("assistant")
                    
                    # Update status
                    self.update_status_async("Generating response...")
                    
                    # Stream response
                    full_response = ""
                    async for chunk in response.aiter_text():
                        if chunk:
                            full_response += chunk
                            # Update the label directly (NiceGUI handles reactivity)
                            assistant_label.text = full_response
                            await asyncio.sleep(0.01)  # Small delay for UI updates
                    
                    # Update status
                    self.update_status_async("Response complete")
                    
        except httpx.TimeoutException:
            self.add_message("error", "Request timed out. Please try again.")
            self.status_label.text = "Request timed out"
        except httpx.RequestError as e:
            self.add_message("error", f"Connection error: Unable to reach the server. Please check if the backend is running.")
            self.status_label.text = "Connection error"
        except Exception as e:
            error_type = type(e).__name__
            friendly_msg = f"An unexpected error occurred: {error_type}. Please try again."
            self.add_message("error", friendly_msg)
            self.status_label.text = f"Error: {error_type}"
        finally:
            # Clear status after a delay
            await asyncio.sleep(2)
            self.status_label.text = ""
    
    def clear_chat(self) -> None:
        """Clear all chat messages."""
        self.messages.clear()
        if self.chat_container:
            self.chat_container.clear()
        self.add_message("system", "Chat cleared. Ready for new conversation.")
        self.status_label.text = ""
    
    def update_status_async(self, status: str) -> None:
        """Update status label asynchronously."""
        self.status_label.text = status
    
    def add_message(self, role: str, content: str) -> str:
        """Add a message to the chat."""
        msg_id = f"msg_{len(self.messages)}"
        
        # Create UI element
        with self.chat_container:
            with ui.card().classes(f"p-3 {'bg-blue-100' if role == 'user' else 'bg-gray-100' if role == 'assistant' else 'bg-red-100'}"):
                ui.label(role.upper()).classes("text-xs font-bold mb-1")
                ui.label(content).classes("text-sm whitespace-pre-wrap")
        
        self.messages.append({"id": msg_id, "role": role, "content": content})
        return msg_id
    
    def add_streaming_message(self, role: str) -> ui.label:
        """Add a streaming message container and return the label for updates."""
        msg_id = f"msg_{len(self.messages)}"
        
        # Create UI element
        with self.chat_container:
            with ui.card().classes(f"p-3 {'bg-blue-100' if role == 'user' else 'bg-gray-100' if role == 'assistant' else 'bg-red-100'}"):
                ui.label(role.upper()).classes("text-xs font-bold mb-1")
                msg_label = ui.label("").classes("text-sm whitespace-pre-wrap")
        
        self.messages.append({"id": msg_id, "role": role, "content": ""})
        return msg_label
    
    async def handle_pdf_upload(self, e) -> None:
        """Handle PDF file upload."""
        self.status_label.text = "Uploading PDF..."
        
        try:
            # NiceGUI upload event structure
            if not hasattr(e, 'file'):
                self.status_label.text = "Upload failed - no file in event"
                self.add_message("error", "PDF upload error: No file in upload event")
                return
            
            uploaded_file = e.file
            file_name = getattr(uploaded_file, 'name', 'document.pdf')
            
            # Fix double extension if present
            if file_name.endswith('.pdf.pdf'):
                file_name = file_name[:-4]
            
            # NiceGUI upload: read file content
            # NiceGUI with auto_upload=True saves files to a temp directory
            # We need to find the actual file location
            file_content = None
            import os
            import tempfile
            
            # Method 1: Try reading as file-like object (most common)
            if hasattr(uploaded_file, 'read'):
                try:
                    read_result = uploaded_file.read()
                    # Check if it's a coroutine (async method)
                    if asyncio.iscoroutine(read_result):
                        file_content = await read_result
                    else:
                        file_content = read_result
                    # Reset file pointer if possible
                    if hasattr(uploaded_file, 'seek'):
                        seek_result = uploaded_file.seek(0)
                        if asyncio.iscoroutine(seek_result):
                            await seek_result
                except Exception:
                    pass
            
            # Method 2: Try content attribute
            if not file_content and hasattr(uploaded_file, 'content'):
                content = uploaded_file.content
                if isinstance(content, bytes):
                    file_content = content
                elif hasattr(content, 'read'):
                    read_result = content.read()
                    # Check if it's a coroutine (async method)
                    if asyncio.iscoroutine(read_result):
                        file_content = await read_result
                    else:
                        file_content = read_result
                elif isinstance(content, str):
                    file_content = content.encode('utf-8')
            
            # Method 3: Try to find file in NiceGUI's upload directory
            # NiceGUI typically saves to a temp directory or uploads folder
            if not file_content and hasattr(uploaded_file, 'path'):
                file_path = uploaded_file.path
                
                # If it's just a filename, try to find it in common locations
                if file_path and not (os.sep in file_path or '/' in file_path or '\\' in file_path):
                    # It's just a filename, search for it
                    possible_dirs = [
                        tempfile.gettempdir(),
                        os.path.join(tempfile.gettempdir(), 'nicegui'),
                        os.path.join(os.getcwd(), 'uploads'),
                        os.path.join(os.path.expanduser('~'), '.nicegui', 'uploads'),
                        # Also check NiceGUI's default upload location
                        os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp'),
                        os.path.join('C:', 'Users', os.getenv('USERNAME', ''), 'AppData', 'Local', 'Temp'),
                    ]
                    
                    # Also try searching recursively in temp directory (last resort)
                    for base_dir in possible_dirs:
                        if os.path.exists(base_dir):
                            full_path = os.path.join(base_dir, file_path)
                            if os.path.exists(full_path) and os.path.isfile(full_path):
                                try:
                                    with open(full_path, "rb") as f:
                                        file_content = f.read()
                                    break
                                except Exception:
                                    continue
                    
                    # If still not found, try searching for files with similar names in temp
                    if not file_content:
                        try:
                            import glob
                            # Search for files matching the name pattern in temp directory
                            search_patterns = [
                                os.path.join(tempfile.gettempdir(), f"*{file_path}*"),
                                os.path.join(tempfile.gettempdir(), "**", file_path),
                            ]
                            for pattern in search_patterns:
                                matches = glob.glob(pattern, recursive=True)
                                if matches:
                                    try:
                                        with open(matches[0], "rb") as f:
                                            file_content = f.read()
                                        break
                                    except Exception:
                                        continue
                        except Exception:
                            pass
                
                # If it's a full path, try reading it directly
                elif file_path and (os.sep in file_path or '/' in file_path or '\\' in file_path):
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        try:
                            with open(file_path, "rb") as f:
                                file_content = f.read()
                        except Exception:
                            pass
            
            if not file_content:
                # Last resort: Try to get file from upload component's internal state
                # NiceGUI might store files differently
                try:
                    # Try accessing through the upload component
                    if hasattr(self.upload_component, '_uploaded_files'):
                        uploaded_files = self.upload_component._uploaded_files
                        if uploaded_files and len(uploaded_files) > 0:
                            last_file = uploaded_files[-1]
                            if hasattr(last_file, 'read'):
                                read_result = last_file.read()
                                if asyncio.iscoroutine(read_result):
                                    file_content = await read_result
                                else:
                                    file_content = read_result
                            elif hasattr(last_file, 'content'):
                                content = last_file.content
                                if isinstance(content, bytes):
                                    file_content = content
                                elif hasattr(content, 'read'):
                                    read_result = content.read()
                                    if asyncio.iscoroutine(read_result):
                                        file_content = await read_result
                                    else:
                                        file_content = read_result
                except Exception:
                    pass
            
            if not file_content:
                # Debug: show what we have - this will help us understand the structure
                file_type = type(uploaded_file).__name__
                all_attrs = dir(uploaded_file)
                # Get both callable and non-callable attributes
                attrs = []
                for attr in all_attrs:
                    if not attr.startswith('_'):
                        try:
                            val = getattr(uploaded_file, attr)
                            if not callable(val):
                                attrs.append(f"{attr}={type(val).__name__}")
                        except:
                            pass
                
                # Also try to print the actual object structure
                import json
                try:
                    obj_repr = str(uploaded_file)
                except:
                    obj_repr = "Could not represent object"
                
                error_msg = f"PDF upload error: Could not read file.\nType: {file_type}\nAttributes: {', '.join(attrs[:10])}\nObject: {obj_repr[:200]}"
                self.add_message("error", error_msg)
                self.status_label.text = "Upload failed - see error details"
                return
            
            # Ensure bytes
            if isinstance(file_content, str):
                file_content = file_content.encode('utf-8')
            
            # Upload to backend
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (file_name, file_content, "application/pdf")}
                data = {"session_id": self.session_id} if self.session_id else {}
                
                response = await client.post(
                    f"{API_BASE_URL}/upload",
                    files=files,
                    data=data,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    metadata = result.get('metadata', {})
                    
                    # Display PDF metadata
                    if metadata:
                        pages = metadata.get('pages', 0)
                        text_length = metadata.get('text_length', 0)
                        file_size_kb = len(file_content) / 1024
                        metadata_display = f"✓ {file_name} ({pages} pages, {file_size_kb:.1f} KB, {text_length:,} chars)"
                        self.upload_label.text = metadata_display
                        self.add_message("system", f"PDF uploaded successfully: {file_name}\n📄 {pages} pages | 📊 {text_length:,} characters | 💾 {file_size_kb:.1f} KB")
                    else:
                        self.upload_label.text = f"✓ {result['message']}"
                        self.add_message("system", f"PDF uploaded: {result['message']}")
                    
                    self.status_label.text = "PDF uploaded successfully!"
                else:
                    error = response.json().get("detail", "Upload failed")
                    # User-friendly error messages
                    if "not a PDF" in error.lower() or "unsupported" in error.lower():
                        friendly_msg = f"Invalid file type. Please upload a PDF file (.pdf extension)."
                    elif "too large" in error.lower() or "size" in error.lower():
                        friendly_msg = f"File too large. Maximum size is 10MB. Please choose a smaller file."
                    elif "empty" in error.lower():
                        friendly_msg = f"File is empty. Please upload a valid PDF file."
                    else:
                        friendly_msg = f"Upload failed: {error}. Please try again."
                    
                    self.upload_label.text = "Upload failed"
                    self.status_label.text = friendly_msg
                    self.add_message("error", friendly_msg)
                    
        except httpx.TimeoutException:
            self.upload_label.text = "Upload failed"
            self.status_label.text = "Upload timed out"
            self.add_message("error", "Upload timed out. Please try again with a smaller file.")
        except httpx.RequestError:
            self.upload_label.text = "Upload failed"
            self.status_label.text = "Connection error"
            self.add_message("error", "Unable to connect to server. Please check if the backend is running.")
        except Exception as e:
            error_type = type(e).__name__
            friendly_msg = f"Upload error: {error_type}. Please try again."
            self.upload_label.text = "Upload failed"
            self.status_label.text = friendly_msg
            self.add_message("error", friendly_msg)
        finally:
            await asyncio.sleep(3)
            if "successfully" in self.status_label.text.lower():
                self.status_label.text = ""


def main() -> None:
    """Run the NiceGUI app."""
    app = ChatApp()
    app.create_ui()
    ui.run(port=8080, title="workingAgent Chatbot", show=False)


# Remove guard to allow multiprocessing (required by NiceGUI)
# This allows run.py to import and call main() directly
if __name__ in {"__main__", "__mp_main__"}:
    main()

