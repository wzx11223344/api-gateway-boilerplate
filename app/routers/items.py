from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate
from app.services import crud
from app.utils.database import get_db
from app.utils.deps import get_current_user

router = APIRouter(prefix="/items")


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new item belonging to the authenticated user."""
    item = await crud.create_item(db=db, data=data, owner_id=current_user.id)
    return item


@router.get("", response_model=dict)
async def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a paginated list of items."""
    items, total = await crud.get_items(db=db, skip=skip, limit=limit)
    return {
        "total": total,
        "items": [ItemResponse.model_validate(i) for i in items],
    }


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a single item by ID."""
    item = await crud.get_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: str,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an item owned by the authenticated user."""
    item = await crud.get_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to edit this item",
        )
    updated = await crud.update_item(db=db, item=item, data=data)
    return updated


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an item owned by the authenticated user."""
    item = await crud.get_item(db=db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item",
        )
    await crud.delete_item(db=db, item=item)
    return None
