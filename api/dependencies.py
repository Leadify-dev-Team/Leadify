"""
FastAPI Dependencies
Authentifizierung und gemeinsame Abhängigkeiten
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from api.config import settings
from api.database import APIDatabase, get_database


# API-Key Header Definition
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verifiziert API-Key aus Request-Header
    
    Args:
        api_key: API-Key aus X-API-KEY Header
    
    Returns:
        Validierter API-Key
    
    Raises:
        HTTPException: Bei fehlendem oder ungültigem API-Key
    """
    valid_keys = settings.get_api_keys()
    
    # Überprüfen ob API-Keys konfiguriert sind
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API-Keys nicht konfiguriert. Bitte API_KEYS Umgebungsvariable setzen."
        )
    
    # API-Key fehlt im Header
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API-Key fehlt. Bitte X-API-KEY Header setzen."
        )
    
    # API-Key ungültig
    if api_key not in valid_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ungültiger API-Key"
        )
    
    return api_key


def get_db() -> APIDatabase:
    """
    Gibt Datenbank-Instanz zurück
    FastAPI Dependency
    """
    return get_database()
