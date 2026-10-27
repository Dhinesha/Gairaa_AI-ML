from fastapi import FastAPI

from app.database.database import engine, Base
from app.routers import employee_router, auth_router


Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Employee Management API",
    description="A RESTful API for managing employees, built with clean layered architecture.",
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",     # ReDoc UI at http://localhost:8000/redoc
)

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(employee_router.router, prefix="/api/v1")


@app.get("/", tags=["Health"])
def health_check():
    """Root endpoint — confirms the API is running."""
    return {
        "status": "healthy",
        "message": "Employee Management API is running!",
        "docs": "/docs",
    }
