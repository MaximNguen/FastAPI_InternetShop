from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path, FastAPI
from database import get_db
from app.models.post import PostModel

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, update, delete

router = APIRouter(
    prefix="/posts",
    tags=["reviews"]
)

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: Annotated[int, Path(description="Id post")], db: Session = Depends(get_db)):
    post = db.scalars(select(PostModel).where(and_(PostModel.id == post_id, PostModel.is_active == True))).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.is_active = False
    db.commit()
    return {"status": "success", "message": "Product marked as inactive"}
