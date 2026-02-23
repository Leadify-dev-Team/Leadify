import flet as ft
from api.api_client import AdminMenuClient


class AdminMenuView:
    """Admin Hauptmenü mit moderner Kachelansicht"""
    
    def __init__(self, page: ft.Page, current_user: dict, app_controller=None):
        self.page = page
        self.current_user = current_user
        self.app_controller = app_controller
        self.account_menu = None
        self.dark_mode = True  # Standard: Dark Mode aktiv
        self.dark_mode_switch = None
        self.notification_badge = None
        self.notification_count = 0
        
        # Manager initialisieren
        self.manager = AdminMenuClient()
    
    def render(self):
        """Zeigt das Admin-Hauptmenü"""
        self.page.clean()
        self.page.padding = 0
        
        # Synchronisiere Dark Mode mit page.theme_mode
        self.dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if self.dark_mode else "#f1f5f9"
        header_bg = "#0f172a" if self.dark_mode else "#ffffff"
        text_color = "white" if self.dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if self.dark_mode else "#64748b"
        tile_bg = "#1e293b" if self.dark_mode else "#ffffff"
        
        self.page.bgcolor = None
        
        # Header mit Account-Button
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        icon_color=text_color,
                        icon_size=24,
                        on_click=self._show_drawer
                    ),
                    ft.Text("Leadify", size=20, color=text_color, weight=ft.FontWeight.BOLD),
                    ft.Container(width=20),
                    ft.Text("Administrator", size=16, color=text_secondary),
                ], spacing=10),
                ft.Row([
                    self._create_notification_button(text_color),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.ACCOUNT_CIRCLE,
                            icon_color="white",
                            icon_size=24,
                            on_click=self._show_account_menu
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
        
        # Anzahl ermitteln für Badges
        pending_leads_count = self._get_pending_leads_count()
        pending_users_count = self._get_pending_users_count()
        
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
                    text_color=text_color,
                    badge_count=pending_leads_count
                ),
                self._create_tile(
                    icon=ft.Icons.PERSON_ADD_OUTLINED,
                    title="Nutzer freigabe",
                    description="Neu registrierte Nutzer anzeigen und freigeben.",
                    color="#713f12",
                    on_click=lambda e: self._navigate_to_benutzerfreigabe(),
                    bg_color=tile_bg,
                    text_color=text_color,
                    badge_count=pending_users_count
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
    
    def _create_tile(self, icon, title, description, color, on_click, bg_color, text_color, badge_count=0):
        """Erstellt eine Admin-Kachel mit optionalem Badge"""
        # Icon-Container mit Badge
        icon_container = ft.Stack([
            ft.Container(
                content=ft.Icon(icon, color="white", size=32),
                bgcolor=color,
                width=64,
                height=64,
                border_radius=12,
                alignment=ft.Alignment(0, 0),
            ),
            # Badge nur anzeigen wenn count > 0
            ft.Container(
                content=ft.Container(
                    content=ft.Text(
                        str(badge_count),
                        size=11,
                        color="white",
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor="#ef4444",
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    border_radius=10,
                    alignment=ft.Alignment(0, 0),
                ),
                right=-5,
                top=-5,
                visible=badge_count > 0,
            ),
        ])
        
        return ft.Container(
            content=ft.Column([
                icon_container,
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
    
    async def _show_account_menu(self, e=None):
        """Zeigt das Account-Menü als Drawer rechts"""
        # Synchronisiere Dark Mode mit page.theme_mode
        self.dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if self.dark_mode else "#ffffff"
        header_bg = "#0f172a" if self.dark_mode else "#f8fafc"
        text_color = "white" if self.dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if self.dark_mode else "#64748b"
        icon_color = "#94a3b8" if self.dark_mode else "#475569"
        divider_color = "#334155" if self.dark_mode else "#e2e8f0"
        
        async def close_drawer(e):
            await self.page.close_end_drawer()
            self.page.update()
        
        async def toggle_dark_mode(e):
            # Wechsle page.theme_mode statt lokale dark_mode Variable
            new_theme = ft.ThemeMode.LIGHT if self.page.theme_mode == ft.ThemeMode.DARK else ft.ThemeMode.DARK
            self.page.theme_mode = new_theme
            self.page.update()
            await close_drawer(e)
            self.render()  # Neu rendern mit neuen Farben
        
        async def change_password(e):
            await close_drawer(e)
            self._show_placeholder("Passwort ändern")
        
        async def logout(e):
            await close_drawer(e)
            self._logout()
        
        # Dark Mode Switch erstellen
        self.dark_mode_switch = ft.Switch(
            value=self.dark_mode,
            on_change=toggle_dark_mode,
        )
        
        # Account-Menü als Drawer rechts
        self.account_menu = ft.NavigationDrawer(
            controls=[
                # Header mit Benutzerdaten
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Container(
                                content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=40, color=icon_color),
                                width=60,
                                height=60,
                                bgcolor="#e2e8f0" if not self.dark_mode else "#334155",
                                border_radius=30,
                                alignment=ft.Alignment(0, 0),
                            ),
                            ft.Column([
                                ft.Text(
                                    f"{self.current_user.get('vorname', '')} {self.current_user.get('nachname', '')}",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=text_color,
                                ),
                                ft.Text(
                                    self.current_user.get('email', 'ausendienst@leadify.com'),
                                    size=13,
                                    color=text_secondary,
                                ),
                            ], spacing=2),
                        ], spacing=15),
                    ]),
                    padding=20,
                    bgcolor=header_bg,
                ),
                
                ft.Divider(height=1, color=divider_color),
                
                # Dark Mode Toggle
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DARK_MODE_OUTLINED, size=20, color=icon_color),
                        ft.Text("Dark Mode", size=15, color=text_color),
                        self.dark_mode_switch,
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                ),
                
                ft.Divider(height=1, color=divider_color),
                
                # Passwort ändern
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOCK_OUTLINED, size=20, color=icon_color),
                        ft.Text("Passwort ändern", size=15, color=text_color),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    on_click=change_password,
                    ink=True,
                ),
                
                ft.Divider(height=1, color=divider_color),
                
                # Abmelden
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT, size=20, color=icon_color),
                        ft.Text("Abmelden", size=15, color=text_color),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    on_click=logout,
                    ink=True,
                ),
            ],
            bgcolor=bg_color,
        )
        
        self.page.end_drawer = self.account_menu
        await self.page.show_end_drawer()
        self.page.update()
    
    def _get_pending_leads_count(self):
        """Ermittelt die Anzahl der zum Löschen vorgemerkten Leads"""
        if self.manager:
            return self.manager.get_pending_leads_count()
        return 0
    
    def _get_pending_users_count(self):
        """Ermittelt die Anzahl der ausstehenden Benutzer zur Freigabe"""
        if self.manager:
            return self.manager.get_pending_users_count()
        return 0
    
    def _navigate_to_delete_leads(self):
        """Navigiert zur Lead-Löschung"""
        if self.app_controller:
            self.app_controller.show_delete_leads()
    
    def _navigate_to_benutzerfreigabe(self):
        """Navigiert zur Benutzerfreigabe"""
        if self.app_controller:
            self.app_controller.show_benutzerfreigabe()
    
    def _show_placeholder(self, feature_name):
        """Zeigt Placeholder für noch nicht implementierte Features"""
        def close_dialog(e):
            self.page.pop_dialog()
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Funktion in Entwicklung"),
            content=ft.Text(f"Die Funktion '{feature_name}' ist noch nicht implementiert."),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        self.page.show_dialog(dialog)
        self.page.update()
    
    async def _show_drawer(self, e=None):
        """Zeigt Navigation Drawer mit den Admin-Aktionen"""
        # Synchronisiere Dark Mode mit page.theme_mode
        self.dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if self.dark_mode else "#ffffff"
        header_bg = "#0f172a" if self.dark_mode else "#f8fafc"
        text_color = "white" if self.dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if self.dark_mode else "#64748b"
        icon_color = "#94a3b8" if self.dark_mode else "#475569"
        divider_color = "#334155" if self.dark_mode else "#e2e8f0"
        
        async def close_drawer(e):
            await self.page.close_drawer()
            self.page.update()
        
        def navigate_delete_leads(e):
            close_drawer(e)
            self._navigate_to_delete_leads()
        
        def navigate_benutzerfreigabe(e):
            close_drawer(e)
            self._navigate_to_benutzerfreigabe()
        
        # Navigation Drawer erstellen
        drawer = ft.NavigationDrawer(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Leadify",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=text_color,
                        ),
                        ft.Text(
                            "Administrator",
                            size=13,
                            color=text_secondary,
                        ),
                    ]),
                    padding=20,
                    bgcolor=header_bg,
                ),
                
                ft.Divider(height=1, color=divider_color),
                
                # Leads löschen
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DELETE_OUTLINE, size=20, color=icon_color),
                        ft.Text("Leads löschen", size=15, color=text_color),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    on_click=navigate_delete_leads,
                    ink=True,
                ),
                
                ft.Divider(height=1, color=divider_color),
                
                # Nutzer freigabe
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=20, color=icon_color),
                        ft.Text("Nutzer freigabe", size=15, color=text_color),
                    ], spacing=15),
                    padding=ft.padding.symmetric(horizontal=20, vertical=15),
                    on_click=navigate_benutzerfreigabe,
                    ink=True,
                ),
            ],
            bgcolor=bg_color,
        )
        
        self.page.drawer = drawer
        await self.page.show_drawer()
        self.page.update()
    
    def _logout(self):
        """Logout und zurück zur Anmeldung"""
        if self.app_controller:
            # Auth-Manager Logout aufrufen
            if hasattr(self.app_controller, 'auth'):
                self.app_controller.auth.logout()
            self.app_controller.start()
    
    def _get_notification_count(self):
        """Zählt die Benachrichtigungen (ausstehende Nutzer + Leads)"""
        if self.manager:
            return self.manager.get_notification_count()
        return 0
    
    def _create_notification_button(self, text_color):
        """Erstellt den Benachrichtigungs-Button mit Badge"""
        self.notification_count = self._get_notification_count()
        
        # Badge-Container
        badge = ft.Container(
            content=ft.Text(
                str(self.notification_count) if self.notification_count > 0 else "",
                size=10,
                color="white",
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor="#ef4444",
            width=20,
            height=20,
            border_radius=10,
            alignment=ft.Alignment(0, 0),
            visible=self.notification_count > 0,
        )
        
        self.notification_badge = badge
        
        return ft.Stack([
            ft.IconButton(
                icon=ft.Icons.EMAIL_OUTLINED,
                icon_color=text_color,
                icon_size=20,
                on_click=self._show_notification_menu,
            ),
            ft.Container(
                content=badge,
                right=0,
                top=0,
            ),
        ])
    
    async def _show_notification_menu(self, e=None):
        """Zeigt das Benachrichtigungs-Menü"""
        # Synchronisiere Dark Mode mit page.theme_mode
        self.dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        # Farben basierend auf Dark Mode
        bg_color = "#1a1f2e" if self.dark_mode else "#ffffff"
        header_bg = "#0f172a" if self.dark_mode else "#f8fafc"
        text_color = "white" if self.dark_mode else "#1e293b"
        text_secondary = "#94a3b8" if self.dark_mode else "#64748b"
        icon_color = "#94a3b8" if self.dark_mode else "#475569"
        divider_color = "#334155" if self.dark_mode else "#e2e8f0"
        tile_bg = "#1e293b" if self.dark_mode else "#f1f5f9"
        
        async def close_menu(e):
            await self.page.close_end_drawer()
            self.page.update()
        
        def navigate_benutzerfreigabe(e):
            close_menu(e)
            self._navigate_to_benutzerfreigabe()
        
        def navigate_delete_leads(e):
            close_menu(e)
            self._navigate_to_delete_leads()
        
        # Zähle ausstehende Nutzer über Manager
        pending_users = self._get_pending_users_count()
        
        # Zähle Leads zum Löschen über Manager
        pending_leads = self._get_pending_leads_count()
        
        notifications = []
        
        # Benachrichtigungen erstellen
        if pending_users > 0:
            notifications.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON_ADD_OUTLINED, size=24, color="#f59e0b"),
                        ft.Column([
                            ft.Text(f"{pending_users} Nutzer zur Freigabe", size=14, color=text_color, weight=ft.FontWeight.W_600),
                            ft.Text("Neue registrierte Nutzer warten auf Freigabe", size=12, color=text_secondary),
                        ], spacing=2, expand=True),
                    ], spacing=15),
                    padding=15,
                    bgcolor=tile_bg,
                    border_radius=8,
                    on_click=navigate_benutzerfreigabe,
                    ink=True,
                )
            )
        
        if pending_leads > 0:
            notifications.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DELETE_OUTLINE, size=24, color="#ef4444"),
                        ft.Column([
                            ft.Text(f"{pending_leads} Leads zum Löschen vorgemerkt", size=14, color=text_color, weight=ft.FontWeight.W_600),
                            ft.Text("Mitarbeiter haben Leads zum Löschen vorgemerkt", size=12, color=text_secondary),
                        ], spacing=2, expand=True),
                    ], spacing=15),
                    padding=15,
                    bgcolor=tile_bg,
                    border_radius=8,
                    on_click=navigate_delete_leads,
                    ink=True,
                )
            )
        
        if not notifications:
            notifications.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DONE_ALL, size=48, color=icon_color),
                        ft.Text("Keine Benachrichtigungen", size=16, color=text_color, weight=ft.FontWeight.W_600),
                        ft.Text("Alles ist auf dem neuesten Stand", size=13, color=text_secondary),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=30,
                    alignment=ft.Alignment(0, 0),
                )
            )
        
        # Benachrichtigungs-Menü als Drawer rechts
        notification_menu = ft.NavigationDrawer(
            controls=[
                # Header
                ft.Container(
                    content=ft.Column([
                        ft.Text(
                            "Benachrichtigungen",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=text_color,
                        ),
                        ft.Text(
                            f"{len([n for n in notifications if 'Benachrichtigungen' not in str(n.content)])} ausstehend",
                            size=12,
                            color=text_secondary,
                        ),
                    ]),
                    padding=20,
                    bgcolor=header_bg,
                ),
                
                ft.Divider(height=1, color=divider_color),
                
                # Benachrichtigungen
                ft.Container(
                    content=ft.Column(notifications, spacing=10),
                    padding=15,
                ),
            ],
            bgcolor=bg_color,
        )
        
        self.page.end_drawer = notification_menu
        await self.page.show_end_drawer()
        self.page.update()