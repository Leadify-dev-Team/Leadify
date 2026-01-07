import flet as ft
from datetime import datetime
from database import Database


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
    
    def has_recent_action(self, lead_id: int):
        """Prüft ob ein Lead innerhalb der letzten 24 Stunden eine Aktion erhalten hat"""
        sql = """
            SELECT COUNT(*) as count
            FROM lead_aktionen
            WHERE lead_id = ?
            AND zeitstempel >= NOW() - INTERVAL 24 HOUR
        """
        result = self.db.fetch_one(sql, (lead_id,))
        return result['count'] > 0 if result else False


# ============================================================================
# VIEW-KLASSE (User Interface)
# ============================================================================

class LeadStatusView:
    """Zeigt Status aller von diesem Benutzer erstellten Leads"""
    
    def __init__(self, page: ft.Page, lead_manager: LeadStatusManager, current_user: dict):
        self.page = page
        self.lead_manager = lead_manager
        self.current_user = current_user
        self.leads = []
        self.app_controller = None  # Wird von AppController gesetzt
        self.active_filters = [1]  # Standardmäßig nur "Offen" anzeigen
        self.filters_initialized = False  # Track ob Filter bereits gesetzt wurden
    
    def render(self):
        """Zeigt die Lead-Status Liste"""
        self.page.clean()
        
        # Page-Einstellungen zurücksetzen (falls von Detailansicht zurückgekehrt)
        self.page.padding = 20
        self.page.bgcolor = None
        
        self.leads = self.lead_manager.get_my_created_leads(self.current_user['benutzer_id'])
        
        # Filter die Leads basierend auf aktiven Filtern
        filtered_leads = [lead for lead in self.leads if lead.status_id in self.active_filters]
        
        # Header
        header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self._go_back_to_menu()
            ),
            ft.Text(f"Meine erstellten Leads ({len(filtered_leads)})", size=24, weight=ft.FontWeight.BOLD),
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
                    ft.Text("Es sind keine offenen Leads vorhanden", color="grey"),
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
            ft.dropdown.Option("1", "Offen"),
            ft.dropdown.Option("2", "In Bearbeitung"),
            ft.dropdown.Option("4", "Abgelehnt"),
            ft.dropdown.Option("5", "Angebot erstellt"),
            ft.dropdown.Option("3", "Erledigt"),
            ft.dropdown.Option("all", "Alle anzeigen")
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
    
    def _show_lead_details(self, lead):
        """Zeigt die Detailansicht für einen Lead"""
        # Lead-Daten als Dictionary vorbereiten
        lead_dict = {
            'lead_id': lead.lead_id,
            'datum_erfasst': lead.datum_erfasst,
            'status_id': lead.status_id,
            'status_name': lead.status_name,
            'kunde_name': lead.kunde_name,
            'produkt_name': lead.produkt_name,
            'bearbeiter_name': lead.bearbeiter_name
        }
        detail_view = LeadDetailViewStatus(self.page, self.lead_manager, lead_dict, self)
        detail_view.render()
    
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
            content=ft.Text(lead.status_name, size=12, weight=ft.FontWeight.BOLD),
            bgcolor=bg_color,
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=4
        )
        
        # Zeitstempel formatieren
        try:
            if isinstance(lead.datum_erfasst, str):
                datum_text = lead.datum_erfasst.split(' ')[0] if ' ' in lead.datum_erfasst else lead.datum_erfasst
            else:
                datum_text = str(lead.datum_erfasst)
        except:
            datum_text = "Unbekannt"
        
        # Status-Icon und Beschreibung basierend auf Status
        status_icon_map = {
            1: (ft.Icons.INBOX, "Offen - wartet auf Bearbeitung"),
            2: (ft.Icons.HISTORY, "In Bearbeitung"),
            3: (ft.Icons.CHECK_CIRCLE, "Erledigt"),
            4: (ft.Icons.CANCEL, "Abgelehnt"),
            5: (ft.Icons.DESCRIPTION, "Angebot erstellt")
        }
        
        status_icon, status_desc = status_icon_map.get(lead.status_id, (ft.Icons.HELP, "Status unbekannt"))
        
        # Prüfe ob Lead kürzlich eine Aktion erhalten hat (innerhalb 24h)
        has_update = self.lead_manager.has_recent_action(lead.lead_id)
        
        # Titel-Zeile mit optionalem "AKTUALISIERT" Badge
        title_content = ft.Row([
            ft.Text(f"Lead #{lead.lead_id} - {lead.kunde_name}"),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="white", size=16),
                    ft.Text("AKTUALISIERT", size=11, color="white", weight=ft.FontWeight.BOLD)
                ], spacing=3),
                bgcolor="orange",
                padding=ft.padding.symmetric(horizontal=6, vertical=3),
                border_radius=4,
                visible=has_update
            )
        ], spacing=10)
        
        # Card mit Hover-Effekt
        card_container = ft.Container(
            content=ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.ASSIGNMENT),
                            title=title_content,
                            subtitle=ft.Row([
                                ft.Text(f"{lead.produkt_name}"),
                                ft.Text("| Status:"),
                                status_badge
                            ], spacing=5),
                        ),
                        ft.Row([
                            ft.Icon(status_icon, color=bg_color, size=16),
                            ft.Text(status_desc, size=11, color=bg_color, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Text(f"Bearbeiter: {lead.bearbeiter_name}", size=11, color="grey")
                        ], spacing=10),
                        ft.Row([
                            ft.Text(f"Erfasst: {datum_text}", size=12, color="grey"),
                        ], spacing=20)
                    ]),
                    padding=10
                ),
                elevation=2
            ),
            on_click=lambda e, l=lead: self._show_lead_details(l),
            ink=True,
            border_radius=10,
        )
        
        return card_container


# ============================================================================
# DETAIL-VIEW FÜR LEAD STATUS (nur Anzeige, keine Aktionen)
# ============================================================================

class LeadDetailViewStatus:
    """Detailansicht eines Leads im Lead-Status (nur lesend)"""
    
    def __init__(self, page: ft.Page, manager: LeadStatusManager, lead: dict, parent_view):
        self.page = page
        self.manager = manager
        self.lead = lead
        self.parent_view = parent_view
        self.aktionen = []
        self.kommentare = []
    
    def render(self):
        """Zeigt die Lead-Details"""
        self.page.clean()
        self.page.padding = 0
        
        # Aktualisierte Daten laden
        self.lead = self.manager.get_lead_by_id(self.lead.get('lead_id'))
        self.aktionen = self.manager.get_lead_aktionen(self.lead.get('lead_id'))
        self.kommentare = self.manager.get_lead_kommentare(self.lead.get('lead_id'))
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: self._go_back(),
                    tooltip="Zurück zur Liste"
                ),
                ft.Text(f"Lead #{self.lead.get('lead_id')}", size=24, weight=ft.FontWeight.BOLD),
            ], spacing=10),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
        )
        
        # Lead-Informationen
        info_section = self._build_info_section()
        
        # Verlauf / Aktionen
        verlauf_section = self._build_verlauf_section()
        
        # Kommentare
        kommentar_section = self._build_kommentar_section()
        
        # Hauptcontainer
        main_content = ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    info_section,
                    ft.Container(height=20),
                    verlauf_section,
                    ft.Container(height=20),
                    kommentar_section,
                ], scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.symmetric(horizontal=30, vertical=20),
                expand=True,
            )
        ], spacing=0, expand=True)
        
        self.page.add(main_content)
    
    def _build_info_section(self):
        """Lead-Informationen"""
        # Datum formatieren
        datum = self.lead.get('datum_erfasst', '')
        if isinstance(datum, datetime):
            datum_str = datum.strftime("%d.%m.%Y %H:%M")
        else:
            datum_str = str(datum)
        
        # Status-Farbe
        status_colors = {
            "Offen": "#10b981",
            "In Bearbeitung": "#f59e0b",
            "Erledigt": "#64748b",
            "Abgelehnt": "#ef4444",
            "Angebot erstellt": "#3b82f6",
        }
        status_color = status_colors.get(self.lead.get('status_name', 'Offen'), "#64748b")
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Lead-Informationen", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Text(self.lead.get('status_name', 'Offen'), size=14),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=15, vertical=8),
                        border_radius=20,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#475569"),
                
                # Kundendaten
                ft.Text("Kunde & Ansprechpartner", size=16, color="#94a3b8", weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.Column([
                        ft.Text("Firma:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('kunde_name', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Ansprechpartner:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('ansprechpartner_name', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Position:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('ansprechpartner_position', '-'), size=14),
                    ], spacing=2),
                ], spacing=30, wrap=True),
                ft.Row([
                    ft.Column([
                        ft.Text("E-Mail:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('kunde_email', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Telefon:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('kunde_telefon', '-'), size=14),
                    ], spacing=2),
                ], spacing=30, wrap=True),
                
                ft.Container(height=15),
                
                # Produktdaten
                ft.Text("Produktinformationen", size=16, color="#94a3b8", weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.Column([
                        ft.Text("Produktgruppe:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('produktgruppe_name', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Produkt:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('produkt_name', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Zustand:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('produktzustand_name', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Quelle:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('quelle_name', '-'), size=14),
                    ], spacing=2),
                ], spacing=30, wrap=True),
                
                ft.Container(height=15),
                
                # Zuständigkeiten
                ft.Text("Zuständigkeiten", size=16, color="#94a3b8", weight=ft.FontWeight.W_600),
                ft.Row([
                    ft.Column([
                        ft.Text("Erfasst von:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('erfasser_name', '-'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Bearbeiter:", size=12, color="#64748b"),
                        ft.Text(self.lead.get('bearbeiter_name', 'Nicht zugewiesen'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Erfasst am:", size=12, color="#64748b"),
                        ft.Text(datum_str, size=14),
                    ], spacing=2),
                ], spacing=30, wrap=True),
            ], spacing=10),
            padding=25,
            border_radius=12,
        )
    
    def _build_verlauf_section(self):
        """Verlauf / Aktionen"""
        if not self.aktionen:
            content = ft.Text("Keine Aktionen vorhanden", size=14, color="#64748b", italic=True)
        else:
            aktion_items = []
            for aktion in self.aktionen:
                # Zeitstempel formatieren
                zeitstempel = aktion.get('zeitstempel', '')
                if isinstance(zeitstempel, datetime):
                    zeit_str = zeitstempel.strftime("%d.%m.%Y %H:%M")
                else:
                    zeit_str = str(zeitstempel)
                
                # Aktion-Text erstellen
                aktion_typ = aktion.get('aktion_typ', '')
                benutzer = aktion.get('benutzer_name', 'Unbekannt')
                ziel = aktion.get('ziel_name', '')
                kommentar = aktion.get('kommentar', '')
                
                if aktion_typ == 'zugewiesen' and ziel:
                    text = f"{benutzer} hat den Lead an {ziel} weitergeleitet"
                elif aktion_typ == 'angenommen':
                    text = f"{benutzer} hat den Lead angenommen"
                elif aktion_typ == 'abgelehnt':
                    text = f"{benutzer} hat den Lead abgelehnt"
                elif aktion_typ == 'erledigt':
                    text = f"{benutzer} hat den Lead erledigt"
                else:
                    text = f"{benutzer}: {aktion_typ}"
                
                aktion_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.HISTORY, size=16, color="#64748b"),
                                ft.Text(zeit_str, size=12, color="#64748b"),
                            ], spacing=5),
                            ft.Text(text, size=14),
                            ft.Text(kommentar, size=12, color="#94a3b8", italic=True) if kommentar else ft.Container(),
                        ], spacing=5),
                        padding=15,
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                    )
                )
            
            content = ft.Column(aktion_items, spacing=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Verlauf", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(color="#475569"),
                content,
            ], spacing=10),
            padding=25,
            border_radius=12,
        )
    
    def _build_kommentar_section(self):
        """Kommentare"""
        if not self.kommentare:
            content = ft.Text("Keine Kommentare vorhanden", size=14, color="#64748b", italic=True)
        else:
            kommentar_items = []
            for kommentar in self.kommentare:
                # Datum formatieren
                datum = kommentar.get('Datum', '')
                if isinstance(datum, datetime):
                    datum_str = datum.strftime("%d.%m.%Y %H:%M")
                else:
                    datum_str = str(datum)
                
                kommentar_items.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Text(datum_str, size=12, color="#64748b"),
                            ft.Text(kommentar.get('text', ''), size=14),
                        ], spacing=5),
                        padding=15,
                        border_radius=8,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                    )
                )
            
            content = ft.Column(kommentar_items, spacing=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Kommentare", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(color="#475569"),
                content,
            ], spacing=10),
            padding=25,
            border_radius=12,
        )
    
    def _go_back(self):
        """Zurück zur Lead-Status-Liste"""
        self.parent_view.render()
