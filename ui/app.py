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
        ui.page_title("MyAgent - RAG Chatbot")
        
        with ui.column().classes("w-full max-w-4xl mx-auto p-4 gap-4"):
            # Header
            ui.label("MyAgent - Document QA Chatbot").classes("text-2xl font-bold")
            ui.label("Ask questions and get streaming responses").classes("text-gray-600")
            
            # PDF Upload section
            with ui.card().classes("w-full p-4"):
                ui.label("Upload PDF Document").classes("font-bold mb-2")
                with ui.row().classes("w-full gap-2 items-center"):
                    self.upload_label = ui.label("No PDF uploaded").classes("text-sm text-gray-600")
                    ui.upload(
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
            
            # Status indicator
            self.status_label = ui.label("").classes("text-sm text-gray-500")
            
    async def send_message(self) -> None:
        """Send message and stream response."""
        message = self.input_field.value.strip()
        if not message:
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
                        self.add_message("error", f"Error: {response.status_code} - {error_text.decode()}")
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
                    
        except Exception as e:
            self.add_message("error", f"Error: {str(e)}")
            self.status_label.text = f"Error: {str(e)}"
        finally:
            # Clear status after a delay
            await asyncio.sleep(2)
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
            # NiceGUI upload event provides file info
            if not e.uploaded_files:
                self.status_label.text = "No file selected"
                return
            
            uploaded_file = e.uploaded_files[0]
            file_path = uploaded_file.name
            
            # Read file content
            with open(file_path, "rb") as f:
                file_content = f.read()
            
            # Upload to backend
            async with httpx.AsyncClient(timeout=30.0) as client:
                files = {"file": (uploaded_file.name, file_content, "application/pdf")}
                data = {"session_id": self.session_id} if self.session_id else {}
                
                response = await client.post(
                    f"{API_BASE_URL}/upload",
                    files=files,
                    data=data,
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.upload_label.text = f"✓ {result['message']}"
                    self.status_label.text = "PDF uploaded successfully!"
                    # Add success message to chat
                    self.add_message("system", f"PDF uploaded: {result['message']}")
                else:
                    error = response.json().get("detail", "Upload failed")
                    self.upload_label.text = "Upload failed"
                    self.status_label.text = f"Error: {error}"
                    self.add_message("error", f"PDF upload failed: {error}")
                    
        except Exception as e:
            self.upload_label.text = "Upload failed"
            self.status_label.text = f"Error: {str(e)}"
            self.add_message("error", f"PDF upload error: {str(e)}")
        finally:
            await asyncio.sleep(3)
            if "successfully" in self.status_label.text.lower():
                self.status_label.text = ""


def main() -> None:
    """Run the NiceGUI app."""
    app = ChatApp()
    app.create_ui()
    ui.run(port=8080, title="MyAgent Chatbot", show=False)


if __name__ == "__main__":
    main()

