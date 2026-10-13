from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import asyncio
import random

from app.api.routes.auth import router as auth_router
from app.api.routes.cases import router as cases_router
from app.api.routes.chat import router as chat_router
from app.api.routes.geography import router as geography_router
from app.api.routes.documents import router as documents_router
from app.api.routes.forensics import router as forensics_router
from app.api.routes.health import router as health_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.risk import router as risk_router
from app.api.routes.reconciliation import router as reconciliation_router
from app.api.routes.reports import router as reports_router
from app.api.routes.sanctions import router as sanctions_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.notifications import router as notifications_router
from app.api.routes.workflow import router as workflow_router

from app.core.exceptions import setup_exception_handlers
from app.db.session import engine
from app.db.base import Base

app = FastAPI(title="Trade Copilot API", version="0.1.0")

# Register global exception handlers
setup_exception_handlers(app)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Basic security hardening headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        return response

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    # Explicit origins are required because the API uses credentialed cookies;
    # browsers reject the '*' wildcard when credentials are included.
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(geography_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(reconciliation_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(sanctions_router, prefix="/api/v1")
app.include_router(forensics_router, prefix="/api/v1")
app.include_router(risk_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(workflow_router, prefix="/api/v1")
app.include_router(conversations_router, prefix="/api/v1")
app.include_router(notifications_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Trade Copilot API is running"}



@app.get("/")
def root():
    return {"message": "Trade Copilot API is running"}
