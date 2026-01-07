import flet as ft


class AdminMenuView:
    """Admin Hauptmenü mit moderner Kachelansicht"""
    
    def __init__(self, page: ft.Page, current_user: dict, app_controller=None):
        self.page = page
        self.current_user = current_user
        self.app_controller = app_controller
    
    def render(self):
        """Zeigt das Admin-Hauptmenü"""
        self.page.clean()
        self.page.padding = 0
        self.page.bgcolor = "#1a1f2e"
        
        # Header mit Logout-Button
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color="white",
                        icon_size=24,
                        on_click=lambda e: self._show_drawer()
                    ),
                    ft.Text("Leadify", size=20, color="white", weight=ft.FontWeight.BOLD),
                    ft.Container(width=20),
                    ft.Text("Administrator", size=16, color="#64748b"),
                ], spacing=10),
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.EMAIL_OUTLINED,
                        icon_color="white",
                        icon_size=20,
                    ),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ACCOUNT_CIRCLE,
                            icon_color="white",
                            icon_size=24,
                            on_click=lambda e: self._logout()
                        ),
                        bgcolor="#3b82f6",
                        border_radius=20,
                        width=40,
                        height=40,
                    ),
                ], spacing=15),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            bgcolor="#0f172a",
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        )
        
        # Willkommenstext
        welcome_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Willkommen zu Leadify!",
                    size=32,
                    color="white",
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"Hallo {self.current_user.get('vorname', 'Administrator')}",
                    size=16,
                    color="#94a3b8",
                ),
                ft.Container(height=20),
                ft.Text(
                    "Was möchtest du heute tun?",
                    size=18,
                    color="white",
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
                    on_click=lambda e: self._navigate_to_delete_leads()
                ),
                self._create_tile(
                    icon=ft.Icons.ARCHIVE_OUTLINED,
                    title="Archivierte Leads verwalten",
                    description="Archivierte Leads anzeigen und wiederherstellen.",
                    color="#14532d",
                    on_click=lambda e: self._show_placeholder("Archivierte Leads")
                ),
                self._create_tile(
                    icon=ft.Icons.PERSON_ADD_OUTLINED,
                    title="Neue Nutzer zur Freigabe",
                    description="Neu registrierte Nutzer anzeigen und freigeben.",
                    color="#713f12",
                    on_click=lambda e: self._show_placeholder("Nutzerfreigabe")
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
    
    def _create_tile(self, icon, title, description, color, on_click):
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
                    color="white",
                    weight=ft.FontWeight.W_600,
                ),
                ft.Container(height=5),
                ft.Text(
                    description,
                    size=13,
                    color="#64748b",
                    max_lines=2,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.START),
            bgcolor="#1e293b",
            padding=25,
            border_radius=12,
            width=280,
            height=200,
            on_click=on_click,
            ink=True,
        )
    
    def _navigate_to_delete_leads(self):
        """Navigiert zur Lead-Löschung"""
        if self.app_controller:
            self.app_controller.show_delete_leads()
    
    def _show_placeholder(self, feature_name):
        """Zeigt Placeholder für noch nicht implementierte Features"""
        def close_dialog(e):
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Funktion in Entwicklung"),
            content=ft.Text(f"Die Funktion '{feature_name}' ist noch nicht implementiert."),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        self.page.open(dialog)
    
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