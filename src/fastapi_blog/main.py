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
from fastapi_blog.routers import users, posts

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

templates = Jinja2Templates(directory=BASE_DIR/"templates")

# include_router() accepts only one router at a time.
# app.include_router(users.router, posts.router) ❌ This is incorrect.
# So calling app.include_router() separately for each router.
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])

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