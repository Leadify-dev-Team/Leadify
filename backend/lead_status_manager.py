from backend.database import Database

# ============================================================================
# MODEL-KLASSE (Daten-Objekt)
# ============================================================================

class Lead:
    """Repräsentiert einen Lead mit allen Details"""
    
    def __init__(self, data: dict):
        """Erstellt Lead-Objekt aus Datenbank-Dictionary"""
        self.lead_id = data.get('lead_id')
        self.datum_erfasst = data.get('datum_erfasst')
        self.status_id = data.get('status_id')
        self.bearbeiter_id = data.get('bearbeiter_id')
        self.erfasser_id = data.get('erfasser_id')
        
        # Zusätzliche Infos (aus JOINs)
        self.kunde_name = data.get('kunde_name', 'Unbekannt')
        self.produkt_name = data.get('produkt_name', 'Unbekannt')
        self.status_name = data.get('status_name', 'Offen')
        self.bearbeiter_name = data.get('bearbeiter_name', 'Nicht zugewiesen')
    
    def __str__(self):
        return f"Lead #{self.lead_id} - {self.kunde_name} ({self.status_name})"


# ============================================================================
# MANAGER-KLASSE (Business-Logik / Datenbankoperationen)
# ============================================================================

class LeadStatusManager:
    """Verwaltet alle Operationen für die Lead-Status-Ansicht"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def get_my_created_leads(self, erfasser_id: int):
        """Gibt alle Leads zurück, die dieser Benutzer erfasst hat"""
        sql = """
            SELECT 
                l.*,
                f.name as kunde_name,
                p.produkt as produkt_name,
                s.status as status_name,
                CONCAT(b.vorname, ' ', b.nachname) as bearbeiter_name
            FROM lead l
            LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
            LEFT JOIN firma f ON ap.firma_id = f.id
            LEFT JOIN produkte p ON l.produkt_id = p.produkt_id
            LEFT JOIN status s ON l.status_id = s.id
            LEFT JOIN benutzer b ON l.bearbeiter_id = b.benutzer_id
            WHERE l.erfasser_id = ?
            ORDER BY l.datum_erfasst DESC
        """
        results = self.db.fetch_all(sql, (erfasser_id,))
        return [Lead(row) for row in results] if results else []
    
    def get_lead_by_id(self, lead_id: int):
        """Gibt einen einzelnen Lead mit allen Details zurück"""
        sql = """
            SELECT 
                l.*,
                CONCAT(b_erfasser.vorname, ' ', b_erfasser.nachname) as erfasser_name,
                CONCAT(b_bearbeiter.vorname, ' ', b_bearbeiter.nachname) as bearbeiter_name,
                f.name as kunde_name,
                CONCAT(ap.vorname, ' ', ap.nachname) as ansprechpartner_name,
                ap.email as kunde_email,
                ap.telefon as kunde_telefon,
                pos.bezeichnung as ansprechpartner_position,
                p.produkt as produkt_name,
                pg.produkt as produktgruppe_name,
                s.status as status_name,
                pz.zustand as produktzustand_name,
                q.quelle as quelle_name
            FROM lead l
            LEFT JOIN benutzer b_erfasser ON l.erfasser_id = b_erfasser.benutzer_id
            LEFT JOIN benutzer b_bearbeiter ON l.bearbeiter_id = b_bearbeiter.benutzer_id
            LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
            LEFT JOIN firma f ON ap.firma_id = f.id
            LEFT JOIN position pos ON ap.position_id = pos.id
            LEFT JOIN produkte p ON l.produkt_id = p.produkt_id
            LEFT JOIN produktgruppe pg ON l.produktgruppe_id = pg.produkt_id
            LEFT JOIN status s ON l.status_id = s.id
            LEFT JOIN produktzustand pz ON l.produktzustand_id = pz.id
            LEFT JOIN quelle q ON l.quelle_id = q.id_quelle
            WHERE l.lead_id = ?
        """
        return self.db.fetch_one(sql, (lead_id,))
    
    def get_lead_aktionen(self, lead_id: int):
        """Gibt alle Aktionen zu einem Lead zurück (Verlauf)"""
        sql = """
            SELECT 
                a.*,
                CONCAT(b.vorname, ' ', b.nachname) as benutzer_name,
                CONCAT(z.vorname, ' ', z.nachname) as ziel_name
            FROM lead_aktionen a
            LEFT JOIN benutzer b ON a.benutzer_id = b.benutzer_id
            LEFT JOIN benutzer z ON a.ziel_benutzer_id = z.benutzer_id
            WHERE a.lead_id = ?
            AND a.aktion_typ != 'lead_angesehen'
            ORDER BY a.zeitstempel DESC
        """
        return self.db.fetch_all(sql, (lead_id,))
    
    def get_lead_kommentare(self, lead_id: int):
        """Gibt alle Kommentare zu einem Lead zurück"""
        sql = """
            SELECT *
            FROM kommentar
            WHERE lead_id = ?
            ORDER BY Datum ASC
        """
        return self.db.fetch_all(sql, (lead_id,))
    
    def update_kommentar(self, kommentar_id: int, new_text: str):
        """Aktualisiert den Text eines existierenden Kommentars"""
        sql = """
            UPDATE kommentar
            SET text = ?, Datum = NOW()
            WHERE kommentar_id = ?
        """
        return self.db.query(sql, (new_text, kommentar_id))
    
    def has_recent_action(self, lead_id: int, erfasser_id: int = None):
        """Prüft ob ein Lead innerhalb der letzten 24 Stunden eine (ungesehene) Aktion erhalten hat"""
        if erfasser_id:
            # Hole Zeitstempel der letzten "lead_angesehen" Aktion für diesen Benutzer
            sql_last_viewed = """
                SELECT MAX(zeitstempel) as last_viewed
                FROM lead_aktionen
                WHERE lead_id = ?
                AND benutzer_id = ?
                AND aktion_typ = 'lead_angesehen'
            """
            viewed_result = self.db.fetch_one(sql_last_viewed, (lead_id, erfasser_id))
            last_viewed = viewed_result.get('last_viewed') if viewed_result else None
            
            # Prüfe ob es Aktionen gibt, die nach dem letzten Ansehen passiert sind
            if last_viewed:
                sql = """
                    SELECT COUNT(*) as count
                    FROM lead_aktionen
                    WHERE lead_id = ?
                    AND zeitstempel > ?
                    AND zeitstempel >= NOW() - INTERVAL 24 HOUR
                    AND aktion_typ NOT IN ('zum Löschen vorgemerkt', 'lead_angesehen')
                """
                result = self.db.fetch_one(sql, (lead_id, last_viewed))
            else:
                # Wenn noch nie angesehen, zeige alle Aktionen der letzten 24h
                sql = """
                    SELECT COUNT(*) as count
                    FROM lead_aktionen
                    WHERE lead_id = ?
                    AND zeitstempel >= NOW() - INTERVAL 24 HOUR
                    AND aktion_typ NOT IN ('zum Löschen vorgemerkt', 'lead_angesehen')
                """
                result = self.db.fetch_one(sql, (lead_id,))
        else:
            # Fallback ohne Erfasser-Prüfung
            sql = """
                SELECT COUNT(*) as count
                FROM lead_aktionen
                WHERE lead_id = ?
                AND zeitstempel >= NOW() - INTERVAL 24 HOUR
                AND aktion_typ NOT IN ('zum Löschen vorgemerkt', 'lead_angesehen')
            """
            result = self.db.fetch_one(sql, (lead_id,))
        return result['count'] > 0 if result else False
    
    def mark_lead_as_viewed(self, lead_id: int, benutzer_id: int):
        """Markiert einen Lead als angesehen durch den Erfasser"""
        # Lösche vorherige "lead_angesehen" Einträge dieses Benutzers für diesen Lead
        sql_delete = """
            DELETE FROM lead_aktionen 
            WHERE lead_id = ? 
            AND benutzer_id = ? 
            AND aktion_typ = 'lead_angesehen'
        """
        self.db.query(sql_delete, (lead_id, benutzer_id))
        
        # Füge neuen "lead_angesehen" Eintrag hinzu
        sql_insert = """
            INSERT INTO lead_aktionen (lead_id, benutzer_id, aktion_typ, kommentar)
            VALUES (?, ?, 'lead_angesehen', NULL)
        """
        self.db.query(sql_insert, (lead_id, benutzer_id))
    
    def get_last_action_type(self, lead_id: int):
        """Gibt den Typ der letzten Aktion für einen Lead zurück"""
        sql = """
            SELECT aktion_typ
            FROM lead_aktionen
            WHERE lead_id = ?
            ORDER BY zeitstempel DESC
            LIMIT 1
        """
        result = self.db.fetch_one(sql, (lead_id,))
        return result['aktion_typ'] if result else None
    
    def mark_lead_for_deletion(self, lead_id: int, benutzer_id: int, kommentar: str = None):
        """Markiert einen Lead zum Löschen (nur für Erfasser und nur offene Leads)"""
        # Prüfe ob Lead dem Benutzer gehört und Status = Offen ist
        sql_check = """
            SELECT erfasser_id, status_id
            FROM lead
            WHERE lead_id = ?
        """
        lead_data = self.db.fetch_one(sql_check, (lead_id,))
        
        if not lead_data:
            return False, "Lead nicht gefunden"
        
        if lead_data['erfasser_id'] != benutzer_id:
            return False, "Sie können nur Ihre eigenen Leads vormerken"
        
        if lead_data['status_id'] != 1:  # 1 = Offen
            return False, "Nur offene Leads können vorgemerkt werden"
        
        # Prüfe ob Lead bereits vorgemerkt ist
        sql_already_marked = """
            SELECT COUNT(*) as count
            FROM lead_aktionen
            WHERE lead_id = ? AND aktion_typ = 'zum Löschen vorgemerkt'
        """
        result = self.db.fetch_one(sql_already_marked, (lead_id,))
        if result and result['count'] > 0:
            return False, "Lead ist bereits zum Löschen vorgemerkt"
        
        # Markierung in lead_aktionen speichern
        sql_insert = """
            INSERT INTO lead_aktionen (lead_id, benutzer_id, aktion_typ, kommentar)
            VALUES (?, ?, 'zum Löschen vorgemerkt', ?)
        """
        self.db.query(sql_insert, (lead_id, benutzer_id, kommentar))
        return True, "Lead wurde erfolgreich zum Löschen vorgemerkt"
    
    def is_lead_marked_for_deletion(self, lead_id: int):
        """Prüft ob ein Lead bereits zum Löschen vorgemerkt ist"""
        sql = """
            SELECT COUNT(*) as count
            FROM lead_aktionen
            WHERE lead_id = ? AND aktion_typ = 'zum Löschen vorgemerkt'
        """
        result = self.db.fetch_one(sql, (lead_id,))
        return result['count'] > 0 if result else False
    
    def get_count_marked_for_deletion(self):
        """Gibt die Anzahl aller zum Löschen vorgemerkten Leads zurück"""
        sql = """
            SELECT COUNT(DISTINCT lead_id) as count
            FROM lead_aktionen
            WHERE aktion_typ = 'zum Löschen vorgemerkt'
        """
        result = self.db.fetch_one(sql, ())
        return result['count'] if result else 0
