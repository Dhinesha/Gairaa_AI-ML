import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from backend.app.api.v1.analytics import router as analytics_router
from backend.app.api.v1.approvals import router as approvals_router
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.database import router as database_router
from backend.app.api.v1.safety import router as safety_router
from backend.app.api.v1.workflows import router as workflows_router
from backend.app.core.config import settings
from backend.app.core.redis_client import cache_client
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.entities import SafetyPolicyConfigModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("safety.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables created
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    # Initialize default safety policy in DB if empty
    db = SessionLocal()
    try:
        existing = db.query(SafetyPolicyConfigModel).first()
        if not existing:
            default_config = SafetyPolicyConfigModel(
                name="Default Production Safety Policy",
                is_active=True,
                max_workflow_steps=20,
                max_repeated_calls=3,
                max_execution_duration_seconds=300.0,
                max_tool_calls=50,
                max_retries=3,
                loop_cycle_threshold=2,
                max_no_progress_steps=3,
                auto_block_no_progress=True,
                sensitive_tools=[
                    "modify_employee_salary",
                    "delete_employee_record",
                    "execute_payment",
                    "drop_database_table",
                    "send_external_email",
                    "grant_admin_access",
                ],
                sensitive_argument_patterns=[
                    "password", "secret", "token", "api_key", "credit_card", "ssn",
                ],
            )
            db.add(default_config)
            db.commit()
            logger.info("Default safety policy seeded in database.")
    except Exception as e:
        logger.warning(f"Note during policy seeding: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down Agent Safety Engine...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agent Workflow Safety & Loop Prevention Engine API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,      # Disables Swagger UI (/docs)
    redoc_url=None,     # Disables ReDoc (/redoc)
    openapi_url=None,   # Disables OpenAPI Schema (/openapi.json)
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(workflows_router, prefix=settings.API_V1_STR)
app.include_router(approvals_router, prefix=settings.API_V1_STR)
app.include_router(safety_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(database_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint checking database and cache status."""
    db_ok = True
    try:
        db = SessionLocal()
        db.execute(Base.metadata.tables["workflows"].select().limit(1))
        db.close()
    except Exception:
        db_ok = False

    db_type = "PostgreSQL (Supabase Cloud)" if ("postgres" in settings.DATABASE_URL.lower()) else "SQLite Native DB"
    supabase_active = bool(settings.SUPABASE_URL and (settings.SUPABASE_KEY or settings.SUPABASE_SERVICE_ROLE_KEY)) or ("postgres" in settings.DATABASE_URL.lower())

    return {
        "status": "healthy" if db_ok else "degraded",
        "service": settings.PROJECT_NAME,
        "database_connected": db_ok,
        "database_type": db_type,
        "supabase_configured": supabase_active,
        "redis_connected": cache_client.is_connected,
        "redis_fallback_mode": not cache_client.is_connected,
    }


@app.get("/metrics", tags=["Monitoring"])
def metrics():
    """Prometheus monitoring metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
