from datetime import datetime

from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ItemResponse(BaseModel):
    """Schema for item public response."""

    id: str
    title: str
    description: str | None = None
    owner_id: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
