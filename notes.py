import sys
import psycopg

DB = "host=localhost port=5432 dbname=notes user=student password=devpassword"


def setup():
    with psycopg.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                body TEXT,
                created_at TIMESTAMPTZ DEFAULT now()
            )
        """)


def add(title, body=""):
    with psycopg.connect(DB) as conn:
        conn.execute("INSERT INTO notes (title, body) VALUES (%s, %s)", (title, body))
    print(f"Added: {title}")


def list_notes():
    with psycopg.connect(DB) as conn:
        rows = conn.execute(
            "SELECT id, title, created_at FROM notes ORDER BY id"
        ).fetchall()
    if not rows:
        print("No notes yet.")
    for note_id, title, created in rows:
        print(f"{note_id:>3}  {created:%Y-%m-%d %H:%M}  {title}")


def show(note_id):
    with psycopg.connect(DB) as conn:
        row = conn.execute(
            "SELECT title, body FROM notes WHERE id = %s", (note_id,)
        ).fetchone()
    if row:
        print(f"# {row[0]}\n\n{row[1]}")
    else:
        print("Note not found.")


def search(word):
    pattern = f"%{word}%"
    with psycopg.connect(DB) as conn:
        rows = conn.execute(
            "SELECT id, title FROM notes WHERE title ILIKE %s OR body ILIKE %s",
            (pattern, pattern),
        ).fetchall()
    for note_id, title in rows:
        print(f"{note_id:>3}  {title}")
    print(f"{len(rows)} result(s).")


def delete(note_id):
    with psycopg.connect(DB) as conn:
        result = conn.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    print("Deleted." if result.rowcount else "Note not found.")


def usage():
    print("Usage:")
    print('  python notes.py add "Title" "Body text"')
    print("  python notes.py list")
    print("  python notes.py show 1")
    print("  python notes.py search word")
    print("  python notes.py delete 1")


if __name__ == "__main__":
    setup()
    args = sys.argv[1:]

    if not args:
        usage()
    elif args[0] == "add" and len(args) >= 2:
        add(args[1], args[2] if len(args) > 2 else "")
    elif args[0] == "list":
        list_notes()
    elif args[0] == "show" and len(args) == 2:
        show(int(args[1]))
    elif args[0] == "search" and len(args) == 2:
        search(args[1])
    elif args[0] == "delete" and len(args) == 2:
        delete(int(args[1]))
    else:
        usage()
