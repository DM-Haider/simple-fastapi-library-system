# FastAPI Library System

A simple library management system built with **FastAPI**.
Books are stored in a **PostgreSQL** database.
(In the first version the data was just a Python list inside the code. Now it lives in a real database.)

## Features

- List all books (with optional search)
- Get a single book by id
- Add a new book
- Partially update a book
- Delete a book

## API Endpoints

| Method | Endpoint | Description | Success Status |
|---|---|---|---|
| GET | `/books` | List all books (add `?query=...` to search by title/author/publisher) | 200 |
| GET | `/books/{id}` | Get a single book | 200 |
| POST | `/books` | Add a new book | 201 |
| PATCH | `/books/{id}` | Update some fields of a book | 200 |
| DELETE | `/books/{id}` | Delete a book | 204 |

**Error responses:**

- `400 Bad Request` — required fields are missing on POST (`title`, `author`, `publisher`)
- `404 Not Found` — no book exists with the given id

**Book object:**

```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "publisher": "Prentice Hall"
}
```

## Database Setup

The app needs a PostgreSQL database running on localhost.
The connection settings are at the top of `main.py` (`DB_CONFIG`).

1. Install PostgreSQL
2. Create the database and the books table:

```sql
CREATE DATABASE library_db;

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    publisher TEXT NOT NULL
);
```

## Installation

```bash
git clone https://github.com/DM-Haider/simple-fastapi-library-system.git
cd fastapi-library-system
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
uvicorn main:app --reload
```

The API is now available at `http://127.0.0.1:8000`

Interactive documentation (Swagger UI): `http://127.0.0.1:8000/docs`

### Examples

```bash
# List all books
curl http://127.0.0.1:8000/books

# Search books
curl "http://127.0.0.1:8000/books?query=python"

# Add a new book
curl -X POST http://127.0.0.1:8000/books \
  -H "Content-Type: application/json" \
  -d '{"title": "Dune", "author": "Frank Herbert", "publisher": "Chilton"}'

# Update a book
curl -X PATCH http://127.0.0.1:8000/books/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Clean Code (2nd Ed.)"}'

# Delete a book
curl -X DELETE http://127.0.0.1:8000/books/1
```

## Project Structure

```
├── main.py            # FastAPI app with all endpoints
├── requirements.txt   # Project dependencies
└── README.md
```

## Tech Stack

- Python
- FastAPI
- Uvicorn
- PostgreSQL (with psycopg)
