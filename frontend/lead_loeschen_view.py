import flet as ft
from api.api_client import LeadLoeschenClient


class LeadLoeschenView:
    """Ansicht zum Löschen von Leads mit Status-Filter"""
    
    def __init__(self, page: ft.Page, db=None, current_user: dict = None, app_controller=None):
        self.page = page
        self.db = db
        self.current_user = current_user
        self.app_controller = app_controller
        self.selected_leads = set()
        self.all_leads = []
        self.current_filter = "vorgemerkt"  # all, abgelehnt, vorgemerkt
        self.delete_button = None  # Referenz für den Löschen-Button
        
        # Manager initialisieren
        self.manager = LeadLoeschenClient()
    
    def render(self):
        """Zeigt die Lead-Löschungs-Ansicht"""
        self.page.clean()
        self.page.padding = 0
        
        # Synchronisiere Dark Mode mit page.theme_mode
        dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if dark_mode else "#f1f5f9"
        header_bg = "#0f172a" if dark_mode else "#ffffff"
        text_color = "white" if dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if dark_mode else "#64748b"
        text_tertiary = "#64748b" if dark_mode else "#94a3b8"
        tile_bg = "#1e293b" if dark_mode else "#ffffff"
        border_color = "#334155" if dark_mode else "#e2e8f0"
        
        self.page.bgcolor = None
        
        # Leads aus Datenbank laden
        self._load_leads()
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=text_color,
                    on_click=lambda e: self._go_back(),
                    tooltip="Zurück zum Admin-Menü"
                ),
                ft.Text("Leads löschen", size=24, color=text_color, weight=ft.FontWeight.BOLD),
            ], spacing=15),
            bgcolor=header_bg,
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
        )
        
        # Info-Text
        info_text = ft.Container(
            content=ft.Text(
                "Hier werden Leads angezeigt, die zum Löschen vorgemerkt wurden.",
                size=14,
                color=text_secondary,
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        )
        
        # Filter und Action-Buttons
        filter_section = ft.Container(
            content=ft.Row([
                # Filter Dropdown
                ft.Dropdown(
                    label="Filter nach Status",
                    value=self.current_filter,
                    options=[
                        ft.DropdownOption(key="all", text="Alle anzeigen"),
                        ft.DropdownOption(key="abgelehnt", text="Abgelehnt"),
                        ft.DropdownOption(key="vorgemerkt", text="vorgemerkt zum Löschen"),
                    ],
                    width=250,
                    on_select=self._on_filter_change,
                    bgcolor=tile_bg,
                    border_color=border_color,
                    color=text_color,
                    label_style=ft.TextStyle(color=text_secondary),
                ),
                ft.Container(expand=True),
                # Löschen-Button
            ]),
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
        )
        
        # Löschen-Button als Instanzvariable für spätere Updates
        self.delete_button = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_FOREVER, color="white", size=18),
                ft.Text("Auswahl endgültig löschen", color="white"),
            ], spacing=8),
            bgcolor="#dc2626",
            color="white",
            on_click=lambda e: self._delete_selected(),
            disabled=len(self.selected_leads) == 0,
        )
        
        # Filter-Sektion mit Button
        filter_section = ft.Container(
            content=ft.Row([
                # Filter Dropdown
                ft.Dropdown(
                    label="Filter nach Status",
                    value=self.current_filter,
                    options=[
                        ft.DropdownOption(key="all", text="Alle anzeigen"),
                        ft.DropdownOption(key="abgelehnt", text="Abgelehnt"),
                        ft.DropdownOption(key="vorgemerkt", text="Vorgemerkt zum Löschen"),
                    ],
                    width=250,
                    on_select=self._on_filter_change,
                    bgcolor=tile_bg,
                    border_color=border_color,
                    color=text_color,
                    label_style=ft.TextStyle(color=text_secondary),
                ),
                ft.Container(expand=True),
                self.delete_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
        )
        
        # Alle auswählen Checkbox
        # Prüfe ob alle gefilterten Leads bereits ausgewählt sind
        filtered_leads_for_check = self._filter_leads()
        all_selected = len(self.selected_leads) > 0 and len(self.selected_leads) == len(filtered_leads_for_check) if filtered_leads_for_check else False
        
        self.select_all_checkbox = ft.Checkbox(
            label="Alle auswählen",
            value=all_selected,
            on_change=self._toggle_select_all,
            label_style=ft.TextStyle(color=text_color),
        )
        
        select_all_section = ft.Container(
            content=self.select_all_checkbox,
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
        )
        
        # Lead-Liste
        self.lead_list_container = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self._render_lead_list(dark_mode, text_color, text_secondary, text_tertiary, tile_bg, border_color)
        
        lead_list_section = ft.Container(
            content=self.lead_list_container,
            padding=ft.padding.symmetric(horizontal=30, vertical=10),
            expand=True,
        )
        
        # Hauptcontainer
        main_content = ft.Column([
            header,
            info_text,
            filter_section,
            ft.Divider(height=1, color=border_color),
            select_all_section,
            lead_list_section,
        ], spacing=0, expand=True)
        
        self.page.add(main_content)
    
    def _load_leads(self):
        """Lädt Leads aus der Datenbank (über Manager)"""
        self.all_leads = self.manager.get_leads_for_deletion()
    
    def _render_lead_list(self, dark_mode, text_color, text_secondary, text_tertiary, tile_bg, border_color):
        """Rendert die Lead-Liste basierend auf Filter"""
        self.lead_list_container.controls.clear()
        
        # Filtere Leads
        filtered_leads = self._filter_leads()
        
        if not filtered_leads:
            # Keine Leads gefunden
            self.lead_list_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INBOX_OUTLINED, size=64, color=text_secondary),
                        ft.Text("Keine Leads gefunden", size=18, color=text_secondary),
                        ft.Text("Ändere die Filter-Einstellungen", size=14, color=text_tertiary),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=40,
                    alignment=ft.Alignment(0, 0),
                )
            )
        else:
            # Lead-Cards erstellen
            for lead in filtered_leads:
                card = self._create_lead_card(lead, dark_mode, text_color, text_secondary, text_tertiary, tile_bg, border_color)
                self.lead_list_container.controls.append(card)
        
        self.page.update()
    
    def _filter_leads(self):
        """Filtert Leads basierend auf ausgewähltem Filter"""
        if self.current_filter == "all":
            return self.all_leads
        elif self.current_filter == "abgelehnt":
            return [l for l in self.all_leads if l['status_id'] == 4]
        elif self.current_filter == "vorgemerkt":
            return [l for l in self.all_leads if l.get('ist_vorgemerkt', 0) == 1]
        return self.all_leads
    
    def _create_lead_card(self, lead, dark_mode, text_color, text_secondary, text_tertiary, tile_bg, border_color):
        """Erstellt eine Lead-Card"""
        lead_id = lead['lead_id']
        is_selected = lead_id in self.selected_leads
        
        # Status-Badge-Farben
        status_colors = {
            4: ("#7f1d1d", "Abgelehnt"),
            6: ("#1e3a8a", "Archiviert"),
        }
        
        # Prüfe ob vorgemerkt
        if lead.get('ist_vorgemerkt', 0) == 1:
            status_color = "#854d0e"
            status_text = "Vorgemerkt zum Löschen"
        else:
            status_color, status_text = status_colors.get(lead['status_id'], ("#475569", lead['status_name']))
        
        return ft.Container(
            content=ft.Row([
                # Checkbox
                ft.Checkbox(
                    value=is_selected,
                    on_change=lambda e, lid=lead_id: self._toggle_lead_selection(lid),
                ),
                # Lead-Info Icon
                ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, color=text_secondary, size=24),
                # Lead-Details
                ft.Column([
                    ft.Row([
                        ft.Text(
                            f"Lead #{lead_id} - {lead['firma_name']}",
                            size=16,
                            color=text_color,
                            weight=ft.FontWeight.W_600,
                        ),
                    ]),
                    ft.Row([
                        ft.Text(
                            f"{lead['produktgruppe']} | Status: ",
                            size=13,
                            color=text_secondary,
                        ),
                        ft.Container(
                            content=ft.Text(
                                status_text,
                                size=11,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=status_color,
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=4,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "Vorgemerkt zum Löschen" if lead['status_id'] == 7 else "",
                                size=11,
                                color="white",
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor="#854d0e",
                            padding=ft.padding.symmetric(horizontal=8, vertical=2),
                            border_radius=4,
                            visible=lead['status_id'] == 7,
                        ),
                    ], spacing=5),
                    ft.Text(
                        f"Erfasst von: {lead['erfasser']} | Datum: {lead['datum_erfasst']}",
                        size=12,
                        color=text_tertiary,
                    ),
                ], spacing=5, expand=True),
            ], spacing=15),
            bgcolor=tile_bg,
            padding=15,
            border_radius=8,
            border=ft.border.all(2, "#334155") if is_selected else ft.border.all(1, border_color),
        )
    
    def _toggle_lead_selection(self, lead_id):
        """Toggle Lead-Auswahl"""
        if lead_id in self.selected_leads:
            self.selected_leads.remove(lead_id)
        else:
            self.selected_leads.add(lead_id)
        
        # Aktualisiere Button-Status
        if self.delete_button:
            self.delete_button.disabled = len(self.selected_leads) == 0
        
        # Synchronisiere Dark Mode mit page.theme_mode
        dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        text_color = "white" if dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if dark_mode else "#64748b"
        text_tertiary = "#64748b" if dark_mode else "#94a3b8"
        tile_bg = "#1e293b" if dark_mode else "#ffffff"
        border_color = "#334155" if dark_mode else "#e2e8f0"
        
        # Update Select-All Checkbox
        filtered_leads = self._filter_leads()
        all_selected = len(self.selected_leads) == len(filtered_leads) and len(filtered_leads) > 0
        self.select_all_checkbox.value = all_selected
        
        self._render_lead_list(dark_mode, text_color, text_secondary, text_tertiary, tile_bg, border_color)
    
    def _toggle_select_all(self, e):
        """Alle Leads aus-/abwählen"""
        filtered_leads = self._filter_leads()
        
        if e.control.value:
            # Alle auswählen
            for lead in filtered_leads:
                self.selected_leads.add(lead['lead_id'])
        else:
            # Alle abwählen
            self.selected_leads.clear()
        
        # Aktualisiere Button-Status
        if self.delete_button:
            self.delete_button.disabled = len(self.selected_leads) == 0
        
        # Aktualisiere nur die Lead-Liste statt gesamte Seite neu zu rendern
        dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        text_color = "white" if dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if dark_mode else "#64748b"
        text_tertiary = "#64748b" if dark_mode else "#94a3b8"
        tile_bg = "#1e293b" if dark_mode else "#ffffff"
        border_color = "#334155" if dark_mode else "#e2e8f0"
        
        self._render_lead_list(dark_mode, text_color, text_secondary, text_tertiary, tile_bg, border_color)
    
    def _on_filter_change(self, e):
        """Filter wurde geändert"""
        self.current_filter = e.control.value
        self.selected_leads.clear()
        self.render()
    
    def _delete_selected(self):
        """Löscht ausgewählte Leads endgültig"""
        if not self.selected_leads:
            return
        
        def confirm_delete(e):
            # Leads über Manager löschen
            success, deleted_count, error_message = self.manager.delete_leads(list(self.selected_leads))
            
            self.page.pop_dialog()
            
            if success:
                self.selected_leads.clear()
                self._load_leads()
                self.render()
                
                # Erfolgs-Snackbar
                snack_bar = ft.SnackBar(
                    content=ft.Text(
                        f"{deleted_count} Lead(s) erfolgreich gelöscht",
                        color="white"
                    ),
                    bgcolor="#16a34a",
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
            else:
                # Fehler-Snackbar
                snack_bar = ft.SnackBar(
                    content=ft.Text(
                        error_message or "Fehler beim Löschen",
                        color="white"
                    ),
                    bgcolor="#dc2626",
                )
                self.page.snack_bar = snack_bar
                snack_bar.open = True
                self.page.update()
        
        def cancel_delete(e):
            self.page.pop_dialog()
            self.page.update()
        
        # Bestätigungsdialog mit Warnung
        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING, color="#dc2626", size=28),
                ft.Text("Leads endgültig löschen?", color="#dc2626"),
            ], spacing=10),
            content=ft.Column([
                ft.Text(
                    f"Sie sind dabei, {len(self.selected_leads)} Lead(s) endgültig zu löschen.",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(height=10),
                ft.Text(
                    "⚠️ Diese Aktion kann nicht rückgängig gemacht werden!",
                    color="#dc2626",
                    size=13,
                ),
                ft.Text(
                    "Alle zugehörigen Aktionen und Kommentare werden ebenfalls gelöscht.",
                    size=12,
                    color="grey",
                ),
            ], tight=True, spacing=5),
            actions=[
                ft.TextButton("Abbrechen", on_click=cancel_delete),
                ft.ElevatedButton(
                    "Endgültig löschen",
                    on_click=confirm_delete,
                    bgcolor="#dc2626",
                    color="white",
                ),
            ],
        )
        
        self.page.show_dialog(dialog)
    
    def _go_back(self):
        """Zurück zum Admin-Menü"""
        if self.app_controller:
            self.app_controller.show_admin_menu()