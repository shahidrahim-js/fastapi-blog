from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi_blog import models
from fastapi_blog.database import get_db
from fastapi_blog.schemas import PostResponse, UserCreate, UserResponse, UserUpdate

# Create router instance
router = APIRouter(prefix="/api/users")

# In main.py we use the prefix "/api/users", while in routers/users.py we use
# an empty string ("") for the route path.
#
# Here, "" acts as the relative path, so the final endpoint becomes "/api/users".
#
# If we use "/" instead of "", the trailing slash will be included,
# and the final endpoint will become "/api/users/".
@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
# get_db is a dependency that uses FastAPI's dependency injection system.
# Before running this function, FastAPI calls get_db (defined in database.py)
# and passes the returned database session to the db parameter.
async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(
    select(models.User).where(models.User.username == user.username)
  )
  existing_user = result.scalars().first() # gived first user object if matched or none

  if existing_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Username already exists"
    )

  result = await db.execute(
    select(models.User).where(models.User.email == user.email)
  )
  existing_email = result.scalars().first() # gived first user object if matched or none

  if existing_email:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Email already exists"
    )

  new_user = models.User(
    username = user.username,
    email = user.email
  )

  db.add(new_user)
  await db.commit()
  await db.refresh(new_user)
  return new_user
