import flet as ft
from datetime import datetime
from database import Database


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
        self.status_name = data.get('status_name', 'Offen')
        self.ansprechpartner_name = data.get('ansprechpartner_name', '')
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
                p.produkt as produkt_name,
                pg.produkt as produktgruppe_name,
                s.status as status_name,
                pz.zustand as produktzustand_name
            FROM lead l
            LEFT JOIN benutzer b ON l.erfasser_id = b.benutzer_id
            LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
            LEFT JOIN firma f ON ap.firma_id = f.id
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


# ============================================================================
# VIEW-KLASSEN (User Interface)
# ============================================================================

class LeadBearbeitungView:
    """Hauptansicht: Liste aller zugewiesenen Leads"""
    
    def __init__(self, page: ft.Page, lead_manager: LeadBearbeitungManager, current_user: dict):
        self.page = page
        self.lead_manager = lead_manager
        self.current_user = current_user
        self.leads = []
        self.app_controller = None  # Wird von AppController gesetzt
        self.active_filters = [1] # Standardmäßig nur "Offen" anzeigen
        self.filters_initialized = False  # Track ob Filter bereits gesetzt wurden
    
    def render(self):
        """Zeigt die Lead-Liste"""
        self.page.clean()
        self.leads = self.lead_manager.get_my_leads(self.current_user['benutzer_id'])
    

        
        # Filter die Leads basierend auf aktiven Filtern
        filtered_leads = [lead for lead in self.leads if lead.status_id in self.active_filters]

        
        # Header
        header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self._go_back_to_menu()
            ),
            ft.Text(f"Meine Nachrichten ({len(filtered_leads)})", size=24, weight=ft.FontWeight.BOLD),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Aktualisieren",
                on_click=lambda e: self.render()
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Filter-Dropdown
        filter_dropdown = self._build_filter_dropdown()
        
        # Lead-Liste
        if not filtered_leads:
            lead_liste = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=64, color="grey"),
                    ft.Text("Keine Leads gefunden", color="grey"),
                    ft.Text("Ändere die Filter-Einstellungen", size=12, color="grey")
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40
            )
        else:
            lead_cards = []
            for lead in filtered_leads:
                card = self._create_lead_card(lead)
                lead_cards.append(card)
            
            lead_liste = ft.Column(lead_cards, spacing=10, scroll=ft.ScrollMode.AUTO)
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    header,
                    ft.Divider(),
                    filter_dropdown,
                    ft.Divider(height=10, color="transparent"),
                    lead_liste
                ], scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True
            )
        )
    
    def _go_back_to_menu(self):
        """Kehrt zum Hauptmenü zurück"""
        if self.app_controller:
            self.app_controller.show_main_app()
    
    def _build_filter_dropdown(self):
        """Erstellt ein Dropdown-Menü für Status-Filter"""
        def on_filter_change(e):
            selected_value = filter_dropdown.value

            
            # Wenn "Alle anzeigen" ausgewählt, alle aktivieren
            if selected_value == "all":
                self.active_filters = [1, 2, 3, 4, 5]
                
            else:
                # Einzelnen Status filtern
                self.active_filters = [int(selected_value)]
            

            self.render()

        
        # Filter-Optionen
        filter_options = [
            ft.dropdown.Option("all", "Alle anzeigen"),
            ft.dropdown.Option("1", "Offen"),
            ft.dropdown.Option("2", "In Bearbeitung"),
            ft.dropdown.Option("4", "Abgelehnt"),
            ft.dropdown.Option("5", "Angebot erstellt"),
            ft.dropdown.Option("3", "Erledigt")
        ]
        
        # Bestimme den aktuellen Dropdown-Wert basierend auf active_filters
        if len(self.active_filters) == 5:
            current_value = "all"
        elif len(self.active_filters) == 1:
            current_value = str(self.active_filters[0])
        else:
            current_value = "1"  # Fallback

        
        filter_dropdown = ft.Dropdown(
            label="Filter nach Status",
            options=filter_options,
            value=current_value,
            on_change=on_filter_change,
            width=250
        )
        
        return ft.Row([filter_dropdown], spacing=10)
    
    def _create_lead_card(self, lead: Lead):
        """Erstellt eine Card für einen Lead"""
        # Status-Farben für Hintergrund
        status_colors = {
            1: ft.Colors.GREEN,          # Offen - grün
            2: ft.Colors.ORANGE,         # In Bearbeitung - orange
            4: ft.Colors.RED,            # Abgelehnt - rot
            5: ft.Colors.BLUE_400,       # Angebot erstellt - blau
            3: ft.Colors.GREY_700        # Erledigt - dunkelgrau
        }
        
        bg_color = status_colors.get(lead.status_id, ft.Colors.GREY)
        
        # Status-Text mit farbigem Hintergrund
        status_badge = ft.Container(
            content=ft.Text(lead.status_name, size=12, color="white", weight=ft.FontWeight.BOLD),
            bgcolor=bg_color,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=4
        )
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.ASSIGNMENT),
                        title=ft.Text(f"Lead #{lead.lead_id} - {lead.kunde_name}"),
                        subtitle=ft.Row([
                            ft.Text(f"{lead.produkt_name}"),
                            ft.Text("| Status:"),
                            status_badge
                        ], spacing=5),
                        trailing=ft.IconButton(
                            icon=ft.Icons.ARROW_FORWARD,
                            tooltip="Details",
                            on_click=lambda e, l=lead: self._show_details(l)
                        )
                    ),
                    ft.Row([
                        ft.Text(f"Erfasst von: {lead.erfasser_name}", size=12, color="grey"),
                        ft.Text(f"Datum: {lead.datum_erfasst}", size=12, color="grey")
                    ], spacing=20)
                ]),
                padding=10
            )
        )
    
    def _show_details(self, lead: Lead):
        """Öffnet die Detail-Ansicht für einen Lead"""
        detail_view = LeadDetailView(self.page, self.lead_manager, self.current_user, lead)
        detail_view.app_controller = self.app_controller  # Controller weitergeben
        detail_view.render()


class LeadDetailView:
    """Detailansicht eines einzelnen Leads mit allen Aktionen"""
    
    def __init__(self, page: ft.Page, lead_manager: LeadBearbeitungManager, 
                 current_user: dict, lead: Lead):
        self.page = page
        self.lead_manager = lead_manager
        self.current_user = current_user
        self.lead = lead
        self.aktionen = []
        self.kommentare = []
        self.app_controller = None  # Wird von LeadBearbeitungView gesetzt
    
    def render(self):
        """Zeigt die Lead-Details"""
        self.page.clean()
        
        # Aktualisierte Daten laden
        self.lead = self.lead_manager.get_lead_by_id(self.lead.lead_id)
        self.aktionen = self.lead_manager.get_lead_aktionen(self.lead.lead_id)
        self.kommentare = self.lead_manager.get_lead_kommentare(self.lead.lead_id)
        
        # Header mit Zurück-Button
        header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Zurück zur Liste",
                on_click=lambda e: self._go_back()
            ),
            ft.Text(f"Lead #{self.lead.lead_id}", size=24, weight=ft.FontWeight.BOLD),
        ])
        
        # Lead-Informationen
        info_section = self._build_info_section()
        
        # Action-Buttons
        action_buttons = self._build_action_buttons()
        
        # Verlauf / Aktionen
        verlauf_section = self._build_verlauf_section()
        
        # Kommentare
        kommentar_section = self._build_kommentar_section()
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    header,
                    ft.Divider(),
                    info_section,
                    ft.Divider(),
                    action_buttons,
                    ft.Divider(),
                    verlauf_section,
                    ft.Divider(),
                    kommentar_section
                ], scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True
            )
        )
    
    def _build_info_section(self):
        """Lead-Informationen"""
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Lead-Informationen", size=18, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Firma: {self.lead.kunde_name}"),
                    ft.Text(f"Ansprechpartner: {self.lead.ansprechpartner_name}"),
                    ft.Text(f"E-Mail: {self.lead.kunde_email}"),
                    ft.Text(f"Telefon: {self.lead.kunde_telefon}"),
                    ft.Divider(height=10),
                    ft.Text(f"Produkt: {self.lead.produkt_name}"),
                    ft.Text(f"Status: {self.lead.status_name}"),
                    ft.Text(f"Erfasst von: {self.lead.erfasser_name}"),
                    ft.Text(f"Datum: {self.lead.datum_erfasst}"),
                ]),
                padding=15
            )
        )
    
    def _build_action_buttons(self):
        """Action-Buttons (Annehmen, Ablehnen, Weiterleiten, Lead erledigt)"""
        # Wenn Status "Offen" (1) - zeige Annehmen/Ablehnen/Weiterleiten
        if self.lead.status_id == 1:
            return ft.Row([
                ft.ElevatedButton(
                    "Annehmen",
                    icon=ft.Icons.CHECK_CIRCLE,
                    on_click=lambda e: self._handle_accept(),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE
                ),
                ft.ElevatedButton(
                    "Ablehnen",
                    icon=ft.Icons.CANCEL,
                    on_click=lambda e: self._handle_reject(),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE
                ),
                ft.ElevatedButton(
                    "Weiterleiten",
                    icon=ft.Icons.FORWARD,
                    on_click=lambda e: self._handle_forward(),
                    color=ft.Colors.WHITE
                )
            ], wrap=True, spacing=10)
        
        # Wenn Status "In Bearbeitung" (2) - zeige Lead erledigt Button
        elif self.lead.status_id == 2:
            return ft.Row([
                ft.ElevatedButton(
                    "Lead erledigt",
                    icon=ft.Icons.CHECK_CIRCLE,
                    on_click=lambda e: self._handle_complete(),
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE
                )
            ], wrap=True, spacing=10)
        
        # Für alle anderen Status - keine Aktionen verfügbar
        return ft.Container(
            content=ft.Text("Keine Aktionen verfügbar", color="grey", size=12),
            padding=10
        )
    
    def _build_verlauf_section(self):
        """Zeigt den Aktionsverlauf"""
        if not self.aktionen:
            return ft.Column([
                ft.Text("Verlauf", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("Noch keine Aktionen", color="grey")
            ])
        
        verlauf_items = []
        for aktion in self.aktionen:
            # Aktion-Typ für Anzeige anpassen
            typ_anzeige = aktion.aktion_typ
            if aktion.aktion_typ == 'zugewiesen':
                typ_anzeige = 'weitergeleitet'
            
            verlauf_items.append(
                ft.ListTile(
                    leading=ft.Icon(self._get_aktion_icon(aktion.aktion_typ)),
                    title=ft.Text(f"{typ_anzeige.capitalize()} von {aktion.benutzer_name}"),
                    subtitle=ft.Text(f"{aktion.kommentar}\n{aktion.zeitstempel}", size=12)
                )
            )
        
        return ft.Column([
            ft.Text("Verlauf", size=18, weight=ft.FontWeight.BOLD),
            ft.Column(verlauf_items)
        ])
    
    def _build_kommentar_section(self):
        """Kommentar-Bereich (ohne Benutzer-Zuordnung)"""
        kommentar_field = ft.TextField(
            label="Neuer Kommentar",
            multiline=True,
            min_lines=2,
            max_lines=4
        )
        
        def add_kommentar(e):
            if kommentar_field.value and kommentar_field.value.strip():
                success = self.lead_manager.add_kommentar(
                    self.lead.lead_id,
                    kommentar_field.value
                )
                if success:
                    kommentar_field.value = ""
                    self.render()  # Neu laden
        
        kommentar_liste = []
        for k in self.kommentare:
            kommentar_liste.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text(k.text, weight=ft.FontWeight.BOLD),
                            ft.Text(str(k.datum), size=10, color="grey")
                        ]),
                        padding=10
                    )
                )
            )
        
        return ft.Column([
            ft.Text("Kommentare", size=18, weight=ft.FontWeight.BOLD),
            ft.Column(kommentar_liste) if kommentar_liste else ft.Text("Keine Kommentare", color="grey"),
            kommentar_field,
            ft.ElevatedButton("Kommentar hinzufügen", on_click=add_kommentar)
        ])
    
    # ---- Action Handlers ----
    
    def _handle_accept(self):
        """Lead annehmen - Menü mit Optionen anzeigen"""
        def on_accept_with_comment(e):
            """Öffnet Dialog für "Mit Kommentar annehmen" Option"""
            self.page.close(dialog)
            
            def submit_accept_comment(e):
                kommentar = kommentar_field.value or ""
                if not kommentar:
                    error_text.value = "Bitte geben Sie einen Kommentar ein."
                    self.page.update()
                    return
                
                # Lead auf "In Bearbeitung" (2) setzen und Kommentar hinzufügen
                success = self.lead_manager.accept_lead_with_comment(
                    self.lead.lead_id,
                    self.current_user['benutzer_id'],
                    kommentar
                )
                if success:
                    self.page.close(comment_dialog)
                    self.render()
            
            kommentar_field = ft.TextField(
                label="Kommentar",
                multiline=True,
                min_lines=4,
                width=300
            )
            error_text = ft.Text("", color="red", size=12)
            
            comment_dialog = ft.AlertDialog(
                title=ft.Text("Lead mit Kommentar annehmen"),
                content=ft.Column([
                    ft.Text("Geben Sie einen Kommentar ein:", size=12),
                    kommentar_field,
                    error_text
                ], spacing=5, tight=True),
                actions=[
                    ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(comment_dialog)),
                    ft.TextButton("Annehmen", on_click=submit_accept_comment)
                ]
            )
            
            self.page.open(comment_dialog)
        
        def on_besuchsbericht(e):
            """Öffnet Dialog für "Besuchsbericht erstellen" Option"""
            self.page.close(dialog)
            self._show_besuchsbericht_dialog()
        
        def on_option_click(option_type):
            def handler(e):
                if option_type == "comment":
                    on_accept_with_comment(e)
                elif option_type == "report":
                    on_besuchsbericht(e)
                else:
                    # TODO: Implementiere Funktionalität für:
                    # - "offer": Angebot erstellen
                    self.page.close(dialog)
            return handler
        
        dialog = ft.AlertDialog(
            title=ft.Text("Lead annehmen - Was möchtest du tun?"),
            content=ft.Column([
                ft.ElevatedButton(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DESCRIPTION, size=32),
                        ft.Text("Angebot erstellen", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Erstelle ein Angebot für diesen Lead", size=11, color="grey")
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=280,
                    height=100,
                    on_click=on_option_click("offer")
                ),
                ft.ElevatedButton(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DOCUMENT_SCANNER, size=32),
                        ft.Text("Besuchsbericht erstellen", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Dokumentiere deinen Kontakt", size=11, color="grey")
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=280,
                    height=100,
                    on_click=on_option_click("report")
                ),
                ft.ElevatedButton(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=32),
                        ft.Text("Mit Kommentar annehmen", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Nimm den Lead mit Notiz an", size=11, color="grey")
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=280,
                    height=100,
                    on_click=on_option_click("comment")
                )
            ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(dialog))
            ]
        )
        
        self.page.open(dialog)
    
    def _handle_reject(self):
        """Lead ablehnen - mit Kommentar"""
        def submit_reject(e):
            kommentar = kommentar_field.value or "Kein Grund angegeben"
            success = self.lead_manager.reject_lead(
                self.lead.lead_id,
                self.current_user['benutzer_id'],
                kommentar
            )
            if success:
                self.page.close(dialog)
                self.render()
        
        kommentar_field = ft.TextField(label="Grund für Ablehnung", multiline=True)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Lead ablehnen"),
            content=kommentar_field,
            actions=[
                ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Ablehnen", on_click=submit_reject)
            ]
        )
        
        self.page.open(dialog)
    
    def _handle_complete(self):
        """Lead als erledigt markieren - mit Kommentar"""
        def submit_complete(e):
            kommentar = kommentar_field.value or ""
            if not kommentar:
                error_text.value = "Bitte geben Sie ein, was gemacht wurde."
                self.page.update()
                return
            
            # Lead auf erledigt setzen und Kommentar hinzufügen
            success = self.lead_manager.complete_lead(
                self.lead.lead_id,
                self.current_user['benutzer_id']
            )
            if success:
                # Kommentar hinzufügen
                self.lead_manager.add_kommentar(
                    self.lead.lead_id,
                    kommentar
                )
                self.page.close(dialog)
                self.render()
        
        kommentar_field = ft.TextField(
            label="Was wurde gemacht?",
            multiline=True,
            min_lines=4,
            hint_text="z.B. Telefonisch Kontakt aufgenommen, Kunde hat Bedarf erstmal zurück gestellt"
        )
        error_text = ft.Text("", color="red", size=12)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Lead erledigt"),
            content=ft.Column([
                ft.Text("Bitte dokumentiere, was gemacht wurde:", size=12),
                kommentar_field,
                error_text
            ], spacing=5, tight=True),
            actions=[
                ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Erledigt", on_click=submit_complete)
            ]
        )
        
        self.page.open(dialog)
    
    def _handle_forward(self):
        """Lead weiterleiten - Bearbeiter auswählen mit Live-Suchfunktion"""
        bearbeiter = self.lead_manager.get_verfuegbare_bearbeiter()
        
        # Filtere den aktuellen Benutzer aus der Liste
        bearbeiter = [b for b in bearbeiter if b['benutzer_id'] != self.current_user['benutzer_id']]
        
        if not bearbeiter:
            # Keine anderen Bearbeiter verfügbar
            error_dialog = ft.AlertDialog(
                title=ft.Text("Keine Bearbeiter verfügbar"),
                content=ft.Text("Es sind keine anderen Innendienst-Mitarbeiter verfügbar."),
                actions=[ft.TextButton("OK", on_click=lambda e: self.page.close(error_dialog))]
            )
            self.page.open(error_dialog)
            return
        
        # State für Suchfunktion
        selected_bearbeiter = {"id": None, "name": None}
        suggestions_list = ft.Column(visible=False, scroll=ft.ScrollMode.AUTO)
        
        def filter_bearbeiter(search_text):
            """Filtert Bearbeiter basierend auf Suchtext"""
            if not search_text:
                return []
            
            search_lower = search_text.lower()
            return [b for b in bearbeiter if search_lower in b['name'].lower()]
        
        def on_search_change(e):
            """Wird aufgerufen wenn Suchtext sich ändert"""
            search_text = search_field.value
            filtered = filter_bearbeiter(search_text)
            
            # Erstelle Suggestions-Liste
            suggestions_list.controls.clear()
            
            if filtered:
                for b in filtered:
                    def create_suggestion_button(bearbeiter_data):
                        def on_select(e):
                            selected_bearbeiter["id"] = bearbeiter_data['benutzer_id']
                            selected_bearbeiter["name"] = bearbeiter_data['name']
                            search_field.value = bearbeiter_data['name']
                            suggestions_list.visible = False
                            self.page.update()
                        
                        return ft.Container(
                            content=ft.Text(bearbeiter_data['name']),
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            on_click=on_select,
                            ink=True
                        )
                    
                    suggestions_list.controls.append(create_suggestion_button(b))
                
                suggestions_list.visible = True
            else:
                suggestions_list.visible = False
            
            self.page.update()
        
        # Suchfeld mit Live-Vorschlägen
        search_field = ft.TextField(
            label="Nach Bearbeiter suchen...",
            hint_text="Name eingeben",
            on_change=on_search_change,
            on_focus=lambda e: None,
            width=300
        )
        
        kommentar_field = ft.TextField(
            label="Kommentar",
            multiline=True,
            min_lines=3,
            width=300
        )
        
        def submit_forward(e):
            if selected_bearbeiter["id"] and kommentar_field.value:
                success = self.lead_manager.forward_lead(
                    self.lead.lead_id,
                    self.current_user['benutzer_id'],
                    selected_bearbeiter["id"],
                    kommentar_field.value
                )
                if success:
                    self.page.close(dialog)
                    self._go_back()  # Zurück zur Liste
            elif not selected_bearbeiter["id"]:
                error_text.value = "Bitte wählen Sie einen Bearbeiter aus der Vorschlagsliste."
                kommentar_field.border_color = None
                self.page.update()
            elif not kommentar_field.value:
                error_text.value = "Bitte geben Sie einen Kommentar ein."
                kommentar_field.border_color = ft.Colors.RED
                self.page.update()
        
        error_text = ft.Text("", color="red", size=12)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Lead weiterleiten"),
            content=ft.Column([
                ft.Text("Bearbeiter auswählen:", size=12, weight=ft.FontWeight.BOLD),
                search_field,
                ft.Container(
                    content=suggestions_list,
                    border_radius=4,
                    height=150 if bearbeiter else 0
                ),
                ft.Text("Kommentar hinzufügen:", size=12, weight=ft.FontWeight.BOLD),
                kommentar_field,
                error_text
            ], tight=True, spacing=5),
            actions=[
                ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Weiterleiten", on_click=submit_forward)
            ]
        )
        
        self.page.open(dialog)
    
    # ---- Hilfsfunktionen ----
    
    def _show_besuchsbericht_dialog(self):
        """Zeigt Besuchsbericht-Dialog mit Kundendaten und Lead-Daten"""
        def submit_besuchsbericht(e):
            # Lead auf "erledigt" (3) setzen mit Kommentar "Besuchsbericht angelegt"
            success = self.lead_manager.complete_lead(
                self.lead.lead_id,
                self.current_user['benutzer_id']
            )
            if success:
                # Kommentar hinzufügen
                self.lead_manager.add_kommentar(
                    self.lead.lead_id,
                    "Besuchsbericht angelegt"
                )
                self.page.close(dialog)
                self.render()
        
        # Kundeninfos Section
        kundeninfos = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Kundeninfos", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Firma: {self.lead.kunde_name}"),
                    ft.Text(f"Ansprechpartner: {self.lead.ansprechpartner_name}"),
                    ft.Text(f"E-Mail: {self.lead.kunde_email}"),
                    ft.Text(f"Telefon: {self.lead.kunde_telefon}"),
                ]),
                padding=12
            )
        )
        
        # Lead-Daten Section
        leaddaten = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Lead-Daten", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Lead ID: {self.lead.lead_id}"),
                    ft.Text(f"Produkt: {self.lead.produkt_name}"),
                    ft.Text(f"Status: {self.lead.status_name}"),
                    ft.Text(f"Erfasst von: {self.lead.erfasser_name}"),
                    ft.Text(f"Datum: {self.lead.datum_erfasst}"),
                ]),
                padding=12
            )
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text("Besuchsbericht erstellen"),
            content=ft.Column([
                ft.Text("Kundendetails und Lead-Informationen:", size=12),
                kundeninfos,
                leaddaten,
                ft.Text("Der Lead wird als 'erledigt' markiert und ein Besuchsbericht wird angelegt.", 
                       size=11, color="grey", italic=True)
            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(dialog)),
                ft.TextButton("Besuchsbericht erstellen", on_click=submit_besuchsbericht)
            ]
        )
        
        self.page.open(dialog)
    
    def _get_aktion_icon(self, aktion_typ: str):
        """Gibt passendes Icon für Aktion zurück"""
        icons = {
            'angenommen': ft.Icons.CHECK_CIRCLE,
            'abgelehnt': ft.Icons.CANCEL,
            'zugewiesen': ft.Icons.FORWARD  # statt 'weitergeleitet'
        }
        return icons.get(aktion_typ, ft.Icons.INFO)
    
    def _go_back(self):
        """Zurück zur Lead-Liste - verwendet die bestehende View-Instanz"""
        if self.app_controller and self.app_controller.lead_bearbeitung_view:
            # Verwende die bestehende View-Instanz mit gespeicherten Filtern
            self.app_controller.lead_bearbeitung_view.render()
        else:
            # Fallback wenn app_controller nicht verfügbar
            liste_view = LeadBearbeitungView(self.page, self.lead_manager, self.current_user)
            liste_view.app_controller = self.app_controller
            liste_view.render()