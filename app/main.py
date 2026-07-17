from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, items, users
from app.utils.database import check_db_connection, engine


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """Manage application lifecycle.

    On startup, verify database connectivity.
    On shutdown, dispose of the async engine.
    """
    # Startup
    if await check_db_connection():
        print("Database connection established.")
    else:
        print("WARNING: Could not connect to database.")

    yield

    # Shutdown
    await engine.dispose()
    print("Database engine disposed.")


app = FastAPI(
    title="API Gateway Boilerplate",
    description="A production-ready FastAPI backend scaffold with JWT auth and CRUD operations.",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Auth"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["Users"])
app.include_router(items.router, prefix=settings.API_V1_PREFIX, tags=["Items"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
async def health_check():
    """Return a simple health-check response."""
    return {"status": "healthy", "service": "api-gateway-boilerplate"}
