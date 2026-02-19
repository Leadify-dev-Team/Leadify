import flet as ft
from api.api_client import BenutzerfreigabeClient


class BenutzerfreigabeView:
    """Ansicht zur Freigabe neuer Benutzer"""
    
    def __init__(self, page: ft.Page, current_user: dict, db=None, app_controller=None):
        self.page = page
        self.current_user = current_user
        self.db = db
        self.app_controller = app_controller
        self.pending_users = []
        
        # Manager initialisieren
        self.manager = BenutzerfreigabeClient()
    
    def render(self):
        """Zeigt die Benutzerfreigabe-Ansicht"""
        self.page.clean()
        self.page.padding = 0
        
        # Synchronisiere Dark Mode mit page.theme_mode
        self.dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if self.dark_mode else "#f1f5f9"
        header_bg = "#0f172a" if self.dark_mode else "#ffffff"
        text_color = "white" if self.dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if self.dark_mode else "#64748b"
        table_bg = "#1e293b" if self.dark_mode else "#ffffff"
        row_hover = "#2d3748" if self.dark_mode else "#f8fafc"
        
        self.page.bgcolor = None
        
        # Header
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=text_color,
                        icon_size=24,
                        on_click=lambda e: self._navigate_back()
                    ),
                    ft.Text("Leadify", size=20, color=text_color, weight=ft.FontWeight.BOLD),
                    ft.Container(width=20),
                    ft.Text("Administrator", size=16, color=text_secondary),
                ], spacing=10),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        icon_color=text_color,
                        icon_size=20,
                        tooltip="Aktualisieren",
                        on_click=lambda e: self._load_pending_users()
                    ),
                ], spacing=15),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=header_bg,
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        )
        
        # Titel-Sektion
        title_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Neue Nutzer zur Freigabe",
                    size=28,
                    color=text_color,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Neu registrierte Mitarbeiter freigeben oder ablehnen",
                    size=14,
                    color=text_secondary,
                ),
            ], spacing=5),
            padding=ft.padding.only(left=30, right=30, top=30, bottom=20),
        )
        
        # Lade ausstehende Benutzer OHNE render zu callen
        self._load_pending_users_silent()
        
        # Tabellen-Container
        table_container = ft.Container(
            content=self._create_users_table(text_color, text_secondary, table_bg, row_hover),
            padding=ft.padding.symmetric(horizontal=30),
        )
        
        # Hauptcontainer
        main_content = ft.Column([
            header,
            title_section,
            table_container,
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        
        self.page.add(main_content)
    
    def _load_pending_users_silent(self):
        """Lädt alle Benutzer mit is_approved = 0 und Passwort + Token (ohne Neu-Rendern)"""
        self.pending_users = self.manager.get_pending_users()
    
    def _load_pending_users(self):
        """Lädt alle Benutzer mit is_approved = 0 und Passwort + Token und rendert die Seite neu"""
        self.pending_users = self.manager.get_pending_users()
        
        # Seite neu rendern um Änderungen zu zeigen
        if hasattr(self, 'page') and self.page:
            self.render()
    
    def _create_users_table(self, text_color, text_secondary, table_bg, row_hover):
        """Erstellt die Tabelle mit den ausstehenden Benutzern"""
        
        # Wenn keine Benutzer vorhanden sind
        if not self.pending_users:
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=64, color=text_secondary),
                    ft.Container(height=20),
                    ft.Text(
                        "Keine neuen Benutzer zur Freigabe",
                        size=18,
                        color=text_color,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        "Alle registrierten Benutzer wurden bereits bearbeitet.",
                        size=14,
                        color=text_secondary,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=ft.padding.all(60),
                alignment=ft.Alignment(0, 0),
                bgcolor=table_bg,
                border_radius=12,
            )
        
        # Tabellen-Header
        header_row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("NAME", size=12, color=text_color, weight=ft.FontWeight.W_600),
                    width=200,
                ),
                ft.Container(
                    content=ft.Text("EMAIL", size=12, color=text_color, weight=ft.FontWeight.W_600),
                    width=250,
                ),
                ft.Container(
                    content=ft.Text("ROLLE", size=12, color=text_color, weight=ft.FontWeight.W_600),
                    width=150,
                ),
                ft.Container(
                    content=ft.Text("AKTION", size=12, color=text_color, weight=ft.FontWeight.W_600),
                    expand=True,
                    alignment=ft.Alignment(1, 0),
                ),
            ], spacing=20),
            padding=ft.padding.symmetric(horizontal=25, vertical=15),
            bgcolor=table_bg,
        )
        
        # Tabellen-Zeilen
        rows = []
        for user in self.pending_users:
            user_id = user.get('benutzer_id')
            vorname = user.get('vorname', '')
            nachname = user.get('nachname', '')
            email = user.get('email', '')
            rolle_id = user.get('rolle_id', '')
            
            # Rolle Name mappen
            rolle_map = {0: 'Admin', 1: 'Außendienst', 2: 'Innendienst', 3: 'Berichtsersteller', 4: 'Auswertung'}
            rolle = rolle_map.get(rolle_id, f'Rolle {rolle_id}')
            
            row = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(
                            f"{vorname} {nachname}",
                            size=14,
                            color=text_color,
                        ),
                        width=200,
                    ),
                    ft.Container(
                        content=ft.Text(
                            email,
                            size=14,
                            color=text_secondary,
                        ),
                        width=250,
                    ),
                    ft.Container(
                        content=ft.Text(
                            rolle,
                            size=14,
                            color=text_secondary,
                        ),
                        width=150,
                    ),
                    ft.Container(
                        content=ft.Row([
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CHECK, size=16),
                                    ft.Text("Freigeben", size=13),
                                ], spacing=5),
                                bgcolor="#10b981",
                                color="white",
                                height=36,
                                on_click=lambda e, uid=user_id: self._approve_user(uid),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.CLOSE, size=16),
                                    ft.Text("Ablehnen", size=13),
                                ], spacing=5),
                                bgcolor="#ef4444",
                                color="white",
                                height=36,
                                on_click=lambda e, uid=user_id: self._reject_user(uid),
                            ),
                        ], spacing=10, alignment=ft.MainAxisAlignment.END),
                        expand=True,
                    ),
                ], spacing=20),
                padding=ft.padding.symmetric(horizontal=25, vertical=15),
                bgcolor=table_bg,
                border=ft.border.only(
                    bottom=ft.BorderSide(1, "#334155" if self.dark_mode else "#e2e8f0")
                ),
            )
            rows.append(row)
        
        # Tabellen-Container mit Header und Zeilen
        table = ft.Container(
            content=ft.Column([
                header_row,
                ft.Divider(height=1, color="#334155" if self.dark_mode else "#e2e8f0"),
                ft.Column(rows, spacing=0),
            ], spacing=0),
            bgcolor=table_bg,
            border_radius=12,
            border=ft.border.all(1, "#334155" if self.dark_mode else "#e2e8f0"),
        )
        
        return table
    
    def _approve_user(self, user_id):
        """Genehmigt einen Benutzer (über Manager)"""
        success = self.manager.approve_user(user_id)
        
        if success:
            # Erfolgs-Snackbar
            snackbar = ft.SnackBar(
                content=ft.Text("Benutzer erfolgreich freigegeben!"),
                bgcolor="#10b981",
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
            
            # Liste neu laden
            self._load_pending_users()
        else:
            snackbar = ft.SnackBar(
                content=ft.Text("Fehler beim Freigeben des Benutzers."),
                bgcolor="#ef4444",
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
    
    def _reject_user(self, user_id):
        """Zeigt Bestätigungsdialog und löscht den Benutzer bei Bestätigung"""
        def confirm_reject(e):
            self.page.pop_dialog()
            success = self.manager.reject_user(user_id)
            
            if success:
                # Erfolgs-Snackbar
                snackbar = ft.SnackBar(
                    content=ft.Text("Benutzer wurde abgelehnt und gelöscht."),
                    bgcolor="#ef4444",
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
                
                # Liste neu laden
                self._load_pending_users()
            else:
                snackbar = ft.SnackBar(
                    content=ft.Text("Fehler beim Ablehnen des Benutzers."),
                    bgcolor="#ef4444",
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
        
        def cancel_reject(e):
            self.page.pop_dialog()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Benutzer ablehnen?"),
            content=ft.Text(
                "Möchten Sie diesen Benutzer wirklich ablehnen? "
                "Der Benutzer wird dauerhaft aus der Datenbank gelöscht."
            ),
            actions=[
                ft.TextButton("Abbrechen", on_click=cancel_reject),
                ft.TextButton("Ablehnen", on_click=confirm_reject, style=ft.ButtonStyle(
                    color={"": "#ef4444"}
                )),
            ],
        )
        
        self.page.show_dialog(dialog)
        self.page.update()
    
    def _navigate_back(self):
        """Navigiert zurück zum Admin-Menü"""
        if self.app_controller:
            self.app_controller.show_admin_menu()