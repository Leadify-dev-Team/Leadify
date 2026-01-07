import flet as ft


class AdminMenuView:
    """Admin Hauptmenü mit moderner Kachelansicht"""
    
    def __init__(self, page: ft.Page, current_user: dict, app_controller=None):
        self.page = page
        self.current_user = current_user
        self.app_controller = app_controller
        self.account_menu = None
        self.dark_mode = True  # Standard: Dark Mode aktiv
        self.dark_mode_switch = None
    
    def render(self):
        """Zeigt das Admin-Hauptmenü"""
        self.page.clean()
        self.page.padding = 0
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if self.dark_mode else "#f1f5f9"
        header_bg = "#0f172a" if self.dark_mode else "#ffffff"
        text_color = "white" if self.dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if self.dark_mode else "#64748b"
        tile_bg = "#1e293b" if self.dark_mode else "#ffffff"
        
        self.page.bgcolor = bg_color
        
        # Header mit Account-Button
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=text_color,
                        icon_size=24,
                        on_click=lambda e: self._show_drawer()
                    ),
                    ft.Text("Leadify", size=20, color=text_color, weight=ft.FontWeight.BOLD),
                    ft.Container(width=20),
                    ft.Text("Administrator", size=16, color=text_secondary),
                ], spacing=10),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EMAIL_OUTLINED,
                        icon_color=text_color,
                        icon_size=20,
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ACCOUNT_CIRCLE,
                            icon_color="white",
                            icon_size=24,
                            on_click=lambda e: self._show_account_menu(e)
                        ),
                        bgcolor="#3b82f6",
                        border_radius=20,
                        width=40,
                        height=40,
                    ),
                ], spacing=15),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor=header_bg,
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        )
        
        # Willkommenstext
        welcome_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Willkommen zu Leadify!",
                    size=32,
                    color=text_color,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"Hallo {self.current_user.get('vorname', 'Administrator')}",
                    size=16,
                    color=text_secondary,
                ),
                ft.Container(height=20),
                ft.Text(
                    "Was möchtest du heute tun?",
                    size=18,
                    color=text_color,
                    weight=ft.FontWeight.W_500,
                ),
            ], spacing=5),
            padding=ft.padding.only(left=30, right=30, top=40, bottom=30),
        )
        
        # Admin-Kacheln
        tiles_section = ft.Container(
            content=ft.Row([
                self._create_tile(
                    icon=ft.Icons.DELETE_OUTLINE,
                    title="Leads löschen",
                    description="Leads dauerhaft und unwiderruflich löschen.",
                    color="#7f1d1d",
                    on_click=lambda e: self._navigate_to_delete_leads(),
                    bg_color=tile_bg,
                    text_color=text_color
                ),
                self._create_tile(
                    icon=ft.Icons.ARCHIVE_OUTLINED,
                    title="Archivierte Leads verwalten",
                    description="Archivierte Leads anzeigen und wiederherstellen.",
                    color="#14532d",
                    on_click=lambda e: self._show_placeholder("Archivierte Leads"),
                    bg_color=tile_bg,
                    text_color=text_color
                ),
                self._create_tile(
                    icon=ft.Icons.PERSON_ADD_OUTLINED,
                    title="Neue Nutzer zur Freigabe",
                    description="Neu registrierte Nutzer anzeigen und freigeben.",
                    color="#713f12",
                    on_click=lambda e: self._show_placeholder("Nutzerfreigabe"),
                    bg_color=tile_bg,
                    text_color=text_color
                ),
            ], spacing=20, wrap=True),
            padding=ft.padding.symmetric(horizontal=30),
        )
        
        # Hauptcontainer
        main_content = ft.Column([
            header,
            welcome_section,
            tiles_section,
        ], spacing=0, expand=True, scroll=ft.ScrollMode.AUTO)
        
        self.page.add(main_content)
    
    def _create_tile(self, icon, title, description, color, on_click, bg_color, text_color):
        """Erstellt eine Admin-Kachel"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Icon(icon, color="white", size=32),
                    bgcolor=color,
                    width=64,
                    height=64,
                    border_radius=12,
                    alignment=ft.alignment.center,
                ),
                ft.Container(height=15),
                ft.Text(
                    title,
                    size=16,
                    color=text_color,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(height=8),
                ft.Text(
                    description,
                    size=13,
                    color="#64748b",
                    max_lines=3,
                    overflow=ft.TextOverflow.VISIBLE,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.START),
            bgcolor=bg_color,
            padding=25,
            border_radius=12,
            width=320,
            height=220,
            on_click=on_click,
            ink=True,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.1, "#000000"),
                offset=ft.Offset(0, 4),
            ) if not self.dark_mode else None,
        )
    
    def _show_account_menu(self, e):
        """Zeigt das Account-Menü als Drawer rechts"""
        def close_drawer(e):
            self.page.close(self.account_menu)
            self.page.update()
        
        def toggle_dark_mode(e):
            self.dark_mode = not self.dark_mode
            if self.dark_mode_switch:
                self.dark_mode_switch.value = self.dark_mode
            close_drawer(e)
            self.render()  # Neu rendern mit neuen Farben
        
        def change_password(e):
            close_drawer(e)
            self._show_placeholder("Passwort ändern")
        
        def logout(e):
            close_drawer(e)
            self._logout()
        
        # Dark Mode Switch erstellen
        self.dark_mode_switch = ft.Switch(
            value=self.dark_mode,
            on_change=toggle_dark_mode,
        )
        
        # Account-Menü als Drawer rechts
        self.account_menu = ft.NavigationDrawer(
            position=ft.NavigationDrawerPosition.END,  # Rechts öffnen
            controls=[
                # Header mit Benutzerdaten
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=40, color="#475569"),
                                width=60,
                                height=60,
                                bgcolor="#e2e8f0",
                                border_radius=30,
                                alignment=ft.alignment.center,
                            ),
                            ft.Column([
                                ft.Text(
                                    f"{self.current_user.get('vorname', '')} {self.current_user.get('nachname', '')}",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color="#1e293b",
                                ),
                                ft.Text(
                                    self.current_user.get('email', 'ausendienst@leadify.com'),
                                    size=13,
                                    color="#64748b",
                                ),
                            ], spacing=2),
                        ], spacing=15),
                    ]),
                    padding=20,
                    bgcolor="#f8fafc",
                ),
                
                ft.Divider(height=1, color="#e2e8f0"),
                
                # Dark Mode Toggle
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DARK_MODE_OUTLINED, size=20, color="#475569"),
                        ft.Text("Dark Mode", size=15, color="#1e293b"),
                        self.dark_mode_switch,
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                ),
                
                ft.Divider(height=1, color="#e2e8f0"),
                
                # Passwort ändern
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK_OUTLINED, size=20, color="#475569"),
                        ft.Text("Passwort ändern", size=15, color="#1e293b"),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    on_click=change_password,
                    ink=True,
                ),
                
                ft.Divider(height=1, color="#e2e8f0"),
                
                # Abmelden
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT, size=20, color="#475569"),
                        ft.Text("Abmelden", size=15, color="#1e293b"),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    on_click=logout,
                    ink=True,
                ),
            ],
            bgcolor="white",
        )
        
        self.page.open(self.account_menu)
        self.page.update()
    
    def _navigate_to_delete_leads(self):
        """Navigiert zur Lead-Löschung"""
        if self.app_controller:
            self.app_controller.show_delete_leads()
    
    def _show_placeholder(self, feature_name):
        """Zeigt Placeholder für noch nicht implementierte Features"""
        def close_dialog(e):
            self.page.close(dialog)
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Funktion in Entwicklung"),
            content=ft.Text(f"Die Funktion '{feature_name}' ist noch nicht implementiert."),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        self.page.open(dialog)
        self.page.update()
    
    def _show_drawer(self):
        """Zeigt Navigation Drawer (optional für später)"""
        pass
    
    def _logout(self):
        """Logout und zurück zur Anmeldung"""
        if self.app_controller:
            # Auth-Manager Logout aufrufen
            if hasattr(self.app_controller, 'auth'):
                self.app_controller.auth.logout()
            self.app_controller.start()