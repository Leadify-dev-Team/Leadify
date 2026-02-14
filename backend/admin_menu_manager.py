from backend.database import Database


# ============================================================================
# MANAGER-KLASSE (Business-Logik / Datenbankoperationen)
# ============================================================================

class AdminMenuManager:
    """Verwaltet Backend-Operationen für das Admin-Menü"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_pending_leads_count(self):
        """
        Ermittelt die Anzahl der zum Löschen vorgemerkten Leads
        
        Returns:
            int: Anzahl der vorgemerkten Leads
        """
        try:
            sql = """
                SELECT COUNT(DISTINCT lead_id) as count 
                FROM lead_aktionen 
                WHERE aktion_typ = 'zum Löschen vorgemerkt'
            """
            result = self.db.fetch_one(sql)
            return result.get('count', 0) if result else 0
        except Exception as e:
            print(f"[ERROR] Fehler beim Zählen vorgemerkter Leads: {e}")
            return 0
    
    def get_pending_users_count(self):
        """
        Ermittelt die Anzahl der ausstehenden Benutzer zur Freigabe
        
        Returns:
            int: Anzahl der ausstehenden Benutzer
        """
        try:
            sql = """
                SELECT COUNT(*) as count FROM benutzer 
                WHERE is_approved = 0 
                AND passwort_hash IS NOT NULL AND passwort_hash != '' 
                AND session_token IS NOT NULL AND session_token != ''
            """
            result = self.db.fetch_one(sql)
            return result.get('count', 0) if result else 0
        except Exception as e:
            print(f"[ERROR] Fehler beim Zählen ausstehender Nutzer: {e}")
            return 0
    
    def get_notification_count(self):
        """
        Zählt die Gesamtanzahl der Benachrichtigungen (ausstehende Nutzer + vorgemerkte Leads)
        
        Returns:
            int: Gesamtanzahl der Benachrichtigungen
        """
        count = 0
        
        # Zähle ausstehende Nutzer zur Freigabe
        count += self.get_pending_users_count()
        
        # Zähle Leads zum Löschen
        count += self.get_pending_leads_count()
        
        return count
