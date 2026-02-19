import flet as ft
from datetime import datetime

# ============================================================================
# VIEW-KLASSE (User Interface für Außendienst)
# ============================================================================

class SearchField:
    """Eingabefeld mit Live-Suchfunktion"""
    
    def __init__(self, label: str, options: list, on_select=None, width=400):
        self.label = label
        self.options = options  # List of dicts mit 'key' und 'text'
        self.on_select = on_select
        self.width = width
        self.selected_value = None
        self.selected_text = ""
        self.filtered_options = []
        
        self.text_field = ft.TextField(
            label=label,
            width=width,
            on_change=self._on_text_change
        )
        
        self.suggestions_list = ft.ListView(
            visible=False,
            height=150,
            spacing=0
        )
        
        self.container = ft.Column([
            self.text_field,
            self.suggestions_list
        ], spacing=0)
    
    def _on_text_change(self, e):
        """Filtert Optionen basierend auf Eingabe"""
        search_text = e.control.value.lower() if e.control.value else ""
        
        print(f"[DEBUG SearchField] Text geändert: '{search_text}'")
        
        if not search_text:
            self.suggestions_list.visible = False
            # NICHT selected_value zurücksetzen bei jedem Keystroke!
        else:
            # Filtere Optionen
            self.filtered_options = [
                opt for opt in self.options
                if search_text in opt['text'].lower()
            ]
            
            # Prüfe ob exakte Übereinstimmung existiert
            exact_match = None
            for opt in self.options:
                if opt['text'].lower() == search_text:
                    exact_match = opt
                    break
            
            if exact_match:
                print(f"[DEBUG SearchField] Exakte Übereinstimmung gefunden: {exact_match['text']}")
                # Exakte Übereinstimmung gefunden - automatisch auswählen
                self._select_option(exact_match['key'], exact_match['text'])
            else:
                # Zeige Suggestions
                self.suggestions_list.controls.clear()
                for opt in self.filtered_options[:10]:  # Max 10 Suggestions
                    btn = ft.Container(
                        content=ft.Text(opt['text'], size=12),
                        padding=8,
                        bgcolor=ft.Colors.TRANSPARENT
                    )
                    btn.data = {'key': opt['key'], 'text': opt['text']}
                    btn.on_click = self._create_selection_handler(opt['key'], opt['text'])
                    self.suggestions_list.controls.append(btn)
                
                self.suggestions_list.visible = len(self.filtered_options) > 0
    
    def _create_selection_handler(self, key: str, text: str):
        """Erstellt einen Click-Handler für eine Option"""
        def handler(e):
            self._select_option(key, text)
        return handler
    
    def _select_option(self, key: str, text: str):
        """Wählt eine Option aus"""
        print(f"[DEBUG SearchField] Option ausgewählt: {text} (key={key})")
        self.text_field.value = text
        self.selected_value = key
        self.selected_text = text
        self.suggestions_list.visible = False
        
        if self.on_select:
            self.on_select(key)
    
    @property
    def value(self):
        """Gibt die ausgewählte ID zurück"""
        print(f"[DEBUG SearchField] .value aufgerufen -> {self.selected_value}")
        return self.selected_value
    
    @property
    def error_text(self):
        return self.text_field.error_text
    
    @error_text.setter
    def error_text(self, value):
        self.text_field.error_text = value

class AussendienstView:
    """Hauptansicht für Außendienst: Lead erstellen"""
    
    def __init__(self, page: ft.Page, aussendienst_manager, current_user: dict):
        self.page = page
        self.manager = aussendienst_manager
        self.current_user = current_user
        self.app_controller = None  # Wird von AppController gesetzt
        
        # Multi-Step Formular
        self.current_step = 1  # Aktueller Schritt (1-4)
        self.total_steps = 4
        
        # Ausgewählte Werte
        self.selected_firma = None
        self.selected_ansprechpartner = None
        self.selected_produktgruppe = None
        self.selected_produkt = None
        self.selected_zustand = None
        self.selected_quelle = None
        self.selected_bearbeiter = None
        
        # UI-Komponenten
        self.firma_dropdown = None
        self.ansprechpartner_dropdown = None
        self.produktgruppe_dropdown = None
        self.produkt_dropdown = None
        self.zustand_dropdown = None
        self.quelle_dropdown = None
        self.bearbeiter_dropdown = None
        self.beschreibung_field = None
    
    def render(self):
        """Zeigt die Lead-Erfassungsmaske mit Multi-Step Formular"""
        try:
            self.page.clean()
            
            # Header
            header = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Zurück zum Menü",
                    on_click=lambda e: self._go_back_to_menu()
                ),
                ft.Text("Neuen Lead erfassen", size=24, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
            # Fortschrittsanzeige
            progress_indicator = self._build_progress_indicator()
            
            # Aktueller Schritt
            step_content = self._build_current_step()
            
            # Navigation Buttons
            nav_buttons = self._build_navigation_buttons()
            
            self.page.add(
                ft.Container(
                    content=ft.Column([
                        header,
                        ft.Divider(),
                        progress_indicator,
                        ft.Divider(height=20, color="transparent"),
                        step_content,
                        ft.Divider(height=20, color="transparent"),
                        nav_buttons
                    ], scroll=ft.ScrollMode.AUTO, expand=True),
                    padding=20,
                    expand=True
                )
            )
        except Exception as ex:
            print(f"[DEBUG] FEHLER in render(): {ex}")
            import traceback
            traceback.print_exc()
            self.page.add(ft.Text(f"Fehler beim Laden: {str(ex)}", color="red"))
    
    def _build_progress_indicator(self):
        """Erstellt die Fortschrittsanzeige"""
        steps = [
            {"number": 1, "label": "Kunde"},
            {"number": 2, "label": "Produkt"},
            {"number": 3, "label": "Details"},
            {"number": 4, "label": "Beschreibung"}
        ]
        
        step_indicators = []
        for step in steps:
            is_current = step["number"] == self.current_step
            is_completed = step["number"] < self.current_step
            
            # Farbe basierend auf Status
            if is_completed:
                color = ft.Colors.GREEN
                icon = ft.Icons.CHECK_CIRCLE
            elif is_current:
                color = ft.Colors.BLUE
                icon = ft.Icons.RADIO_BUTTON_CHECKED
            else:
                color = ft.Colors.GREY_400
                icon = ft.Icons.RADIO_BUTTON_UNCHECKED
            
            step_indicators.append(
                ft.Column([
                    ft.Icon(icon, color=color, size=30),
                    ft.Text(
                        step["label"],
                        size=12,
                        weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
                        color=color
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5)
            )
        
        return ft.Row(
            step_indicators,
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            spacing=10
        )
    
    def _build_current_step(self):
        """Erstellt den Inhalt für den aktuellen Schritt"""
        if self.current_step == 1:
            return self._build_step_1_kundendaten()
        elif self.current_step == 2:
            return self._build_step_2_produktinformationen()
        elif self.current_step == 3:
            return self._build_step_3_lead_details()
        elif self.current_step == 4:
            return self._build_step_4_beschreibung()
        else:
            return ft.Text("Ungültiger Schritt", color="red")
    
    def _build_navigation_buttons(self):
        """Erstellt die Navigations-Buttons"""
        buttons = []
        
        # Zurück-Button (außer bei Schritt 1)
        if self.current_step > 1:
            buttons.append(
                ft.OutlinedButton(
                    "Zurück",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: self._previous_step()
                )
            )
        
        # Abbrechen-Button
        buttons.append(
            ft.OutlinedButton(
                "Abbrechen",
                icon=ft.Icons.CANCEL,
                on_click=lambda e: self._go_back_to_menu()
            )
        )
        
        # Weiter/Speichern-Button
        if self.current_step < self.total_steps:
            buttons.append(
                ft.ElevatedButton(
                    "Weiter",
                    icon=ft.Icons.ARROW_FORWARD,
                    on_click=lambda e: self._next_step(),
                    bgcolor=ft.Colors.BLUE,
                    color=ft.Colors.WHITE
                )
            )
        else:
            buttons.append(
                ft.ElevatedButton(
                    "Lead speichern",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: self._save_lead(),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE
                )
            )
        
        return ft.Row(
            buttons,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10
        )
    
    def _build_step_1_kundendaten(self):
        """Schritt 1: Kundendaten eingeben"""
        print("\n[DEBUG] ===== Schritt 1: Kundendaten =====")
        
        # Firma SearchField erstellen (nur beim ersten Mal)
        if self.firma_dropdown is None:
            firmen = self.manager.get_alle_firmen()
            self.firma_options = [
                {'key': str(f['id']), 'text': f"{f['firma']} ({f['ort']})"}
                for f in firmen
            ]
            
            self.firma_dropdown = SearchField(
                label="Firma auswählen *",
                options=self.firma_options,
                on_select=lambda key: self._on_firma_selected(key),
                width=400
            )
        
        # Ansprechpartner Dropdown erstellen (nur beim ersten Mal)
        if self.ansprechpartner_dropdown is None:
            self.ansprechpartner_dropdown = ft.Dropdown(
                label="Ansprechpartner auswählen *",
                options=[],
                width=400
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Schritt 1: Kundendaten", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                ft.Text("Wählen Sie die Firma und den Ansprechpartner aus", size=14, color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.firma_dropdown.container,
                ft.Divider(height=10, color="transparent"),
                self.ansprechpartner_dropdown,
                ft.Divider(height=10, color="transparent"),
                ft.Text("* Pflichtfelder", size=12, color="grey", italic=True)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
    
    def _build_step_2_produktinformationen(self):
        """Schritt 2: Produktinformationen eingeben"""
        print("\n[DEBUG] ===== Schritt 2: Produktinformationen =====")
        
        # Produktgruppe Dropdown erstellen (nur beim ersten Mal)
        if self.produktgruppe_dropdown is None:
            produktgruppen = self.manager.get_produktgruppen()
            produktgruppe_options = [
                ft.DropdownOption(key=str(pg['produkt_id']), text=pg['produkt'])
                for pg in produktgruppen
            ]
            
            self.produktgruppe_dropdown = ft.Dropdown(
                label="Produktgruppe auswählen *",
                options=produktgruppe_options,
                on_select=lambda e: self._on_produktgruppe_selected(e.control.value),
                width=400
            )
        
        # Produkt Dropdown erstellen (nur beim ersten Mal)
        if self.produkt_dropdown is None:
            self.produkt_dropdown = ft.Dropdown(
                label="Produkt auswählen *",
                options=[],
                width=400
            )
        
        # Zustand Dropdown erstellen (nur beim ersten Mal)
        if self.zustand_dropdown is None:
            zustaende = self.manager.get_produktzustaende()
            zustand_options = [
                ft.DropdownOption(key=str(z['id']), text=z['zustand'])
                for z in zustaende
                if z['id'] != 3  # ID 3 ist für Serviceleistungen reserviert (NULL-Wert)
            ]
            
            self.zustand_dropdown = ft.Dropdown(
                label="Zustand *",
                options=zustand_options,
                width=400
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Schritt 2: Produktinformationen", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                ft.Text("Wählen Sie Produktgruppe, Produkt und Zustand aus", size=14, color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.produktgruppe_dropdown,
                ft.Divider(height=10, color="transparent"),
                self.produkt_dropdown,
                ft.Divider(height=10, color="transparent"),
                self.zustand_dropdown,
                ft.Divider(height=10, color="transparent"),
                ft.Text("* Pflichtfelder", size=12, color="grey", italic=True)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
    
    def _build_step_3_lead_details(self):
        """Schritt 3: Lead-Details eingeben"""
        print("\n[DEBUG] ===== Schritt 3: Lead-Details =====")
        
        # Quelle Dropdown erstellen (nur beim ersten Mal)
        if self.quelle_dropdown is None:
            quellen = self.manager.get_quellen()
            quelle_options = [
                ft.DropdownOption(key=str(q['id']), text=q['quelle'])
                for q in quellen
            ]
            
            self.quelle_dropdown = ft.Dropdown(
                label="Lead-Herkunft *",
                options=quelle_options,
                width=400
            )
        
        # Bearbeiter Dropdown erstellen (nur beim ersten Mal)
        if self.bearbeiter_dropdown is None:
            bearbeiter = self.manager.get_verfuegbare_bearbeiter()
            bearbeiter_options = [
                ft.DropdownOption(key=str(b['benutzer_id']), text=b['name'])
                for b in bearbeiter
            ]
            
            self.bearbeiter_dropdown = ft.Dropdown(
                label="An Innendienst zuweisen *",
                options=bearbeiter_options,
                width=400
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Schritt 3: Lead-Details", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                ft.Text("Geben Sie Quelle und Bearbeiter an", size=14, color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.quelle_dropdown,
                ft.Divider(height=10, color="transparent"),
                self.bearbeiter_dropdown,
                ft.Divider(height=10, color="transparent"),
                ft.Text("* Pflichtfelder", size=12, color="grey", italic=True)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
    
    def _build_step_4_beschreibung(self):
        """Schritt 4: Beschreibung eingeben"""
        print("\n[DEBUG] ===== Schritt 4: Beschreibung =====")
        
        # Beschreibung TextField erstellen (nur beim ersten Mal)
        if self.beschreibung_field is None:
            self.beschreibung_field = ft.TextField(
                label="Beschreibung / Notizen (optional)",
                multiline=True,
                min_lines=8,
                max_lines=12,
                width=400
            )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Schritt 4: Beschreibung", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(height=10, color="transparent"),
                ft.Text("Fügen Sie optional eine Beschreibung oder Notizen hinzu", size=14, color="grey"),
                ft.Divider(height=20, color="transparent"),
                self.beschreibung_field,
                ft.Divider(height=10, color="transparent"),
                ft.Text("Dieses Feld ist optional", size=12, color="grey", italic=True)
            ], spacing=10),
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=10
        )
    
    def _next_step(self):
        """Wechselt zum nächsten Schritt"""
        # Validierung des aktuellen Schritts
        if not self._validate_current_step():
            return
        
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.render()
    
    def _previous_step(self):
        """Wechselt zum vorherigen Schritt"""
        if self.current_step > 1:
            self.current_step -= 1
            self.render()
    
    def _validate_current_step(self):
        """Validiert die Eingaben des aktuellen Schritts"""
        if self.current_step == 1:
            # Validiere Kundendaten
            if not self.firma_dropdown.value:
                self.firma_dropdown.error_text = "Bitte wählen Sie eine Firma aus"
                self.page.update()
                return False
            
            if not self.ansprechpartner_dropdown.value:
                self.ansprechpartner_dropdown.error_text = "Bitte wählen Sie einen Ansprechpartner aus"
                self.page.update()
                return False
            
            self.selected_ansprechpartner = int(self.ansprechpartner_dropdown.value)
            
        elif self.current_step == 2:
            # Validiere Produktinformationen
            if not self.produktgruppe_dropdown.value:
                self.produktgruppe_dropdown.error_text = "Bitte wählen Sie eine Produktgruppe aus"
                self.page.update()
                return False
            
            if not self.produkt_dropdown.value:
                self.produkt_dropdown.error_text = "Bitte wählen Sie ein Produkt aus"
                self.page.update()
                return False
            
            # Zustand nur validieren wenn das Feld sichtbar ist (nicht bei Serviceleistungen)
            if self.zustand_dropdown.visible and not self.zustand_dropdown.value:
                self.zustand_dropdown.error_text = "Bitte wählen Sie einen Zustand aus"
                self.page.update()
                return False
            
            self.selected_produkt = int(self.produkt_dropdown.value)
            # Zustand nur setzen wenn das Feld sichtbar ist (nicht bei Serviceleistungen)
            if self.zustand_dropdown.visible and self.zustand_dropdown.value:
                self.selected_zustand = int(self.zustand_dropdown.value)
            else:
                self.selected_zustand = 3  # ID 3 = NULL-Eintrag für Serviceleistungen
            
        elif self.current_step == 3:
            # Validiere Lead-Details
            if not self.quelle_dropdown.value:
                self.quelle_dropdown.error_text = "Bitte wählen Sie eine Quelle aus"
                self.page.update()
                return False
            
            if not self.bearbeiter_dropdown.value:
                self.bearbeiter_dropdown.error_text = "Bitte wählen Sie einen Bearbeiter aus"
                self.page.update()
                return False
            
            self.selected_quelle = int(self.quelle_dropdown.value)
            self.selected_bearbeiter = int(self.bearbeiter_dropdown.value)
        
        # Schritt 4 (Beschreibung) hat keine Pflichtfelder
        
        return True
    
    # ---- Event Handlers ----
    
    def _on_firma_selected(self, firma_id):
        """Wird aufgerufen wenn Firma in SearchField ausgewählt wird - lädt automatisch Ansprechpartner"""
        if not firma_id:
            return
        
        self.selected_firma = int(firma_id)
        print(f"[DEBUG] Firma ausgewählt: {self.selected_firma}")
        
        # Ansprechpartner automatisch laden
        try:
            print(f"[DEBUG] Lade Ansprechpartner für Firma-ID: {self.selected_firma}")
            
            # Ansprechpartner laden - filtert nach firma_id
            ansprechpartner = self.manager.get_ansprechpartner_by_firma(self.selected_firma)
            print(f"[DEBUG] Ansprechpartner gefunden: {len(ansprechpartner)}")
            
            if ansprechpartner:
                # Dropdown-Optionen füllen
                self.ansprechpartner_dropdown.options = [
                    ft.DropdownOption(
                        key=str(ap['id']),
                        text=f"{ap['anrede']} {ap['vorname']} {ap['nachname']} ({ap['position']})"
                    )
                    for ap in ansprechpartner
                ]
                
                # Kein Ansprechpartner automatisch auswählen - Nutzer muss explizit wählen
                self.ansprechpartner_dropdown.value = None
                self.ansprechpartner_dropdown.hint_text = "Bitte wählen"
                self.ansprechpartner_dropdown.error_text = None
                print(f"[DEBUG] {len(ansprechpartner)} Ansprechpartner geladen, bitte auswählen")
            else:
                self.ansprechpartner_dropdown.options = []
                self.ansprechpartner_dropdown.value = None
                self.ansprechpartner_dropdown.error_text = "Keine Ansprechpartner für diese Firma gefunden"
                print(f"[DEBUG] Keine Ansprechpartner für Firma {self.selected_firma}")
            
            self.page.update()
            
        except Exception as e:
            print(f"[DEBUG] FEHLER beim Laden der Ansprechpartner: {e}")
            import traceback
            traceback.print_exc()
            self.ansprechpartner_dropdown.error_text = f"Fehler: {str(e)}"
            self.page.update()
    
    def _on_produktgruppe_selected(self, produktgruppe_id):
        """Wird aufgerufen wenn Produktgruppe ausgewählt wird"""
        if not produktgruppe_id:
            self.produkt_dropdown.options = []
            return
        
        self.selected_produktgruppe = int(produktgruppe_id)
        
        # DEBUG
        print(f"[DEBUG] Produktgruppe ausgewählt: {self.selected_produktgruppe}")
        
        # Prüfe ob Serviceleistungen ausgewählt wurden (verstecke Zustand-Feld)
        produktgruppe_text = self.produktgruppe_dropdown.value
        selected_option = next((opt for opt in self.produktgruppe_dropdown.options if opt.key == produktgruppe_text), None)
        if selected_option and "Serviceleistungen" in selected_option.text:
            # Zustand-Feld verstecken für Serviceleistungen
            self.zustand_dropdown.visible = False
            self.zustand_dropdown.value = None  # Wert zurücksetzen
            self.selected_zustand = None
            print("[DEBUG] Serviceleistungen ausgewählt - Zustand-Feld ausgeblendet")
        else:
            # Zustand-Feld anzeigen für alle anderen Produktgruppen
            self.zustand_dropdown.visible = True
            print("[DEBUG] Zustand-Feld angezeigt")
        
        # Produkte laden
        try:
            produkte = self.manager.get_produkte_by_gruppe(self.selected_produktgruppe)
            print(f"[DEBUG] Produkte geladen: {len(produkte)} gefunden")
            print(f"[DEBUG] Erste Produkte: {produkte[:3] if produkte else 'KEINE'}")
            
            if produkte:
                # Filtere Produkte basierend auf der Produktgruppe
                # Stapler (angenommen ID 1) -> nur Produkt-IDs 1-4
                # Industriegeräte (angenommen ID 2) -> nur Produkt-IDs 5-8
                filtered_produkte = produkte
                
                # Prüfe ob es Stapler oder Industriegeräte sind
                if selected_option:
                    if "Stapler" in selected_option.text:
                        # Nur Produkte mit IDs 1-4
                        filtered_produkte = [p for p in produkte if 1 <= p['produkt_id'] <= 4]
                        print(f"[DEBUG] Stapler ausgewählt - gefiltert auf IDs 1-4: {len(filtered_produkte)} Produkte")
                    elif "Industriegeräte" in selected_option.text or "Industrieger" in selected_option.text:
                        # Nur Produkte mit IDs 5-8
                        filtered_produkte = [p for p in produkte if 5 <= p['produkt_id'] <= 8]
                        print(f"[DEBUG] Industriegeräte ausgewählt - gefiltert auf IDs 5-8: {len(filtered_produkte)} Produkte")
                
                self.produkt_dropdown.options = [
                    ft.DropdownOption(key=str(p['produkt_id']), text=p['produkt'])
                    for p in filtered_produkte
                ]
                self.produkt_dropdown.value = None  # Zurücksetzen der Auswahl
                self.produkt_dropdown.error_text = None
            else:
                self.produkt_dropdown.options = []
                self.produkt_dropdown.value = None
                self.produkt_dropdown.error_text = "Keine Produkte gefunden"
        except Exception as e:
            print(f"[DEBUG] FEHLER beim Laden von Produkten: {e}")
            self.produkt_dropdown.error_text = f"Fehler: {str(e)}"
        
        self.page.update()
    
    def _save_lead(self):
        """Lead speichern - mit Validierung"""
        
        print("[DEBUG] ===== _save_lead() aufgerufen! =====")
        print(f"[DEBUG] firma: {self.firma_dropdown.value}")
        print(f"[DEBUG] produkt: {self.produkt_dropdown.value}")
        print(f"[DEBUG] bearbeiter: {self.bearbeiter_dropdown.value}")
        
        try:
            # Validierung
            errors = []
            
            # Prüfe Firma (SearchField)
            if not self.firma_dropdown.value:
                errors.append("Bitte Firma auswählen")
                self.firma_dropdown.error_text = "Pflichtfeld"
            else:
                self.firma_dropdown.error_text = None
            
            # Prüfe Ansprechpartner (Dropdown)
            if not self.ansprechpartner_dropdown.value:
                errors.append("Bitte Ansprechpartner auswählen")
                self.ansprechpartner_dropdown.error_text = "Pflichtfeld"
            else:
                self.ansprechpartner_dropdown.error_text = None
            
            # Prüfe Produktgruppe (Dropdown)
            if not self.produktgruppe_dropdown.value:
                errors.append("Bitte Produktgruppe auswählen")
                self.produktgruppe_dropdown.error_text = "Pflichtfeld"
            else:
                self.produktgruppe_dropdown.error_text = None
            
            # Prüfe Produkt (SearchField)
            if not self.produkt_dropdown.value:
                errors.append("Bitte Produkt auswählen")
                self.produkt_dropdown.error_text = "Pflichtfeld"
            else:
                self.produkt_dropdown.error_text = None
            
            # Prüfe Zustand (Dropdown) - nur wenn sichtbar (nicht bei Serviceleistungen)
            if self.zustand_dropdown.visible and not self.zustand_dropdown.value:
                errors.append("Bitte Zustand auswählen")
                self.zustand_dropdown.error_text = "Pflichtfeld"
            elif self.zustand_dropdown.visible:
                self.zustand_dropdown.error_text = None
            
            # Prüfe Quelle (Dropdown)
            if not self.quelle_dropdown.value:
                errors.append("Bitte Quelle auswählen")
            
            # Prüfe Bearbeiter (Dropdown)
            if not self.bearbeiter_dropdown.value:
                errors.append("Bitte Bearbeiter auswählen (Innendienst zuweisen)")
            
            # Wenn Fehler vorhanden, Dialog anzeigen
            if errors:
                self.page.update()
                error_dialog = ft.AlertDialog(
                    title=ft.Text("Validierungsfehler"),
                    content=ft.Column([
                        ft.Text("Bitte fülle alle Pflichtfelder aus:", weight=ft.FontWeight.BOLD),
                        *[ft.Text(f"• {error}", size=12) for error in errors]
                    ], tight=True),
                    actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())]
                )
                self.page.show_dialog(error_dialog)
                return
            
            print("[DEBUG] Validierung erfolgreich - starte Lead-Erstellung")
            
            # Lead erstellen - Zustand auf ID 3 setzen wenn nicht sichtbar (Serviceleistungen)
            zustand_id = int(self.zustand_dropdown.value) if self.zustand_dropdown.visible and self.zustand_dropdown.value else 3
            
            lead_id = self.manager.create_lead(
                ansprechpartner_id=int(self.ansprechpartner_dropdown.value),
                produkt_id=int(self.produkt_dropdown.value),
                produktgruppe_id=int(self.produktgruppe_dropdown.value),
                produktzustand_id=zustand_id,
                quelle_id=int(self.quelle_dropdown.value),
                erfasser_id=self.current_user['benutzer_id'],
                bearbeiter_id=int(self.bearbeiter_dropdown.value),
                beschreibung=self.beschreibung_field.value
            )
            
            print(f"[DEBUG] Lead-Erstellung abgeschlossen: ID={lead_id}")
            
            if lead_id:
                # Erfolgs-Dialog
                success_dialog = ft.AlertDialog(
                    title=ft.Text("Erfolg!", color=ft.Colors.GREEN),
                    content=ft.Column([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=64, color=ft.Colors.GREEN),
                        ft.Text(f"Lead #{lead_id} wurde erfolgreich erstellt!", 
                               text_align=ft.TextAlign.CENTER),
                        ft.Text("Der Lead wurde an den Innendienst weitergeleitet.",
                               size=12, color="grey", text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, tight=True),
                    actions=[
                        ft.TextButton("OK", on_click=lambda e: self._after_save_success(success_dialog))
                    ]
                )
                self.page.show_dialog(success_dialog)
            else:
                raise Exception("Lead konnte nicht erstellt werden")
        
        except Exception as ex:
            print(f"[DEBUG] FEHLER in _save_lead: {ex}")
            import traceback
            traceback.print_exc()
            
            # Fehler-Dialog
            error_dialog = ft.AlertDialog(
                title=ft.Text("Fehler", color=ft.Colors.RED),
                content=ft.Text(f"Fehler beim Speichern: {str(ex)}"),
                actions=[ft.TextButton("OK", on_click=lambda e: self.page.pop_dialog())]
            )
            self.page.show_dialog(error_dialog)
    
    def _after_save_success(self, dialog):
        """Nach erfolgreichem Speichern: Dialog schließen und zurück zum Menü"""
        self.page.pop_dialog()
        self._reset_form()  # Formular zurücksetzen vor Rückkehr zum Menü
        self._go_back_to_menu()
    
    def _reset_form(self):
        """Setzt alle Formularfelder und Variablen zurück"""
        print("[DEBUG] Formular wird zurückgesetzt...")
        
        # Schritt zurücksetzen
        self.current_step = 1
        
        # Ausgewählte Werte zurücksetzen
        self.selected_firma = None
        self.selected_ansprechpartner = None
        self.selected_produktgruppe = None
        self.selected_produkt = None
        self.selected_zustand = None
        self.selected_quelle = None
        self.selected_bearbeiter = None
        
        # UI-Komponenten zurücksetzen (auf None setzen, damit sie beim nächsten render() neu erstellt werden)
        self.firma_dropdown = None
        self.ansprechpartner_dropdown = None
        self.produktgruppe_dropdown = None
        self.produkt_dropdown = None
        self.zustand_dropdown = None
        self.quelle_dropdown = None
        self.bearbeiter_dropdown = None
        self.beschreibung_field = None
        
        print("[DEBUG] Formular erfolgreich zurückgesetzt")
    
    def _go_back_to_menu(self):
        """Kehrt zum Hauptmenü zurück"""
        if self.app_controller:
            self.app_controller.show_main_app()