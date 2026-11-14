import csv
import json
import logging
import os
import sqlite3
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

logger = logging.getLogger("database.router")

router = APIRouter(prefix="/database", tags=["Database Explainer"])

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads", "databases")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ColumnInfo(BaseModel):
    name: str
    type: str
    is_primary_key: bool
    not_null: bool


class TableInfo(BaseModel):
    name: str
    row_count: int
    columns: List[ColumnInfo]
    preview_rows: List[Dict[str, Any]]


class DatabaseUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size_bytes: int
    database_type: str
    table_count: int
    total_records: int
    tables: List[TableInfo]
    summary_en: str
    summary_ta: str


def inspect_sqlite_db(db_path: str) -> Dict[str, Any]:
    """Inspect an SQLite database to extract tables, schema, row counts, and sample preview."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get non-internal table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    table_rows = cursor.fetchall()
    table_names = [row["name"] for row in table_rows]

    tables_data: List[Dict[str, Any]] = []
    total_records = 0

    for tbl in table_names:
        # Get column info
        cursor.execute(f"PRAGMA table_info(`{tbl}`);")
        cols_raw = cursor.fetchall()
        cols = [
            {
                "name": c["name"],
                "type": c["type"] or "TEXT",
                "is_primary_key": bool(c["pk"]),
                "not_null": bool(c["notnull"]),
            }
            for c in cols_raw
        ]

        # Get row count
        cursor.execute(f"SELECT COUNT(*) as cnt FROM `{tbl}`;")
        cnt_row = cursor.fetchone()
        row_count = cnt_row["cnt"] if cnt_row else 0
        total_records += row_count

        # Get preview rows (up to 5)
        cursor.execute(f"SELECT * FROM `{tbl}` LIMIT 5;")
        sample_rows = cursor.fetchall()
        preview = [dict(r) for r in sample_rows]

        tables_data.append(
            {
                "name": tbl,
                "row_count": row_count,
                "columns": cols,
                "preview_rows": preview,
            }
        )

    conn.close()
    return {
        "tables": tables_data,
        "table_count": len(tables_data),
        "total_records": total_records,
    }


def convert_csv_to_sqlite(csv_path: str, sqlite_path: str, table_name: str) -> None:
    """Convert an uploaded CSV file into an SQLite table."""
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV file is empty or missing headers.")

        fields = [f.strip() for f in reader.fieldnames if f]
        clean_tbl = "".join(c if c.isalnum() else "_" for c in table_name)

        col_defs = ", ".join([f"`{col}` TEXT" for col in fields])
        cursor.execute(f"CREATE TABLE IF NOT EXISTS `{clean_tbl}` ({col_defs});")

        placeholders = ", ".join(["?"] * len(fields))
        insert_sql = f"INSERT INTO `{clean_tbl}` VALUES ({placeholders})"

        batch = []
        for row in reader:
            batch.append([row.get(col, "") for col in fields])
            if len(batch) >= 1000:
                cursor.executemany(insert_sql, batch)
                batch = []
        if batch:
            cursor.executemany(insert_sql, batch)

    conn.commit()
    conn.close()


def convert_json_to_sqlite(json_path: str, sqlite_path: str, table_name: str) -> None:
    """Convert an uploaded JSON file into an SQLite table."""
    with open(json_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list) or len(data) == 0 or not isinstance(data[0], dict):
        raise ValueError("JSON file must contain an array of objects.")

    fields = list(data[0].keys())
    clean_tbl = "".join(c if c.isalnum() else "_" for c in table_name)

    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()

    col_defs = ", ".join([f"`{col}` TEXT" for col in fields])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS `{clean_tbl}` ({col_defs});")

    placeholders = ", ".join(["?"] * len(fields))
    insert_sql = f"INSERT INTO `{clean_tbl}` VALUES ({placeholders})"

    rows = [[str(item.get(col, "")) for col in fields] for item in data]
    cursor.executemany(insert_sql, rows)
    conn.commit()
    conn.close()


@router.post("/upload", response_model=DatabaseUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_database(file: UploadFile = File(...)):
    """Upload a custom database (.db, .sqlite, .csv, .json) and automatically inspect its schema."""
    filename = file.filename or "uploaded_database.db"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in (".db", ".sqlite", ".sqlite3", ".csv", ".json", ".sql"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Please upload an SQLite (.db, .sqlite), CSV (.csv), or JSON (.json) file.",
        )

    file_id = str(uuid.uuid4())
    stored_path = os.path.join(UPLOAD_DIR, f"{file_id}_{filename}")

    # Write file to disk
    contents = await file.read()
    with open(stored_path, "wb") as f:
        f.write(contents)

    sqlite_db_path = stored_path
    base_name = os.path.splitext(filename)[0]

    # Convert CSV or JSON if necessary
    try:
        if ext == ".csv":
            sqlite_db_path = os.path.join(UPLOAD_DIR, f"{file_id}_{base_name}.db")
            convert_csv_to_sqlite(stored_path, sqlite_db_path, base_name)
        elif ext == ".json":
            sqlite_db_path = os.path.join(UPLOAD_DIR, f"{file_id}_{base_name}.db")
            convert_json_to_sqlite(stored_path, sqlite_db_path, base_name)
        elif ext == ".sql":
            sqlite_db_path = os.path.join(UPLOAD_DIR, f"{file_id}_{base_name}.db")
            conn = sqlite3.connect(sqlite_db_path)
            conn.executescript(contents.decode("utf-8", errors="ignore"))
            conn.commit()
            conn.close()

        # Inspect the SQLite database
        inspection = inspect_sqlite_db(sqlite_db_path)
    except Exception as e:
        logger.error(f"Error parsing uploaded database {filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse database file: {str(e)}",
        )

    tbl_names = [t["name"] for t in inspection["tables"]]
    tables_summary = ", ".join([f"'{t}'" for t in tbl_names])

    summary_en = (
        f"Successfully loaded database '{filename}' with {inspection['table_count']} table(s) ({tables_summary}) "
        f"containing {inspection['total_records']} total records. Ready for AI inspection & safe query execution."
    )
    summary_ta = (
        f"'{filename}' டேட்டாபேஸ் வெற்றிகரமாக பதிவேற்றப்பட்டது. இதில் {inspection['table_count']} டேபிள்கள் ({tables_summary}) "
        f"மற்றும் மொத்தம் {inspection['total_records']} பதிவுகள் உள்ளன. AI ஆய்வுக்கு தயார்!"
    )

    return DatabaseUploadResponse(
        file_id=file_id,
        filename=filename,
        file_size_bytes=len(contents),
        database_type="SQLite Relational Database",
        table_count=inspection["table_count"],
        total_records=inspection["total_records"],
        tables=inspection["tables"],
        summary_en=summary_en,
        summary_ta=summary_ta,
    )


@router.get("/sample", response_model=DatabaseUploadResponse)
def get_sample_database(preset: str = "university"):
    """Returns a pre-loaded sample dataset (university, banking, healthcare, ecommerce) for instant 1-click evaluation."""
    preset_clean = preset.lower().strip()

    if preset_clean in ("banking", "finance", "bank"):
        sample_path = os.path.join(UPLOAD_DIR, "enterprise_banking_vault.db")
        target_name = "enterprise_banking_vault.db"
    elif preset_clean in ("healthcare", "hospital", "patient"):
        csv_path = os.path.join(UPLOAD_DIR, "healthcare_patient_registry.csv")
        sample_path = os.path.join(UPLOAD_DIR, "healthcare_patient_registry.db")
        if not os.path.exists(sample_path) and os.path.exists(csv_path):
            convert_csv_to_sqlite(csv_path, sample_path, "healthcare_patient_registry")
        target_name = "healthcare_patient_registry.csv"
    elif preset_clean in ("ecommerce", "retail", "sales"):
        csv_path = os.path.join(UPLOAD_DIR, "ecommerce_sales_transactions.csv")
        sample_path = os.path.join(UPLOAD_DIR, "ecommerce_sales_transactions.db")
        if not os.path.exists(sample_path) and os.path.exists(csv_path):
            convert_csv_to_sqlite(csv_path, sample_path, "ecommerce_sales_transactions")
        target_name = "ecommerce_sales_transactions.csv"
    elif preset_clean in ("students", "academic", "student"):
        csv_path = os.path.join(UPLOAD_DIR, "student_academic_records.csv")
        sample_path = os.path.join(UPLOAD_DIR, "student_academic_records.db")
        if not os.path.exists(sample_path) and os.path.exists(csv_path):
            convert_csv_to_sqlite(csv_path, sample_path, "student_academic_records")
        target_name = "student_academic_records.csv"
    else:
        sample_path = os.path.join(UPLOAD_DIR, "sample_university.db")
        target_name = "sample_university.db"

    if not os.path.exists(sample_path):
        raise HTTPException(status_code=404, detail=f"Sample dataset '{preset}' not found.")

    inspection = inspect_sqlite_db(sample_path)
    tbl_names = [t["name"] for t in inspection["tables"]]
    tables_summary = ", ".join([f"'{t}'" for t in tbl_names])

    return DatabaseUploadResponse(
        file_id=f"sample-{preset_clean}",
        filename=target_name,
        file_size_bytes=os.path.getsize(sample_path),
        database_type="SQLite Relational Database",
        table_count=inspection["table_count"],
        total_records=inspection["total_records"],
        tables=inspection["tables"],
        summary_en=(
            f"Pre-loaded '{target_name}' dataset with {inspection['table_count']} table(s) ({tables_summary}) "
            f"and {inspection['total_records']} records. Perfect for student viva and agent loop evaluation."
        ),
        summary_ta=(
            f"மாதிரி '{target_name}' தரவுத்தொகுப்பு ({inspection['table_count']} டேபிள்கள்: {tables_summary}, "
            f"மொத்தம் {inspection['total_records']} பதிவுகள்). AI ஆய்வு மற்றும் செயல்விளக்கத்திற்கு தயார்!"
        ),
    )

