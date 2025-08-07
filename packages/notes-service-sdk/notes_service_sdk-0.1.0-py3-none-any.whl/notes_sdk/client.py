import httpx
from typing import List, Optional
import uuid

from .exceptions import APIError,AuthenticationError
from .models import Note, NoteCreate, NoteUpdate

class NotesSDK:
    """The main client for interacting with the Notes Services API."""

    def __init__(self, api_key: str, base_url: str = "http://127.0.0.1:8000"):
        """Initializes the Sdk client.

        Args: 
            api_key: The API key for authentication.
            base_url: The base URL of the Notes Service API.
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.base_url = base_url
        self.api_key = api_key

        # Create an async HTTP client with he API key set in the default headers
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"api-key": self.api_key},
            timeout=10.0,
        )

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """A private helper method to handle all API requests."""
        try:
            response = await self._client.request(method, endpoint, **kwargs)
            
            # Raise exceptions for specific error status codes
            if response.status_code == 401:
                raise AuthenticationError("Invalid API Key.")
            
            response.raise_for_status() # Raises an HTTPError for 4xx/5xx responses
            
            # For 204 No Content, there's no body to parse
            if response.status_code == 204:
                return {}

            return response.json()

        except httpx.HTTPStatusError as e:
            # Catch client/server errors and wrap them in our custom exception
            raise APIError(f"API Error on {e.request.url}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            # Catch network/connection errors
            raise APIError(f"Request failed for {e.request.url}: {str(e)}")
    
    async def create_note(self, title: str, content: Optional[str] = None) -> Note:
        """
        Creates a new note.

        Args:
            title: The title of the note.
            content: The content of the note.

        Returns:
            A Note object representing the newly created note.
        """
        note_data = NoteCreate(title=title, content=content)
        response_data = await self._request(
            "POST",
            "/api/v1/notes/",
            json=note_data.model_dump()
        )
        return Note(**response_data)

    async def get_notes(self) -> List[Note]:
        """
        Retrieves all notes for the authenticated user.

        Returns:
            A list of Note objects.
        """
        response_data = await self._request("GET", "/api/v1/notes/")
        return [Note(**item) for item in response_data]
    
    async def update_note(self, note_id: uuid.UUID, title: Optional[str] = None, content: Optional[str] = None) -> Note:
        """
        Updates an existing note.

        Args:
            note_id: The ID of the note to update.
            title: The new title for the note (optional).
            content: The new content for the note (optional).

        Returns:
            A Note object representing the updated note.
        """
        update_data = NoteUpdate(title=title, content=content).model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("At least one field (title or content) must be provided for update.")
            
        response_data = await self._request(
            "PUT",
            f"/api/v1/notes/{note_id}",
            json=update_data
        )
        return Note(**response_data)
    
    async def delete_note(self, note_id: uuid.UUID) -> None:
        """
        Deletes a note.

        Args:
            note_id: The ID of the note to delete.
        """
        await self._request("DELETE", f"/api/v1/notes/{note_id}")

    async def close(self):
        """Closes the underlying HTTP client session."""
        await self._client.aclose()
