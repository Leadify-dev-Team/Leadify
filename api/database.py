"""
Datenbank-Layer für API
Kapselter Nur-Lese-Zugriff auf die Leadify-Datenbank
"""

import mariadb
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from api.config import settings


class APIDatabase:
    """
    Read-Only Datenbank-Wrapper für die API
    Vollständig getrennt von der bestehenden Database-Klasse
    """
    
    def __init__(self):
        """Initialisiert die Datenbankverbindung"""
        self.host = settings.DB_HOST
        self.user = settings.DB_USER
        self.password = settings.DB_PASSWORD
        self.database = settings.DB_DATABASE
        self.port = settings.DB_PORT
        self._connection = None
    
    def connect(self):
        """Stellt Verbindung zur Datenbank her"""
        if self._connection is None or not self.is_connected():
            try:
                self._connection = mariadb.connect(
                    host=self.host,
                    user=self.user,
                    port=self.port,
                    password=self.password,
                    database=self.database
                )
                print(f"[API-DB] Verbindung zu {self.database} hergestellt")
            except mariadb.Error as e:
                print(f"[API-DB ERROR] Verbindung fehlgeschlagen: {e}")
                raise
    
    def is_connected(self) -> bool:
        """Prüft, ob Verbindung aktiv ist"""
        if self._connection is None:
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except mariadb.Error:
            return False
    
    def disconnect(self):
        """Schließt die Datenbankverbindung"""
        if self._connection:
            try:
                self._connection.close()
                print("[API-DB] Verbindung geschlossen")
            except mariadb.Error as e:
                print(f"[API-DB ERROR] Fehler beim Schließen: {e}")
            finally:
                self._connection = None
    
    @contextmanager
    def get_cursor(self):
        """
        Context Manager für sichere Cursor-Verwendung
        Stellt sicher, dass Verbindung besteht und bereinigt Ressourcen
        """
        self.connect()
        cursor = self._connection.cursor(dictionary=True)
        try:
            yield cursor
        finally:
            cursor.close()
    
    def fetch_all(self, sql: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Führt SELECT-Query aus und gibt alle Ergebnisse zurück
        
        Args:
            sql: SQL-Query (nur SELECT erlaubt)
            params: Query-Parameter als Tuple
        
        Returns:
            Liste von Dictionaries (Zeilen)
        """
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Nur SELECT-Queries sind erlaubt (Read-Only API)")
        
        with self.get_cursor() as cursor:
            cursor.execute(sql, params or ())
            results = cursor.fetchall()
            return results if results else []
    
    def fetch_one(self, sql: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Führt SELECT-Query aus und gibt erste Zeile zurück
        
        Args:
            sql: SQL-Query (nur SELECT erlaubt)
            params: Query-Parameter als Tuple
        
        Returns:
            Dictionary oder None
        """
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Nur SELECT-Queries sind erlaubt (Read-Only API)")
        
        with self.get_cursor() as cursor:
            cursor.execute(sql, params or ())
            result = cursor.fetchone()
            return result


# Globale Instanz für die API
api_db = APIDatabase()


def get_database() -> APIDatabase:
    """
    Dependency-Funktion für FastAPI
    Gibt Datenbank-Instanz zurück
    """
    return api_db
