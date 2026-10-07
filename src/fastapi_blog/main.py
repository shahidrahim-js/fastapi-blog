from pathlib import Path
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exception_handlers import (
  http_exception_handler,
  request_validation_exception_handler
)
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import models
from fastapi_blog.database import Base, engine, get_db
from fastapi_blog.schemas import PostCreate, PostResponse, UserCreate, PostUpdate, UserResponse, UserUpdate

from fastapi_blog.routers import users

# It looks at models that inherit from Base and Create database tables (if tabel not exist) when the app starts 
# Base.metadata.create_all(bind=engine)

# Using lifespan function to handle startup and shutdown events.
@asynccontextmanager
async def lifespan(_app: FastAPI):
  # Startup
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield
  # Shutdown
  await engine.dispose()


# Set BASE_DIR to the absolute directory path where current file (main.py) is located.
# Path(__file__) returns file relative path eg: src/fastapi_blog/main.py
# Path(__file__).resolve() returns absolute path eg: /home/user/\fastapi-blog\src\fastapi_blog\main.py
# Path(__file__).resolve().parent returns parent folder path eg: /home/user/\fastapi-blog\src\fastapi_blog
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(lifespan=lifespan)

# Serve files from the static directory at the /static URL path
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

app.mount("/media", StaticFiles(directory=BASE_DIR/"media"), name="media")

app.include_router(users.router)

templates = Jinja2Templates(directory=BASE_DIR/"templates")

# ----- Start HTML Template routes ------------------
# include_in_schema=False exclude this page route from API docs (swagger)
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
# The dictionary MUST include "request": Request as FastAPI required it.
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(select(models.Post).options(selectinload(models.Post.author))) #Egerly loading author of the Post
  posts = result.scalars().all()
  return templates.TemplateResponse(
    request,
    "home.html",
    {"posts": posts, "title": "Home"}
  )

@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(
    select(models.Post)
    .options(selectinload(models.Post.author))
    .where(models.Post.id == post_id)
  )
  post = result.scalars().first()
  if post:
    title = post.title[:50]
    return templates.TemplateResponse(
      request,
      "post.html",
      {"post": post, "title": title}
    )
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
  request: Request,
  user_id: int,
  db: Annotated[AsyncSession, Depends(get_db)]
):
  result = await db.execute(select(models.User).where(models.User.id == user_id))
  user = result.scalars().first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found"
    )
  result = await db.execute(
    select(models.Post)
    .options(selectinload(models.Post.author))
    .where(models.Post.user_id == user.id)
  )
  posts = result.scalars().all()
  return templates.TemplateResponse(
    request,
    "user_posts.html",
    {"posts": posts, "user": user, "title": f"{user.username}'s Posts"}
  )

# ------- End HTML Template routes ------------------------

# -------- Start API endpoints ------------------

@app.get("/api/posts", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(
    select(models.Post).options(selectinload(models.Post.author))
  )
  posts = result.scalars().all()
  return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(
    select(models.Post)
    .options(selectinload(models.Post.author))
    .where(models.Post.id == post_id)
  )
  post = result.scalars().first()
  if post:
    return post
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.put("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_full(
  post_id: int,
  post_data: PostCreate,
  db: Annotated[AsyncSession, Depends(get_db)]
):
  result = await db.execute(
    select(models.Post).where(models.Post.id == post_id)
  )
  post = result.scalars().first()
  if not post:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Post not found"
    )
  if post_data.user_id != post.user_id:
    result = await db.execute(select(models.User).where(models.User.id == post_data.user_id))
    user = result.scalars().first()
    if not user:
      raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
      )
  post.title = post_data.title
  post.content = post_data.content
  post.user_id = post_data.user_id

  await db.commit()
  await db.refresh(post, attribute_names=["author"])
  return post

@app.patch("/api/posts/{post_id}", response_model=PostResponse)
async def update_post_partial(
  post_id: int,
  post_data: PostUpdate,
  db: Annotated[AsyncSession, Depends(get_db)]
):
  result = await db.execute(
    select(models.Post).where(models.Post.id == post_id)
  )
  post = result.scalars().first()
  if not post:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Post not found"
    )
  
  update_data = post_data.model_dump(exclude_unset=True)
  for field, value in update_data.items():
    setattr(post, field, value)

  await db.commit()
  await db.refresh(post, attribute_names=["author"])
  return post

@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(
    select(models.Post).where(models.Post.id == post_id)
  )
  post = result.scalars().first()
  if not post:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

  await db.delete(post)
  await db.commit()

@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
  result = await db.execute(
    select(models.User).where(models.User.id == post.user_id)
  )
  user = result.scalars().first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found"
    )
  
  new_post = models.Post(
    title = post.title,
    content = post.content,
    user_id = post.user_id
  )
  db.add(new_post)
  await db.commit()
  await db.refresh(new_post, attribute_names=["author"]) # 'attribute_names' -> On create new post, it reurns author in response
  return new_post

# -------- End API endpoints ---------------

#--- Exception handling for both API andd html template -----------
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
  if request.url.path.startswith('/api'):
    return await http_exception_handler(request, exception)
  
  message = (
    exception.detail
    if exception.detail
    else "An error occured. Please check your request and try again."
  )
  return templates.TemplateResponse(
    request,
    "error.html",
    {
      "status_code": exception.status_code,
      "title": exception.status_code,
      "message": message
    },
    status_code=exception.status_code
  )

# --- Validation HTTP Exception handling for both API and html template -------
@app.exception_handler(RequestValidationError)
async def validation_exception(request: Request, exception: RequestValidationError):
  if request.url.path.startswith("/api"):
    return await request_validation_exception_handler(request, exception)
    
  return templates.TemplateResponse(
    request,
    "error.html",
    {
      "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
      "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
      "message": "Invalid request. Please check your input and try again."
    },
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
  )