from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models
from .database import Base, engine, get_db
from .schemas import PostCreate, PostResponse, UserCreate, UserResponse

# It looks at models that inherit from Base and Create database tables (if tabel not exist) when the app starts 
Base.metadata.create_all(bind=engine)


# Set BASE_DIR to the absolute directory path where current file (main.py) is located.
# Path(__file__) returns file relative path eg: src/fastapi_blog/main.py
# Path(__file__).resolve() returns absolute path eg: /home/user/\fastapi-blog\src\fastapi_blog\main.py
# Path(__file__).resolve().parent returns parent folder path eg: /home/user/\fastapi-blog\src\fastapi_blog
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# Serve files from the static directory at the /static URL path
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

app.mount("/media", StaticFiles(directory=BASE_DIR/"media"), name="media")

templates = Jinja2Templates(directory=BASE_DIR/"templates")

# ----- Start HTML Template routes ------------------
# include_in_schema=False exclude this page route from API docs (swagger)
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
# The dictionary MUST include "request": Request as FastAPI required it.
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Post))
  posts = result.scalars().all()
  return templates.TemplateResponse(
    request,
    "home.html",
    {"posts": posts, "title": "Home"}
  )

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Post).where(models.Post.id == post_id))
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
def user_posts_page(request: Request, user_id: int, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.User).where(models.User.id == user_id))
  user = result.scalars().first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found"
    )
  result = db.execute(select(models.Post).where(models.Post.user_id == user.id))
  posts = result.scalars().all()
  return templates.TemplateResponse(
    request,
    "user_posts.html",
    {"posts": posts, "user": user, "title": f"{user.username}'s Posts"}
  )

# ------- End HTML Template routes ------------------------

# -------- Start API endpoints ------------------
@app.post(
    "/api/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
# get_db is a dependency injection
# This tells FastAPI before runing this function call get_db (defined in detabase.py) and pass the result as db parameter
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(
    select(models.User).where(models.User.username == user.username)
  )
  existing_user = result.scalars().first() # gived first user object if matched or none

  if existing_user:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Username already exists"
    )

  result = db.execute(
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
  db.commit()
  db.refresh(new_user)
  return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(
    select(models.User).where(models.User.id == user_id)
  )
  user = result.scalars().first()

  if user:
    return user

  raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
  )

@app.get("api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(
    select(models.User).where(models.User.id == user_id)
  )
  user = result.scalars().first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found."
    )
  
  result = db.execute(
    select(models.Post).where(models.Post.user_id == user.id)
  )
  posts = result.scalars().all()
  return posts


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Post))
  posts = result.scalars().all()
  return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.Post).where(models.Post.id == post_id))
  post = result.scalars().first()
  if post:
    return post
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
  result = db.execute(select(models.User).where(models.User.id == post.user_id))
  user = result.scalars().first()
  if not user:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="User not found"
    )
  
  new_post = models.Post(
    title = post.title,
    author = post.author,
    content = post.content
  )
  db.add(new_post)
  db.commit()
  db.refresh(new_post)
  return new_post

# -------- End API endpoints ---------------

#--- Exception handling for both API nad html template -----------
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
  message = (
    exception.detail
    if exception.detail
    else "An error occured. Please check your request and try again."
  )

  if request.url.path.startswith('/api'):
    return JSONResponse(
      status_code=exception.status_code,
      content={"detail": message}
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
def validation_exception(request: Request, exception: RequestValidationError):
  if request.url.path.startswith("/api"):
    return JSONResponse(
      status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
      content={"details": exception.errors()}
    )
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