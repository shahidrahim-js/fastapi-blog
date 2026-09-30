from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

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



@app.get("/api/posts")
def get_posts():
  return posts

@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
  for post in posts:
    if post.get("id") == post_id:
      return post
  raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")