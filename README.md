## FastAPI Project

This is a simple FastAPI project built with **Python** and **uv**.

## Requirements
* Python 3.14+
* uv

## Setup
Clone the project:

```python
  git clone <your-github-repository-url>
  cd <project-folder>
```
Install the project  dependencies:

```
  uv sync
```

## Run the Application
Start the FastAPI development server:

```
  uv run fastapi dev src/fastapi_blog/main.py
```

This application will run at 
```
  http://127.0.0.1:8000
  or
  http://localhost:8000
```

## API Documentation
FastAPI provides interactive API documentation.

Open this URL in your browser:

```
  http://127.0.0.1:8000/docs
  or
  http://localhost:8000/docs
```
You can use the documentation page to test the API.

## Project Structure

```text
.
├── src/
│   └── fastapi_blog/
│       ├── __init__.py
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── posts.py
│       │   └── users.py
│       ├── static
│       │   ├── css
│       │   ├── js
│       │   └── images
│       └── templates 
│           ├── layout.html
│           ├── home.html
│           ├── users.html
│           └── user_posts.html
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

## Dependencies
The Project uses:
* FastAPI
* Uvicorn
* uv for Python package and project management
* aiosqlite
* sqlalchemy

## Development
After changing the code, restart the development server if needed.

The --reload option automatically reloads the server when code changes:

```
  uv run fastapi dev src/fastapi_blog/main.py
```

## License
This project is for learning and development.