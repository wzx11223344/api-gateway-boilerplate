from typing import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


async def get_items(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[Sequence[Item], int]:
    """Fetch a paginated list of items.

    Returns:
        A tuple of (items list, total count).
    """
    count_q = select(func.count(Item.id))
    total = (await db.execute(count_q)).scalar_one()

    q = select(Item).offset(skip).limit(limit).order_by(Item.created_at.desc())
    result = await db.execute(q)
    items = result.scalars().all()
    return items, total


async def get_item(db: AsyncSession, item_id: str) -> Item | None:
    """Fetch a single item by id."""
    result = await db.execute(select(Item).where(Item.id == item_id))
    return result.scalar_one_or_none()


async def create_item(db: AsyncSession, data: ItemCreate, owner_id: str) -> Item:
    """Create a new item."""
    item = Item(
        title=data.title,
        description=data.description,
        owner_id=owner_id,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update_item(db: AsyncSession, item: Item, data: ItemUpdate) -> Item:
    """Update an existing item with partial data."""
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    await db.flush()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item: Item) -> None:
    """Delete an item from the database."""
    await db.delete(item)
    await db.flush()
