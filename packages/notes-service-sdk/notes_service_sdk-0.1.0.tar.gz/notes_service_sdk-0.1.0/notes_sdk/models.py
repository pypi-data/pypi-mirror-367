import uuid
from pydantic import BaseModel, ConfigDict
from typing import Optional

"""
These models define the data structures for the SDK user.
They are simplified versions of the backend schemas, focusing on what the developer using the SDK needs to interact with
"""

class NoteCreate(BaseModel):
    """Data model for creating a new note."""
    title: str
    content: Optional[str] = None

class NoteUpdate(BaseModel):
    """Data model for updating an existing note."""
    title: Optional[str] = None
    content: Optional[str] = None

class Note(BaseModel):
    """Data model representing a note returned from the API.
    This is what the SDK user will receive and interact with
    """
    id: uuid.UUID
    title: str
    content: Optional[str] = None
    owner_id: uuid.UUID

    # this coniguratio allows the model to be created from objects
    # like the dictionary response from the api
    model_config = ConfigDict(from_attributes=True)