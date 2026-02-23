from backend.database import Database


# ============================================================================
# MANAGER-KLASSE (Business-Logik / Datenbankoperationen)
# ============================================================================

class BenutzerfreigabeManager:
    """Verwaltet Backend-Operationen für die Benutzerfreigabe"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_pending_users(self):
        """
        Lädt alle Benutzer mit is_approved = 0 und Passwort + Token
        
        Returns:
            list: Liste der ausstehenden Benutzer
        """
        try:
            sql = """
                SELECT benutzer_id, vorname, nachname, email, rolle_id
                FROM benutzer 
                WHERE is_approved = 0 
                AND passwort_hash IS NOT NULL AND passwort_hash != '' 
                AND session_token IS NOT NULL AND session_token != ''
                ORDER BY benutzer_id DESC
            """
            return self.db.fetch_all(sql)
        except Exception as e:
            return []
    
    def approve_user(self, user_id: int):
        """
        Genehmigt einen Benutzer (setzt is_approved auf 1)
        
        Args:
            user_id: ID des Benutzers
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            sql = "UPDATE benutzer SET is_approved = 1 WHERE benutzer_id = ?"
            self.db.query(sql, (user_id,))
            return True
        except Exception as e:
            return False
    
    def reject_user(self, user_id: int):
        """
        Lehnt einen Benutzer ab und löscht ihn aus der Datenbank
        
        Args:
            user_id: ID des Benutzers
            
        Returns:
            bool: True bei Erfolg, False bei Fehler
        """
        try:
            sql = "DELETE FROM benutzer WHERE benutzer_id = ?"
            self.db.query(sql, (user_id,))
            return True
        except Exception as e:
            return False
