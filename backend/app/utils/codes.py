"""
Human-readable code generation, e.g. EMP-000001, AST-000001, RT-000001.

Codes are derived from the row's own primary key, but that creates a
chicken-and-egg problem when the code column is NOT NULL: a first flush
with employee_code=None to "get an id" violates the constraint before an
id is ever assigned. `reserve_id_and_code` avoids that by pulling the next
value from the table's own identity sequence *before* the row is
constructed, so the INSERT carries both the id and the formatted code in
one shot — no partial/invalid intermediate row ever hits the DB.
"""
from sqlalchemy import text
from sqlalchemy.orm import Session


def format_code(prefix: str, numeric_id: int, width: int = 6) -> str:
    return f"{prefix}-{numeric_id:0{width}d}"


def reserve_id_and_code(db: Session, *, table_name: str, prefix: str, width: int = 6) -> tuple[int, str]:
    """Reserves the next id from `<table_name>_id_seq` and formats it as a
    code. Table/column names are developer-controlled constants here (never
    user input), so this is not a SQL-injection vector despite the string
    interpolation."""
    sequence_name = f"{table_name}_id_seq"
    next_id = db.execute(text(f"SELECT nextval('{sequence_name}')")).scalar_one()
    return next_id, format_code(prefix, next_id, width)
