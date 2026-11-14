import time
from typing import Any, Dict, List
from backend.app.safety.models import ToolOutcome

MOCK_EMPLOYEES_DB = [
    {
        "id": "EMP-101",
        "name": "Sarah Connor",
        "department": "Engineering",
        "role": "Principal Systems Architect",
        "salary": 165000,
        "email": "sarah.connor@antigravity.io",
        "status": "Active",
    },
    {
        "id": "EMP-102",
        "name": "John Anderson",
        "department": "Engineering",
        "role": "Senior Security Engineer",
        "salary": 145000,
        "email": "j.anderson@antigravity.io",
        "status": "Active",
    },
    {
        "id": "EMP-204",
        "name": "Elena Rostova",
        "department": "Finance",
        "role": "Senior Financial Controller",
        "salary": 130000,
        "email": "elena.rostova@antigravity.io",
        "status": "Active",
    },
    {
        "id": "EMP-305",
        "name": "Marcus Vance",
        "department": "Operations",
        "role": "Site Reliability Lead",
        "salary": 140000,
        "email": "marcus.v@antigravity.io",
        "status": "Active",
    },
]


def tool_search_employees(query: str = "", department: str = "", limit: int = 10) -> Dict[str, Any]:
    """Search employee directory by name, department, or keyword."""
    time.sleep(0.05)  # Simulate brief I/O
    q = (query or "").lower().strip()
    dept = (department or "").lower().strip()

    results = []
    for emp in MOCK_EMPLOYEES_DB:
        match_q = not q or q in emp["name"].lower() or q in emp["role"].lower()
        match_d = not dept or dept in emp["department"].lower()
        if match_q and match_d:
            results.append(emp)

    return {
        "count": len(results[:limit]),
        "query": query,
        "department": department,
        "employees": results[:limit],
    }


def tool_get_employee_details(employee_id: str) -> Dict[str, Any]:
    """Retrieve full employee profile record."""
    time.sleep(0.05)
    for emp in MOCK_EMPLOYEES_DB:
        if emp["id"].upper() == employee_id.upper().strip():
            return {
                "found": True,
                "profile": emp,
                "permissions": ["REPO_READ", "PROD_METRICS_VIEW"],
            }
    return {"found": False, "error": f"Employee {employee_id} not found."}


def tool_generate_report(title: str, records: List[Any], format: str = "markdown") -> Dict[str, Any]:
    """Compile records into a formatted executive summary report."""
    time.sleep(0.08)
    return {
        "report_id": f"REP-{int(time.time())}",
        "title": title,
        "format": format,
        "items_included": len(records),
        "summary": f"Report '{title}' generated successfully with {len(records)} verified records.",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%SZ"),
    }


def tool_modify_employee_salary(employee_id: str, new_salary: float, reason: str = "") -> Dict[str, Any]:
    """SENSITIVE: Modifies compensation structure in HR record."""
    time.sleep(0.1)
    for emp in MOCK_EMPLOYEES_DB:
        if emp["id"].upper() == employee_id.upper().strip():
            old_sal = emp["salary"]
            emp["salary"] = new_salary
            return {
                "success": True,
                "employee_id": employee_id,
                "previous_salary": old_sal,
                "updated_salary": new_salary,
                "reason": reason,
                "audit_timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ"),
            }
    return {"success": False, "error": f"Employee {employee_id} not found."}


def tool_delete_employee_record(employee_id: str, confirm: bool = False) -> Dict[str, Any]:
    """CRITICAL SENSITIVE: Permanently purge employee profile."""
    time.sleep(0.1)
    return {
        "success": True,
        "action": "RECORD_PURGED",
        "employee_id": employee_id,
        "deleted_at": time.strftime("%Y-%m-%d %H:%M:%SZ"),
    }


def tool_repeating_static_tool(ping: str = "health_ping") -> Dict[str, Any]:
    """Intentionally returns the exact same static output to test no-progress detection."""
    return {
        "status": "STATIC_NO_CHANGE",
        "value": 42,
        "cache_hit": True,
        "payload": "identical_static_content",
    }


def tool_flaky_error_tool(action: str = "sync") -> Dict[str, Any]:
    """Intentionally raises an error or fails to test unhandled error halting."""
    raise RuntimeError(f"Simulated network timeout connecting to downstream service '{action}'.")


def tool_sync_cache(sync: str = "cache") -> Dict[str, Any]:
    """Mock Tool B for cyclic loop simulation."""
    return {"status": "synced", "target": sync, "synced_keys": 128}


def tool_lookup_feed(lookup: str = "data_feed") -> Dict[str, Any]:
    """Mock Tool A for cyclic loop simulation."""
    return {"status": "feed_active", "feed": lookup, "items": 15}


def tool_inspect_uploaded_db(target: str = "uploaded_schema", include_foreign_keys: bool = True) -> Dict[str, Any]:
    """Inspects tables, columns, foreign keys, and constraints of uploaded database."""
    time.sleep(0.08)
    return {
        "status": "SCHEMA_INSPECTED",
        "database_type": "SQLite 3 Relational",
        "discovered_tables": ["students", "courses", "grades"],
        "table_schemas": {
            "students": {
                "columns": ["student_id (PK)", "name", "department", "gpa", "email"],
                "records": 5,
                "primary_key": "student_id",
            },
            "courses": {
                "columns": ["course_id (PK)", "course_name", "credits", "instructor"],
                "records": 3,
                "primary_key": "course_id",
            },
            "grades": {
                "columns": ["id (PK)", "student_id (FK)", "course_id (FK)", "grade"],
                "records": 5,
                "foreign_keys": ["student_id -> students.student_id", "course_id -> courses.course_id"],
            },
        },
        "relationships_detected": [
            "students (1) <---> (N) grades",
            "courses (1) <---> (N) grades",
        ],
    }


def tool_query_uploaded_db(query: str = "SELECT * FROM students", limit: int = 10) -> Dict[str, Any]:
    """Executes safe analytical queries against the uploaded database."""
    time.sleep(0.06)
    return {
        "status": "QUERY_SUCCESS",
        "query_executed": query,
        "rows_returned": 3,
        "results": [
            {"department": "Artificial Intelligence", "student_count": 2, "avg_gpa": 3.785},
            {"department": "Computer Science", "student_count": 1, "avg_gpa": 3.850},
            {"department": "Cyber Security", "student_count": 1, "avg_gpa": 3.950},
        ],
        "top_performing_department": "Cyber Security (Avg GPA 3.95)",
    }


def tool_explain_database(topic: str = "SchemaArchitecture", language: str = "both") -> Dict[str, Any]:
    """Synthesizes comprehensive pedagogical database teaching summary in English and Tamil."""
    time.sleep(0.05)
    return {
        "status": "TEACHING_REPORT_GENERATED",
        "explanation_en": (
            "Architecture Summary: This is a normalized relational database (3NF) containing 3 entities: "
            "1) 'students' represents registered learners with GPA metrics. "
            "2) 'courses' maintains curriculum offerings and credit weights. "
            "3) 'grades' serves as an associative junction table capturing enrollment and academic performance via foreign keys."
        ),
        "explanation_ta": (
            "டேட்டாபேஸ் விளக்கம்: இது 3 முக்கிய டேபிள்களைக் கொண்ட ஒரு Relational Database: "
            "1) 'students' டேபிள் மாணவர்களின் பெயர், துறை மற்றும் GPA விவரங்களை சேமிக்கிறது. "
            "2) 'courses' டேபிள் பாடங்கள் மற்றும் கிரெடிட் விவரங்களை கொண்டுள்ளது. "
            "3) 'grades' டேபிள் மாணவர்களையும் பாடங்களையும் Foreign Key மூலம் இணைத்து தேர்ச்சி நிலையை விவரிக்கிறது."
        ),
        "suggested_student_queries": [
            "SELECT name, gpa FROM students ORDER BY gpa DESC;",
            "SELECT c.course_name, COUNT(g.student_id) FROM courses c LEFT JOIN grades g ON c.course_id = g.course_id GROUP BY c.course_id;",
        ],
    }


def tool_modify_database_table(table_name: str = "students", action: str = "DROP_TABLE") -> Dict[str, Any]:
    """CRITICAL SENSITIVE: Mutation on database schema requiring Human Approval."""
    time.sleep(0.1)
    return {
        "status": "MUTATION_ATTEMPTED",
        "table": table_name,
        "action": action,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ"),
    }

