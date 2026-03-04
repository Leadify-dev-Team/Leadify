"""
API Konfiguration
Verwaltet Umgebungsvariablen und API-Einstellungen
"""

from typing import Set
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API-Konfigurationseinstellungen"""
    
    # API Einstellungen
    API_TITLE: str = "Leadify ERP API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Read-Only REST API für ERP-Integration"
    
    # API Keys (Komma-getrennt)
    API_KEYS: str = ""
    
    # Datenbank
    DB_HOST: str = "localhost"
    DB_USER: str = "WIV_Denis"
    DB_PASSWORD: str = "denisHDD1996"
    DB_DATABASE: str = "leadify2"
    DB_PORT: int = 3306
    
    # Server
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_RELOAD: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignoriert unbekannte Felder aus .env
    
    def get_api_keys(self) -> Set[str]:
        """Gibt Set von gültigen API-Keys zurück"""
        if not self.API_KEYS:
            return set()
        return {key.strip() for key in self.API_KEYS.split(",") if key.strip()}


# Singleton-Instanz
settings = Settings()
