import flet as ft
from datetime import datetime
from backend.auswertung_manager import AuswertungManager
try:
    from openpyxl import Workbook
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


# ============================================================================
# VIEW-KLASSE (UI / Darstellung)
# ============================================================================

class AuswertungView:
    """Zeigt alle Leads für Auswertungszwecke an"""
    
    def __init__(self, page: ft.Page, manager: AuswertungManager, current_user: dict, app_controller=None):
        self.page = page
        self.manager = manager
        self.current_user = current_user
        self.app_controller = app_controller
        self.all_leads = []
        self.filtered_leads = []
        self.current_filter_erfasser = None
        self.current_filter_status = None
        self.search_query = ""
        
        # UI-Referenzen
        self.erfasser_dropdown = None
        self.status_dropdown = None
        self.search_field = None
        self.lead_list_container = None
        self.stats_section = None
        
    def render(self):
        """Zeigt die Auswertungs-Ansicht"""
        self.page.clean()
        self.page.padding = 0
        
        # Leads laden
        self._load_leads()
        
        # Statistiken abrufen
        stats = self.manager.get_statistics()
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=lambda e: self._go_back(),
                        tooltip="Zurück"
                    ),
                    ft.Text("Lead Ansicht - Alle Leads", size=24, weight=ft.FontWeight.BOLD),
                ], spacing=10),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_size=28,
                        on_click=lambda e: self._export_to_excel(),
                        tooltip="Als Excel exportieren (mit Filtern)"
                    ),
                ], spacing=15),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
        )
        
        # Statistik-Karten
        self.stats_section = ft.Container(
            content=ft.Row([
                self._create_stat_card("Gesamt", stats.get('gesamt', 0), "#3b82f6"),
                self._create_stat_card("Offen", stats.get('offen', 0), "#f59e0b"),
                self._create_stat_card("In Bearbeitung", stats.get('in_bearbeitung', 0), "#8b5cf6"),
                self._create_stat_card("Erledigt", stats.get('erledigt', 0), "#10b981"),
                self._create_stat_card("Abgelehnt", stats.get('abgelehnt', 0), "#ef4444"),
                self._create_stat_card("Angebot erstellt", stats.get('angebot_erstellt', 0), "#9ca3af"),
            ], spacing=15, wrap=True),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
        )
        
        # Filter-Leiste
        filter_section = self._create_filter_section()
        
        # Lead-Liste Container
        self.lead_list_container = ft.Container(
            content=self._create_lead_list(),
            expand=True,
        )
        
        # Hauptcontainer
        main_content = ft.Column([
            header,
            self.stats_section,
            filter_section,
            self.lead_list_container,
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        
        self.page.add(main_content)
    
    def _create_stat_card(self, title, value, color):
        """Erstellt eine Statistik-Karte"""
        return ft.Container(
            content=ft.Column([
                ft.Text(title, size=14, color="#94a3b8"),
                ft.Text(str(value), size=32, weight=ft.FontWeight.BOLD),
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            border_radius=12,
            width=150,
            border=ft.border.all(2, color),
        )
    
    def _create_filter_section(self):
        """Erstellt die Filter-Leiste"""
        erfasser_list = self.manager.get_all_erfasser()
        
        self.erfasser_dropdown = ft.Dropdown(
            label="Nach Erfasser filtern",
            width=250,
            options=[ft.DropdownOption(key="all", text="Alle Erfasser")] +
                    [ft.DropdownOption(key=str(e['benutzer_id']), text=e['name']) 
                     for e in erfasser_list],
            value="all",
            on_select=lambda e: self._filter_by_erfasser(e.control.value),
        )
        
        self.status_dropdown = ft.Dropdown(
            label="Nach Status filtern",
            width=250,
            options=[
                ft.DropdownOption(key="all", text="Alle Anzeigen"),
                ft.DropdownOption(key="1", text="Offen"),
                ft.DropdownOption(key="2", text="In Bearbeitung"),
                ft.DropdownOption(key="3", text="Erledigt"),
                ft.DropdownOption(key="4", text="Abgelehnt"),
                ft.DropdownOption(key="5", text="Angebot erstellt"),
            ],
            value="all",
            on_select=lambda e: self._filter_by_status(e.control.value),
        )
        
        self.search_field = ft.TextField(
            label="Suchen",
            hint_text="Kunde, Produkt, Erfasser...",
            width=300,
            on_change=lambda e: self._search_leads(e.control.value),
            prefix_icon=ft.Icons.SEARCH,
        )
        
        reset_button = ft.ElevatedButton(
            "Filter zurücksetzen",
            icon=ft.Icons.REFRESH,
            on_click=lambda e: self._reset_filters(),
        )
        
        return ft.Container(
            content=ft.Row([
                self.erfasser_dropdown,
                self.status_dropdown,
                self.search_field,
                reset_button,
            ], spacing=15, wrap=True),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        )
    
    def _create_lead_list(self):
        """Erstellt die Lead-Liste"""
        if not self.filtered_leads:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.INBOX, size=64, color="#475569"),
                    ft.Text("Keine Leads gefunden", size=18, color="#94a3b8"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=50,
            )
        
        lead_items = []
        for lead in self.filtered_leads:
            lead_items.append(self._create_lead_card(lead))
        
        return ft.Container(
            content=ft.Column(lead_items, spacing=10, scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
            expand=True,
        )
    
    def _create_lead_card(self, lead):
        """Erstellt eine Lead-Karte"""
        # Farbe basierend auf Status
        status_colors = {
            "Offen": "#f59e0b",
            "In Bearbeitung": "#8b5cf6",
            "Erledigt": "#10b981",
            "Abgelehnt": "#ef4444",
        }
        status_color = status_colors.get(lead.get('status_name', 'Offen'), "#64748b")
        
        # Datum formatieren
        datum = lead.get('datum_erfasst', '')
        if isinstance(datum, datetime):
            datum_str = datum.strftime("%d.%m.%Y %H:%M")
        else:
            datum_str = str(datum)
        
        return ft.Container(
            content=ft.Column([
                # Kopfzeile
                ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"#{lead.get('lead_id')}", size=12, weight=ft.FontWeight.BOLD),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4,
                        ),
                        ft.Text(lead.get('kunde_name', 'Unbekannt'), size=16, weight=ft.FontWeight.W_600),
                    ], spacing=10),
                    ft.Container(
                        content=ft.Text(lead.get('status_name', 'Offen'), size=12, color="white"),
                        bgcolor=status_color,
                        padding=ft.padding.symmetric(horizontal=10, vertical=5),
                        border_radius=12,
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=1, color="#475569"),
                
                # Details
                ft.Row([
                    ft.Column([
                        ft.Text("Produkt:", size=12, color="#64748b"),
                        ft.Text(lead.get('produkt_name', 'Unbekannt'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Erfasser:", size=12, color="#64748b"),
                        ft.Text(lead.get('erfasser_name', 'Unbekannt'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Bearbeiter:", size=12, color="#64748b"),
                        ft.Text(lead.get('bearbeiter_name', 'Nicht zugewiesen'), size=14),
                    ], spacing=2),
                    ft.Column([
                        ft.Text("Erfasst am:", size=12, color="#64748b"),
                        ft.Text(datum_str, size=14),
                    ], spacing=2),
                ], spacing=30, wrap=True),
                
                # Zusätzliche Informationen
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY_OUTLINED, size=16, color="#64748b"),
                        ft.Text(lead.get('produktgruppe_name', ''), size=12, color="#94a3b8"),
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color="#64748b"),
                        ft.Text(lead.get('produktzustand_name', ''), size=12, color="#94a3b8"),
                    ], spacing=5),
                    ft.Row([
                        ft.Icon(ft.Icons.SOURCE_OUTLINED, size=16, color="#64748b"),
                        ft.Text(lead.get('quelle_name', ''), size=12, color="#94a3b8"),
                    ], spacing=5),
                ], spacing=20, wrap=True),
            ], spacing=10),
            padding=20,
            border_radius=12,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            on_click=lambda e, l=lead: self._show_lead_details(l),
            ink=True,
        )
    
    def _load_leads(self):
        """Lädt alle Leads aus der Datenbank"""
        self.all_leads = self.manager.get_all_leads()
        self.filtered_leads = self.all_leads.copy()
    
    def _filter_by_erfasser(self, erfasser_id):
        """Filtert Leads nach Erfasser"""
        if erfasser_id == "all":
            self.current_filter_erfasser = None
        else:
            self.current_filter_erfasser = int(erfasser_id)
        self._apply_filters()
    
    def _filter_by_status(self, status_id):
        """Filtert Leads nach Status"""
        if status_id == "all":
            self.current_filter_status = None
        else:
            self.current_filter_status = int(status_id)
        self._apply_filters()
    
    def _search_leads(self, query):
        """Sucht in Leads nach Text"""
        self.search_query = query.lower()
        self._apply_filters()
    
    def _apply_filters(self):
        """Wendet alle aktiven Filter an"""
        self.filtered_leads = self.all_leads.copy()
        
        # Erfasser-Filter
        if self.current_filter_erfasser is not None:
            self.filtered_leads = [
                lead for lead in self.filtered_leads 
                if lead.get('erfasser_id') == self.current_filter_erfasser
            ]
        
        # Status-Filter
        if self.current_filter_status is not None:
            self.filtered_leads = [
                lead for lead in self.filtered_leads 
                if lead.get('status_id') == self.current_filter_status
            ]
        
        # Suchfilter
        if self.search_query:
            self.filtered_leads = [
                lead for lead in self.filtered_leads
                if self.search_query in str(lead.get('kunde_name', '')).lower() or
                   self.search_query in str(lead.get('produkt_name', '')).lower() or
                   self.search_query in str(lead.get('erfasser_name', '')).lower() or
                   self.search_query in str(lead.get('bearbeiter_name', '')).lower()
            ]
        
        # Nur die Lead-Liste aktualisieren, nicht die gesamte Seite
        self._update_lead_list()
    
    def _reset_filters(self):
        """Setzt alle Filter zurück"""
        self.current_filter_erfasser = None
        self.current_filter_status = None
        self.search_query = ""
        if self.erfasser_dropdown:
            self.erfasser_dropdown.value = "all"
        if self.status_dropdown:
            self.status_dropdown.value = "all"
        if self.search_field:
            self.search_field.value = ""
        self._apply_filters()
    
    def _update_lead_list(self):
        """Aktualisiert nur die Lead-Liste ohne die gesamte Seite neu zu rendern"""
        if self.lead_list_container:
            self.lead_list_container.content = self._create_lead_list()
            self.page.update()
    
    def _show_lead_details(self, lead):
        """Zeigt die Detailansicht für einen Lead"""
        detail_view = LeadDetailViewAuswertung(self.page, self.manager, lead, self)
        detail_view.render()
    
    def _export_to_excel(self):
        """Exportiert ALLE Leads als Excel-Datei mit aktiven Filtern"""
        if not EXCEL_AVAILABLE:
            self._show_message(
                "Excel-Export nicht verfügbar",
                "Die benötigte Bibliothek 'openpyxl' ist nicht installiert.\n\nBitte installieren Sie: pip install openpyxl"
            )
            return
        
        if not self.all_leads:
            self._show_message("Keine Daten zum Exportieren", "Es wurden keine Leads gefunden.")
            return
        
        # Erfasser-Namen für Filter abrufen
        erfasser_name = self._get_erfasser_name(self.current_filter_erfasser) if self.current_filter_erfasser else ""
        
        # Excel-Export über Manager durchführen
        success, filename, message = self.manager.export_to_excel(
            all_leads=self.all_leads,
            current_filter_status=self.current_filter_status,
            current_filter_erfasser=self.current_filter_erfasser,
            search_query=self.search_query,
            erfasser_name_for_filter=erfasser_name
        )
        
        # Ergebnis anzeigen
        if success:
            self._show_message("Export erfolgreich", message, success=True)
        else:
            self._show_message("Export fehlgeschlagen", message)
    
    def _get_erfasser_name(self, erfasser_id):
        """Gibt den Erfasser-Namen für eine Erfasser-ID zurück"""
        if self.erfasser_dropdown and self.erfasser_dropdown.options:
            for option in self.erfasser_dropdown.options:
                if option.key == str(erfasser_id):
                    return option.text
        return ""
    
    def _show_message(self, title, message, success=False):
        """Zeigt eine Benachrichtigung an"""
        def close_dialog(e):
            self.page.pop_dialog()
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        self.page.show_dialog(dialog)
    
    def _go_back(self):
        """Zurück zum Hauptmenü"""
        if self.app_controller:
            # Für rolle_id = 4 zurück zum Auswertungsmenü, sonst normales Hauptmenü
            if self.current_user.get('rolle_id') == 4:
                self.app_controller.show_auswertung_menu()
            else:
                self.app_controller.show_main_app()


# ============================================================================
# DETAIL-VIEW FÜR AUSWERTUNG (nur Anzeige, keine Aktionen)
# ============================================================================

class LeadDetailViewAuswertung:
    """Detailansicht eines Leads in der Auswertung (nur lesend)"""
    
    def __init__(self, page: ft.Page, manager: AuswertungManager, lead: dict, parent_view):
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
            "Offen": "#f59e0b",
            "In Bearbeitung": "#8b5cf6",
            "Erledigt": "#10b981",
            "Abgelehnt": "#ef4444",
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
        """Zurück zur Auswertungsliste"""
        self.parent_view.render()
