from fastapi import FastAPI

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

@app.get("/")
def home():
  return {"message": "Wow! our first fastapi API."}

@app.get("/api/posts")
def get_posts():
  return posts
