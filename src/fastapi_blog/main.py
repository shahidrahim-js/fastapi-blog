from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi_blog.schemas import PostCreate, PostResponse

# Set BASE_DIR to the absolute directory path where current file (main.py) is located.
# Path(__file__) returns file relative path eg: src/fastapi_blog/main.py
# Path(__file__).resolve() returns absolute path eg: /home/user/\fastapi-blog\src\fastapi_blog\main.py
# Path(__file__).resolve().parent returns parent folder path eg: /home/user/\fastapi-blog\src\fastapi_blog
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# Serve files from the static directory at the /static URL path
app.mount("/static", StaticFiles(directory=BASE_DIR/"static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR/"templates")

posts: list[dict] = [
  {
    "id": 1,
    "author": "Raju Rastogi",
    "title": "Fast API is Awesome",
    "content": "This framework is really easy to use and super fast.",
    "created_at": "August 20, 2026"
  },
  {
    "id": 2,
    "author": "Shahjeb Rose",
    "title": "Python is Great for Web Development",
    "content": "Python is a great language for web development, and FastAPI makes it even better.",
    "created_at": "September 05, 2026"
  },
]

# include_in_schema=False exclude this page route from API docs (swagger)
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
  # The dictionary MUST include "request": Request as FastAPI required it.
  return templates.TemplateResponse(request, "home.html", {"posts": posts, "title": "Home"})

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
  for post in posts:
    if post.get("id") == post_id:
      title = post["title"][:50]
      return templates.TemplateResponse(
        request,
        "post.html",
        {"post": post, "title": title})
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


# ------- API endpoints
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
  return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
  for post in posts:
    if post.get("id") == post_id:
      return post
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post(
    "/api/post",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED
)
def create_post(post: PostCreate):
  new_id = max(p["id"] for p in posts) + 1 if posts else 1
  new_post = {
    "id": new_id,
    "author": post.author,
    "title": post.title,
    "content": post.content,
    "created_at": "October 02, 2026"
  }
  posts.append(new_post)
  return new_post

# end API endpoints ---------------

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