from backend.database import Database


# ============================================================================
# MODEL-KLASSEN (Daten-Objekte)
# ============================================================================

class Lead:
    """Repräsentiert einen Lead mit allen Details"""
    
    def __init__(self, data: dict):
        """Erstellt Lead-Objekt aus Datenbank-Dictionary"""
        self.lead_id = data.get('lead_id')
        self.datum_erfasst = data.get('datum_erfasst')
        self.produktgruppe_id = data.get('produktgruppe_id')
        self.produkt_id = data.get('produkt_id')
        self.produktzustand_id = data.get('produktzustand_id')
        self.status_id = data.get('status_id')
        self.quelle_id = data.get('quelle_id')
        self.ansprechpartner_id = data.get('ansprechpartner_id')
        self.erfasser_id = data.get('erfasser_id')
        self.bearbeiter_id = data.get('bearbeiter_id')
        self.bild_id = data.get('bild_id')
        
        # Zusätzliche Infos (aus JOINs)
        self.erfasser_name = data.get('erfasser_name', 'Unbekannt')
        self.kunde_name = data.get('kunde_name', 'Unbekannt')
        self.produkt_name = data.get('produkt_name', 'Unbekannt')
        self.produktgruppe_name = data.get('produktgruppe_name', 'Unbekannt')
        self.produktzustand_name = data.get('produktzustand_name', 'Unbekannt')
        self.status_name = data.get('status_name', 'Offen')
        self.ansprechpartner_name = data.get('ansprechpartner_name', '')
        self.ansprechpartner_position = data.get('ansprechpartner_position', '')
        self.kunde_email = data.get('kunde_email', '')
        self.kunde_telefon = data.get('kunde_telefon', '')
    
    def __str__(self):
        return f"Lead #{self.lead_id} - {self.kunde_name} ({self.status_name})"


class LeadAktion:
    """Repräsentiert eine Aktion (Weiterleitung, Ablehnung, etc.)"""
    
    def __init__(self, data: dict):
        self.aktion_id = data.get('aktion_id')
        self.lead_id = data.get('lead_id')
        self.benutzer_id = data.get('benutzer_id')
        self.aktion_typ = data.get('aktion_typ')
        self.ziel_benutzer_id = data.get('ziel_benutzer_id')
        self.kommentar = data.get('kommentar', '')
        self.zeitstempel = data.get('zeitstempel')
        
        # Zusätzliche Infos
        self.benutzer_name = data.get('benutzer_name', 'Unbekannt')
        self.ziel_name = data.get('ziel_name', '')


class LeadKommentar:
    """Repräsentiert einen Kommentar zu einem Lead"""
    
    def __init__(self, data: dict):
        self.kommentar_id = data.get('kommentar_id')
        self.lead_id = data.get('lead_id')
        self.datum = data.get('Datum')  # Großes D wie in DB
        self.text = data.get('text', '')


# ============================================================================
# MANAGER-KLASSE (Business-Logik / Datenbankoperationen)
# ============================================================================

class LeadBearbeitungManager:
    """Verwaltet alle Operationen für die Lead-Bearbeitung"""
    
    def __init__(self, db: Database):
        self.db = db
    
    # ---- Lead-Abfragen ----
    
    def get_my_leads(self, bearbeiter_id: int):
        """Gibt alle Leads zurück, die diesem Bearbeiter zugewiesen sind"""
        sql = """
            SELECT 
                l.*,
                CONCAT(b.vorname, ' ', b.nachname) as erfasser_name,
                f.name as kunde_name,
                p.produkt as produkt_name,
                s.status as status_name
            FROM lead l
            LEFT JOIN benutzer b ON l.erfasser_id = b.benutzer_id
            LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
            LEFT JOIN firma f ON ap.firma_id = f.id
            LEFT JOIN produkte p ON l.produkt_id = p.produkt_id
            LEFT JOIN status s ON l.status_id = s.id
            WHERE l.bearbeiter_id = ?
            ORDER BY l.datum_erfasst DESC
        """
        results = self.db.fetch_all(sql, (bearbeiter_id,))
        return [Lead(row) for row in results] if results else []
    
    def get_lead_by_id(self, lead_id: int):
        """Gibt einen einzelnen Lead mit allen Details zurück"""
        sql = """
            SELECT 
                l.*,
                CONCAT(b.vorname, ' ', b.nachname) as erfasser_name,
                f.name as kunde_name,
                CONCAT(ap.vorname, ' ', ap.nachname) as ansprechpartner_name,
                ap.email as kunde_email,
                ap.telefon as kunde_telefon,
                pos.bezeichnung as ansprechpartner_position,
                p.produkt as produkt_name,
                pg.produkt as produktgruppe_name,
                s.status as status_name,
                pz.zustand as produktzustand_name
            FROM lead l
            LEFT JOIN benutzer b ON l.erfasser_id = b.benutzer_id
            LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
            LEFT JOIN firma f ON ap.firma_id = f.id
            LEFT JOIN position pos ON ap.position_id = pos.id
            LEFT JOIN produkte p ON l.produkt_id = p.produkt_id
            LEFT JOIN produktgruppe pg ON l.produktgruppe_id = pg.produkt_id
            LEFT JOIN status s ON l.status_id = s.id
            LEFT JOIN produktzustand pz ON l.produktzustand_id = pz.id
            WHERE l.lead_id = ?
        """
        result = self.db.fetch_one(sql, (lead_id,))
        return Lead(result) if result else None
    
    # ---- Status-Änderungen ----
    
    def accept_lead(self, lead_id: int, bearbeiter_id: int):
        """Lead annehmen - Status auf 'in Bearbeitung' setzen"""
        sql = "UPDATE lead SET status_id = 2 WHERE lead_id = ?"
        result = self.db.query(sql, (lead_id,))
        
        if result:
            # Aktion loggen
            self.log_aktion(lead_id, bearbeiter_id, 'angenommen', None, 'Lead angenommen')
            return True
        return False
    
    def accept_lead_with_comment(self, lead_id: int, bearbeiter_id: int, kommentar: str):
        """Lead mit Kommentar annehmen - Status auf 'in Bearbeitung' setzen und Kommentar speichern"""
        # Erst Lead als angenommen setzen
        success = self.accept_lead(lead_id, bearbeiter_id)
        
        if success:
            # Dann Kommentar hinzufügen
            self.add_kommentar(lead_id, kommentar)
            return True
        return False
    
    def reject_lead(self, lead_id: int, bearbeiter_id: int, kommentar: str):
        """Lead ablehnen - Status auf 'abgelehnt' setzen"""
        sql = "UPDATE lead SET status_id = 4 WHERE lead_id = ?"
        result = self.db.query(sql, (lead_id,))
        
        if result:
            # Aktion loggen
            self.log_aktion(lead_id, bearbeiter_id, 'abgelehnt', None, kommentar)
            return True
        return False
    
    def complete_lead(self, lead_id: int, bearbeiter_id: int):
        """Lead als erledigt markieren - Status auf 'erledigt' (3) setzen"""
        sql = "UPDATE lead SET status_id = 3 WHERE lead_id = ?"
        result = self.db.query(sql, (lead_id,))
        
        if result:
            # Aktion loggen
            self.log_aktion(lead_id, bearbeiter_id, 'erledigt', None, 'Lead erledigt')
            return True
        return False
    
    # ---- Weiterleitung ----
    
    def forward_lead(self, lead_id: int, von_benutzer_id: int, zu_benutzer_id: int, kommentar: str):
        """Lead an anderen Bearbeiter weiterleiten - Status bleibt auf 'Offen'"""
        sql = "UPDATE lead SET bearbeiter_id = ?, status_id = 1 WHERE lead_id = ?"
        result = self.db.query(sql, (zu_benutzer_id, lead_id))
        
        if result:
            # Aktion loggen - 'zugewiesen' statt 'weitergeleitet'
            self.log_aktion(lead_id, von_benutzer_id, 'zugewiesen', zu_benutzer_id, kommentar)
            return True
        return False
    
    def get_verfuegbare_bearbeiter(self):
        """Gibt alle Innendienst-Mitarbeiter zurück (für Weiterleitung)"""
        sql = """
            SELECT benutzer_id, CONCAT(vorname, ' ', nachname) as name, email
            FROM benutzer 
            WHERE rolle_id = 2 AND is_approved = 1
            ORDER BY vorname, nachname
        """
        return self.db.fetch_all(sql)
    
    # ---- Aktionen & Verlauf ----
    
    def log_aktion(self, lead_id: int, benutzer_id: int, aktion_typ: str, 
                   ziel_benutzer_id: int = None, kommentar: str = ''):
        """Loggt eine Aktion in die Datenbank"""
        sql = """
            INSERT INTO lead_aktionen 
            (lead_id, benutzer_id, aktion_typ, ziel_benutzer_id, kommentar, zeitstempel)
            VALUES (?, ?, ?, ?, ?, NOW())
        """
        return self.db.query(sql, (lead_id, benutzer_id, aktion_typ, 
                                   ziel_benutzer_id, kommentar))
    
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
            ORDER BY a.zeitstempel DESC
        """
        results = self.db.fetch_all(sql, (lead_id,))
        return [LeadAktion(row) for row in results] if results else []
    
    # ---- Kommentare ----
    
    def add_kommentar(self, lead_id: int, text: str):
        """Fügt einen Kommentar zu einem Lead hinzu (ohne benutzer_id)"""
        sql = """
            INSERT INTO kommentar (lead_id, Datum, text)
            VALUES (?, NOW(), ?)
        """
        return self.db.query(sql, (lead_id, text))
    
    def get_lead_kommentare(self, lead_id: int):
        """Gibt alle Kommentare zu einem Lead zurück"""
        sql = """
            SELECT *
            FROM kommentar
            WHERE lead_id = ?
            ORDER BY Datum ASC
        """
        results = self.db.fetch_all(sql, (lead_id,))
        return [LeadKommentar(row) for row in results] if results else []
    
    # ---- Neue Lead Benachrichtigungen ----
    
    def get_neue_leads(self, bearbeiter_id: int):
        """
        Gibt alle neuen Leads zurück, die diesem Bearbeiter kürzlich zugewiesen wurden
        (Leads mit status_id = 1 'Offen' seit der letzten Prüfung)
        """
        sql = """
            SELECT 
                l.*,
                CONCAT(b.vorname, ' ', b.nachname) as erfasser_name,
                f.name as kunde_name,
                p.produkt as produkt_name,
                s.status as status_name,
                CONCAT(ap.vorname, ' ', ap.nachname) as ansprechpartner_name
            FROM lead l
            LEFT JOIN benutzer b ON l.erfasser_id = b.benutzer_id
            LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
            LEFT JOIN firma f ON ap.firma_id = f.id
            LEFT JOIN produkte p ON l.produkt_id = p.produkt_id
            LEFT JOIN status s ON l.status_id = s.id
            WHERE l.bearbeiter_id = ? 
            AND l.status_id = 1
            AND l.datum_erfasst >= NOW() - INTERVAL 24 HOUR
            ORDER BY l.datum_erfasst DESC
        """
        results = self.db.fetch_all(sql, (bearbeiter_id,))
        return [Lead(row) for row in results] if results else []
    
    def count_neue_leads(self, bearbeiter_id: int):
        """Zählt die Anzahl neuer, offener Leads für einen Bearbeiter"""
        sql = """
            SELECT COUNT(*) as anzahl
            FROM lead
            WHERE bearbeiter_id = ? 
            AND status_id = 1
            AND datum_erfasst >= NOW() - INTERVAL 24 HOUR
        """
        result = self.db.fetch_one(sql, (bearbeiter_id,))
        return result['anzahl'] if result else 0
    
    # ---- Angebot erstellen ----
    
    def create_angebot(self, lead_id: int, bearbeiter_id: int):
        """Lead auf 'Angebot erstellt' (5) setzen mit Aktion und Kommentar"""
        sql = "UPDATE lead SET status_id = 5 WHERE lead_id = ?"
        result = self.db.query(sql, (lead_id,))
        
        if result:
            # Aktion loggen
            self.log_aktion(
                lead_id,
                bearbeiter_id,
                'Angebot erstellt',
                None,
                'Angebot erstellt'
            )
            # Kommentar hinzufügen
            self.add_kommentar(lead_id, "Angebot erstellt")
            return True
        return False