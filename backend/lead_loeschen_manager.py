from backend.database import Database


# ============================================================================
# MANAGER-KLASSE (Business-Logik / Datenbankoperationen)
# ============================================================================

class LeadLoeschenManager:
    """Verwaltet Backend-Operationen für das Löschen von Leads"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_leads_for_deletion(self):
        """
        Lädt Leads die zum Löschen vorgemerkt sind oder abgelehnt wurden
        
        Returns:
            list: Liste der Leads die zum Löschen bereit sind
        """
        try:
            sql = """
                SELECT DISTINCT
                    l.lead_id,
                    f.name as firma_name,
                    CONCAT(a.vorname, ' ', a.nachname) as ansprechpartner,
                    p.produkt as produktgruppe,
                    s.status as status_name,
                    l.status_id,
                    l.datum_erfasst,
                    CONCAT(b.vorname, ' ', b.nachname) as erfasser,
                    CASE 
                        WHEN la.aktion_typ = 'zum Löschen vorgemerkt' THEN 1 
                        ELSE 0 
                    END as ist_vorgemerkt
                FROM lead l
                LEFT JOIN ansprechpartner a ON l.ansprechpartner_id = a.id
                LEFT JOIN firma f ON a.firma_id = f.id
                LEFT JOIN produktgruppe p ON l.produktgruppe_id = p.produkt_id
                LEFT JOIN status s ON l.status_id = s.id
                LEFT JOIN benutzer b ON l.erfasser_id = b.benutzer_id
                LEFT JOIN lead_aktionen la ON l.lead_id = la.lead_id AND la.aktion_typ = 'zum Löschen vorgemerkt'
                WHERE l.status_id IN (4, 6) OR la.aktion_typ = 'zum Löschen vorgemerkt'
                ORDER BY l.datum_erfasst DESC
            """
            
            results = self.db.fetch_all(sql)
            return results if results else []
        except Exception as e:
            return []
    
    def delete_leads(self, lead_ids: list):
        """
        Löscht Leads endgültig mit allen abhängigen Daten
        
        Args:
            lead_ids: Liste der Lead-IDs die gelöscht werden sollen
            
        Returns:
            tuple: (success: bool, deleted_count: int, error_message: str oder None)
        """
        if not lead_ids:
            return (False, 0, "Keine Leads zum Löschen ausgewählt")
        
        try:
            deleted_count = 0
            for lead_id in lead_ids:
                # Lösche zuerst abhängige Einträge
                # 1. Lead-Aktionen löschen
                sql_aktionen = "DELETE FROM lead_aktionen WHERE lead_id = ?"
                self.db.query(sql_aktionen, (lead_id,))
                
                # 2. Kommentare löschen
                sql_kommentare = "DELETE FROM kommentar WHERE lead_id = ?"
                self.db.query(sql_kommentare, (lead_id,))
                
                # 3. Lead selbst löschen
                sql_lead = "DELETE FROM lead WHERE lead_id = ?"
                self.db.query(sql_lead, (lead_id,))
                deleted_count += 1
            
            return (True, deleted_count, None)
        except Exception as e:
            error_msg = f"Fehler beim Löschen: {str(e)}"
            return (False, 0, error_msg)
