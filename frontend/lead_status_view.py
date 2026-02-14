import flet as ft
from datetime import datetime
from backend.lead_status_manager import LeadStatusManager, Lead

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
        self.page.padding = 5
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
            ft.Text(f"Meine erstellten Leads ({len(filtered_leads)})", size=18, weight=ft.FontWeight.BOLD),
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
                padding=5,
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
            ft.DropdownOption("1", "Offen"),
            ft.DropdownOption("2", "In Bearbeitung"),
            ft.DropdownOption("4", "Abgelehnt"),
            ft.DropdownOption("5", "Angebot erstellt"),
            ft.DropdownOption("3", "Erledigt"),
            ft.DropdownOption("all", "Alle anzeigen")
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
            on_select=on_filter_change,
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
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
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
        
        # Prüfe ob Lead zum Löschen vorgemerkt ist
        is_marked_for_deletion = self.lead_manager.is_lead_marked_for_deletion(lead.lead_id)
        
        # Prüfe ob Lead kürzlich eine Aktion erhalten hat (innerhalb 24h, außer Löschung)
        # Nur ungesehene Aktionen berücksichtigen
        has_update = self.lead_manager.has_recent_action(lead.lead_id, self.current_user['benutzer_id'])
        
        # Titel-Zeile mit optionalem Badge
        badge_controls = []
        
        # Prüfe ob mobile Ansicht (Breite < 600px)
        is_mobile = self.page.width and self.page.width < 600
        
        # Wenn zum Löschen vorgemerkt, zeige rotes Badge
        if is_marked_for_deletion:
            if is_mobile:
                # Mobile: Nur Icon
                badge_controls.append(
                    ft.Container(
                        content=ft.Icon(ft.Icons.DELETE_OUTLINE, color="white", size=18),
                        bgcolor="#dc2626",
                        padding=ft.Padding.symmetric(horizontal=8, vertical=6),
                        border_radius=4,
                    )
                )
            else:
                # Desktop: Icon + Text
                badge_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.DELETE_OUTLINE, color="white", size=16),
                            ft.Text("ZUM LÖSCHEN VORGEMERKT", size=11, color="white", weight=ft.FontWeight.BOLD)
                        ], spacing=3),
                        bgcolor="#dc2626",
                        padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                        border_radius=4,
                    )
                )
        # Sonst wenn andere Aktionen, zeige orange Badge
        elif has_update:
            badge_controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.NOTIFICATIONS_ACTIVE, color="white", size=16),
                        ft.Text("AKTUALISIERT", size=11, color="white", weight=ft.FontWeight.BOLD)
                    ], spacing=3),
                    bgcolor="orange",
                    padding=ft.Padding.symmetric(horizontal=6, vertical=3),
                    border_radius=4,
                )
            )
        
        # Titel-Zeile: Badge links auf Mobile, rechts auf Desktop
        if is_mobile and badge_controls:
            title_content = ft.Row([
                *badge_controls,
                ft.Text(
                    f"Lead #{lead.lead_id} - {lead.kunde_name}",
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True
                ),
            ], spacing=10)
        else:
            title_content = ft.Row([
                ft.Text(
                    f"Lead #{lead.lead_id} - {lead.kunde_name}",
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True
                ),
                *badge_controls
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
                                ft.Text(
                                    f"{lead.produkt_name}",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS
                                ),
                                ft.Text("| Status:"),
                                status_badge
                            ], spacing=5),
                        ),
                        # Status-Zeile - unterschiedliche Anordnung für Mobile/Desktop
                        ft.Row([
                            ft.Container(
                                content=ft.Text(
                                    f"Bearbeiter: {lead.bearbeiter_name}",
                                    size=11,
                                    color="grey",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    text_align=ft.TextAlign.LEFT
                                ),
                                width=150
                            ),
                        ], spacing=10) if is_mobile else ft.Row([
                            ft.Icon(status_icon, color=bg_color, size=16),
                            ft.Text(status_desc, size=11, color=bg_color, weight=ft.FontWeight.BOLD),
                            ft.Container(expand=True),
                            ft.Container(
                                content=ft.Text(
                                    f"Bearbeiter: {lead.bearbeiter_name}",
                                    size=11,
                                    color="grey",
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    text_align=ft.TextAlign.RIGHT
                                ),
                                width=150
                            )
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
        self.current_user = parent_view.current_user  # Benutzer vom parent_view holen
        self.aktionen = []
        self.kommentare = []
    
    def render(self):
        """Zeigt die Lead-Details"""
        self.page.clean()
        self.page.padding = 0
        
        # Markiere Lead als angesehen durch den aktuellen Benutzer
        self.manager.mark_lead_as_viewed(self.lead.get('lead_id'), self.current_user['benutzer_id'])
        
        # Aktualisierte Daten laden
        self.lead = self.manager.get_lead_by_id(self.lead.get('lead_id'))
        self.aktionen = self.manager.get_lead_aktionen(self.lead.get('lead_id'))
        self.kommentare = self.manager.get_lead_kommentare(self.lead.get('lead_id'))
        
        # Prüfe ob Lead bereits vorgemerkt ist
        is_marked = self.manager.is_lead_marked_for_deletion(self.lead.get('lead_id'))
        
        # Prüfe ob mobile Ansicht (Breite < 600px)
        is_mobile = self.page.width and self.page.width < 600
        
        # Button zum Vormerken nur anzeigen wenn:
        # 1. Lead noch offen ist (status_id = 1)
        # 2. Benutzer der Erfasser ist
        # 3. Lead noch nicht vorgemerkt ist
        show_mark_button = (
            self.lead.get('status_id') == 1 and 
            self.lead.get('erfasser_id') == self.current_user['benutzer_id'] and 
            not is_marked
        )
        
        # Header mit Button
        header_controls = [
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self._go_back(),
                tooltip="Zurück zur Liste"
            ),
            ft.Text(f"Lead #{self.lead.get('lead_id')}", size=24, weight=ft.FontWeight.BOLD),
        ]
        
        # Füge Vormerken-Button hinzu, wenn Bedingungen erfüllt sind
        if show_mark_button:
            header_controls.append(ft.Container(expand=True))  # Spacer
            header_controls.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="#dc2626",
                    tooltip="Zum Löschen vormerken",
                    on_click=lambda e: self._mark_for_deletion(),
                    bgcolor="#fee2e2",
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    )
                )
            )
        
        # Zeige Info wenn bereits vorgemerkt
        if is_marked:
            header_controls.append(ft.Container(expand=True))  # Spacer
            
            if is_mobile:
                # Mobile: Nur Info-Icon mit Dialog
                def show_info_dialog(e):
                    dialog = ft.AlertDialog(
                        title=ft.Text("Zum Löschen vorgemerkt"),
                        content=ft.Text("Dieser Lead ist zum Löschen vorgemerkt. Warte auf Administration."),
                        actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())]
                    )
                    self.page.show_dialog(dialog)
                
                header_controls.append(
                    ft.IconButton(
                        icon=ft.Icons.INFO_OUTLINE,
                        icon_color="#dc2626",
                        icon_size=28,
                        tooltip="Zum Löschen vorgemerkt",
                        on_click=show_info_dialog,
                        style=ft.ButtonStyle(
                            bgcolor="#fee2e2",
                            shape=ft.RoundedRectangleBorder(radius=8),
                        )
                    )
                )
            else:
                # Desktop: Vollständiges Badge mit Text
                header_controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INFO_OUTLINE, color="#dc2626", size=20),
                            ft.Text("Zum Löschen vorgemerkt", color="#dc2626", size=14, weight=ft.FontWeight.W_500)
                        ], spacing=8),
                        bgcolor="#fee2e2",
                        padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                        border_radius=8,
                    )
                )
        
        header = ft.Container(
            content=ft.Row(header_controls, spacing=10),
            padding=ft.Padding.symmetric(horizontal=10, vertical=20),
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
                padding=ft.Padding.symmetric(horizontal=10, vertical=20),
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
                        padding=ft.Padding.symmetric(horizontal=15, vertical=8),
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
            padding=15,
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
                        border=ft.Border.all(1, ft.Colors.OUTLINE),
                    )
                )
            
            content = ft.Column(aktion_items, spacing=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Verlauf", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(color="#475569"),
                content,
            ], spacing=10),
            padding=15,
            border_radius=12,
        )
    
    def _build_kommentar_section(self):
        """Kommentare"""
        # Prüfe ob User der Erfasser ist und Lead offen ist
        can_edit = (
            self.lead.get('erfasser_id') == self.current_user['benutzer_id'] and
            self.lead.get('status_id') == 1
        )
        
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
                
                # Container-Inhalt mit optionalem Edit-Button
                kommentar_content = ft.Column([
                    ft.Row([
                        ft.Text(datum_str, size=12, color="#64748b"),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=16,
                            tooltip="Kommentar bearbeiten",
                            on_click=lambda e, k=kommentar: self._edit_kommentar(k),
                        ) if can_edit else ft.Container(),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Text(kommentar.get('text', ''), size=14),
                ], spacing=5)
                
                kommentar_items.append(
                    ft.Container(
                        content=kommentar_content,
                        padding=15,
                        border_radius=8,
                        border=ft.Border.all(1, ft.Colors.OUTLINE),
                    )
                )
            
            content = ft.Column(kommentar_items, spacing=10)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Kommentare", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(color="#475569"),
                content,
            ], spacing=10),
            padding=15,
            border_radius=12,
        )
    
    def _go_back(self):
        """Zurück zur Lead-Status-Liste"""
        self.parent_view.render()
    
    def _edit_kommentar(self, kommentar):
        """Öffnet einen Dialog zum Bearbeiten eines Kommentars"""
        # TextField für neuen Kommentartext
        kommentar_field = ft.TextField(
            label="Kommentar",
            value=kommentar.get('text', ''),
            multiline=True,
            min_lines=3,
            max_lines=5,
            autofocus=True,
        )
        
        def save_edit(e):
            new_text = kommentar_field.value.strip()
            if not new_text:
                # Zeige Fehler, wenn leer
                snackbar = ft.SnackBar(
                    content=ft.Text("Kommentar darf nicht leer sein"),
                    bgcolor="#dc2626",
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
                return
            
            # Kommentar aktualisieren
            self.manager.update_kommentar(kommentar.get('kommentar_id'), new_text)
            
            self.page.pop_dialog()
            
            # Snackbar mit Erfolg anzeigen
            snackbar = ft.SnackBar(
                content=ft.Text("Kommentar erfolgreich aktualisiert"),
                bgcolor="#10b981",
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
            
            # Ansicht neu laden
            self.render()
        
        def cancel_edit(e):
            self.page.pop_dialog()
            self.page.update()
        
        # Dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Kommentar bearbeiten"),
            content=kommentar_field,
            actions=[
                ft.TextButton("Abbrechen", on_click=cancel_edit),
                ft.Button(
                    "Speichern",
                    bgcolor="#10b981",
                    color="white",
                    on_click=save_edit
                ),
            ],
        )
        
        self.page.show_dialog(dialog)
        self.page.update()
    
    def _mark_for_deletion(self):
        """Markiert den Lead zum Löschen"""
        def confirm_mark(e):
            self.page.pop_dialog()
            # Lead zum Löschen vormerken
            success, message = self.manager.mark_lead_for_deletion(
                self.lead.get('lead_id'), 
                self.current_user['benutzer_id'],
                "Lead wurde durch Erfasser zum Löschen vorgemerkt"
            )
            
            # Snackbar mit Ergebnis anzeigen
            snackbar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor="#10b981" if success else "#dc2626",
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
            
            # Wenn erfolgreich, Ansicht neu laden
            if success:
                self.render()
        
        def cancel_mark(e):
            self.page.pop_dialog()
            self.page.update()
        
        # Bestätigungsdialog
        dialog = ft.AlertDialog(
            title=ft.Text("Lead zum Löschen vormerken?"),
            content=ft.Text(
                "Möchten Sie diesen Lead wirklich zum Löschen vormerken?\n\n"
                "Der Lead wird für Administratoren als löschbar markiert und kann "
                "von diesen endgültig gelöscht werden."
            ),
            actions=[
                ft.TextButton("Abbrechen", on_click=cancel_mark),
                ft.Button(
                    "Vormerken",
                    bgcolor="#dc2626",
                    color="white",
                    on_click=confirm_mark
                ),
            ],
        )
        
        self.page.show_dialog(dialog)
        self.page.update()
