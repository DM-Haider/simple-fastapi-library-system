import psycopg
from psycopg.rows import dict_row
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

# postgres connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "library_db",
    "user": "postgres",
    "password": "postgres",
}

app = FastAPI()

REQUIRED_FIELDS = ("title", "author", "publisher")


def get_connection():
    # open a new connection for each request, it closes when the block ends
    return psycopg.connect(**DB_CONFIG, row_factory=dict_row)


@app.get("/hello/{name}")
async def hello_name(name: str):
    return {"message": f"Hello {name}!"}


@app.get("/hello")
async def hello_query(name: str = "world"):
    return {"message": f"Hello {name}!"}


# -----------------------
# Books endpoints (data is stored in postgres now)
# -----------------------

@app.get("/books")
def list_books(query: str | None = None):
    if query is None:
        sql = "SELECT id, title, author, publisher FROM books ORDER BY id"
        params = ()
    else:
        sql = (
            "SELECT id, title, author, publisher FROM books "
            "WHERE title ILIKE %s OR author ILIKE %s OR publisher ILIKE %s "
            "ORDER BY id"
        )
        params = (f"%{query}%", f"%{query}%", f"%{query}%")

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    results = list(rows)

    if query is None:
        return {"count": len(results), "results": results}

    return {
        "query": query,
        "results_count": len(results),
        "results": results
    }


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with get_connection() as conn:
        book = conn.execute(
            "SELECT id, title, author, publisher FROM books WHERE id = %s",
            (book_id,),
        ).fetchone()

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(payload: dict):
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing)}"
        )

    with get_connection() as conn:
        book = conn.execute(
            "INSERT INTO books (title, author, publisher) "
            "VALUES (%s, %s, %s) "
            "RETURNING id, title, author, publisher",
            (payload["title"], payload["author"], payload["publisher"]),
        ).fetchone()
        conn.commit()

    return book


@app.patch("/books/{book_id}")
def update_book(book_id: int, payload: dict):
    fields = {field: payload[field] for field in REQUIRED_FIELDS if field in payload}
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid field to update"
        )

    # field names come from the fixed REQUIRED_FIELDS list, values go as %s params
    set_sql = ", ".join(f"{field} = %s" for field in fields)

    with get_connection() as conn:
        book = conn.execute(
            f"UPDATE books SET {set_sql} WHERE id = %s "
            "RETURNING id, title, author, publisher",
            [*fields.values(), book_id],
        ).fetchone()
        conn.commit()

    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return book


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    with get_connection() as conn:
        deleted = conn.execute(
            "DELETE FROM books WHERE id = %s RETURNING id",
            (book_id,),
        ).fetchone()
        conn.commit()

    if deleted is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


# -----------------------
# CORS
# -----------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
