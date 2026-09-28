from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
@app.get("/posts", response_class=HTMLResponse, include_in_schema=False)
def home():
  return f"<h1>{posts[0]['title']}</h1>"

@app.get("/api/posts")
def get_posts():
  return posts
