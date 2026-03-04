"""
FastAPI Haupt-Anwendung
Read-Only REST API für ERP-Integration
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from api.config import settings
from api.routes import router as lead_router
from api.database import api_db


# ============================================================================
# FastAPI App erstellen
# ============================================================================

app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ============================================================================
# Middleware
# ============================================================================

# CORS-Middleware (falls benötigt für Browser-Zugriff)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken!
    allow_credentials=True,
    allow_methods=["GET"],  # Nur GET, da Read-Only
    allow_headers=["*"],
)


# Logging-Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Loggt alle eingehenden Requests"""
    start_time = time.time()
    
    # Request verarbeiten
    response = await call_next(request)
    
    # Zeit berechnen
    process_time = time.time() - start_time
    
    # Log ausgeben
    print(f"[API] {request.method} {request.url.path} - Status: {response.status_code} - Zeit: {process_time:.3f}s")
    
    return response


# ============================================================================
# Event Handlers
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Wird beim Start der API ausgeführt"""
    print("=" * 70)
    print(f"  {settings.API_TITLE} v{settings.API_VERSION}")
    print("  Read-Only REST API für ERP-Integration")
    print("=" * 70)
    
    # Datenbankverbindung herstellen
    try:
        api_db.connect()
        print(f"[OK] Datenbankverbindung erfolgreich ({settings.DB_DATABASE})")
    except Exception as e:
        print(f"[ERROR] Datenbankverbindung fehlgeschlagen: {e}")
        raise
    
    # API-Keys prüfen
    api_keys = settings.get_api_keys()
    if not api_keys:
        print("[WARNING] Keine API-Keys konfiguriert! Bitte API_KEYS setzen.")
    else:
        print(f"[OK] {len(api_keys)} API-Key(s) konfiguriert")
    
    print(f"[OK] Server gestartet auf http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"[OK] API-Dokumentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Wird beim Beenden der API ausgeführt"""
    print("\n[API] Server wird heruntergefahren...")
    api_db.disconnect()
    print("[OK] Datenbankverbindung geschlossen")


# ============================================================================
# Routen einbinden
# ============================================================================

app.include_router(lead_router)


# ============================================================================
# Health-Check Endpoint
# ============================================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
    description="Prüft ob API und Datenbank erreichbar sind"
)
async def health_check():
    """
    Health-Check Endpoint
    Prüft Status der API und Datenbankverbindung
    """
    db_status = "connected" if api_db.is_connected() else "disconnected"
    
    return {
        "status": "healthy" if api_db.is_connected() else "unhealthy",
        "api_version": settings.API_VERSION,
        "database": db_status
    }


# ============================================================================
# Root Endpoint
# ============================================================================

@app.get(
    "/",
    tags=["System"],
    summary="API Info",
    description="Gibt grundlegende API-Informationen zurück"
)
async def root():
    """
    Root-Endpoint mit API-Informationen
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "documentation": "/docs",
        "health": "/health",
        "endpoints": {
            "leads": "/api/leads",
            "lead_detail": "/api/leads/{id}"
        }
    }


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Globaler Exception Handler"""
    print(f"[ERROR] Unerwarteter Fehler: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "Ein unerwarteter Fehler ist aufgetreten"
        }
    )


# ============================================================================
# Haupteinstiegspunkt (für direkten Start)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
