import flet as ft
from db_config import db_host,db_user,db_password,db_port,db_database
import database
from auth_manager import AuthManager
from lead_bearbeitung import LeadBearbeitungManager, LeadBearbeitungView
import json
from pathlib import Path

# ========== NEU: Außendienst-Imports ==========
from Außendienst import AussendienstManager
from aussendienst_view import AussendienstView
# ==============================================

# ========== Admin-Imports ==========
from admin_menu import AdminMenuView
from lead_loeschen import LeadLoeschenView
# ====================================

# ========== Auswertungs-Imports ==========
from auswertung import AuswertungManager, AuswertungView
# =========================================

# ========== Lead-Status-Imports ==========
from lead_status import LeadStatusManager, LeadStatusView
# ==========================================


class AppController:
    """Hauptsteuerung der Anwendung - verwaltet Navigation und Benutzer-Status"""
    
    def __init__(self, page: ft.Page, db: database.Database):
        self.page = page
        self.db = db
        self.auth = AuthManager(db)
        self.current_user = None
        self.lead_bearbeitung_view = None  # Speichere Lead-View für persistente Filter
        
        # ========== NEU: Außendienst-Manager ==========
        self.aussendienst_manager = AussendienstManager(db)
        self.aussendienst_view = None  # Speichere Außendienst-View
        # ==============================================
        
        # ========== Auswertungs-Manager ==========
        self.auswertung_manager = AuswertungManager(db)
        self.auswertung_view = None  # Speichere Auswertungs-View
        # ==========================================
        
        # ========== Lead-Status-Manager ==========
        self.lead_status_manager = LeadStatusManager(db)
        self.lead_status_view = None  # Speichere Lead-Status-View
        # ========================================
        
        # Page-Konfiguration
        self.page.title = "Leadify"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
        
        # Theme laden und anwenden
        self._load_theme()
    
    def _load_theme(self):
        """Lädt gespeichertes Theme aus Datei"""
        theme_file = Path.home() / ".leadify_theme.json"
        try:
            if theme_file.exists():
                with open(theme_file, 'r') as f:
                    theme_data = json.load(f)
                    is_dark = theme_data.get('dark_mode', False)
                    self.page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
            else:
                # Standard: Light Mode
                self.page.theme_mode = ft.ThemeMode.LIGHT
        except:
            self.page.theme_mode = ft.ThemeMode.LIGHT
    
    def _save_theme(self, is_dark: bool):
        """Speichert Theme-Präferenz"""
        theme_file = Path.home() / ".leadify_theme.json"
        try:
            with open(theme_file, 'w') as f:
                json.dump({'dark_mode': is_dark}, f)
        except Exception as e:
            print(f"Fehler beim Speichern des Themes: {e}")
    
    def _toggle_theme(self, e):
        """Wechselt zwischen Dark und Light Mode"""
        is_dark = e.control.value
        self.page.theme_mode = ft.ThemeMode.DARK if is_dark else ft.ThemeMode.LIGHT
        self._save_theme(is_dark)
        self.page.update()
    
    def start(self):
        """Startet die Anwendung und prüft Auto-Login"""
        is_logged_in, user_data, message = self.auth.check_auto_login()
        
        if is_logged_in:
            self.current_user = user_data
            self.show_main_app()
        elif "Warte noch auf Admin-Freigabe" in message:
            self.show_pending_approval()
        else:
            self.show_login_screen()
    
    def show_main_app(self):
        """Zeigt das Hauptmenü nach erfolgreichem Login"""
        # Rollenüberprüfung: Admin (rolle_id = 0) zum Admin-Menü weiterleiten
        if self.current_user and self.current_user.get('rolle_id') == 0:
            self.show_admin_menu()
            return
        
        # Rollenüberprüfung: Auswertungs-Benutzer (rolle_id = 4) direkt zur Auswertung
        if self.current_user and self.current_user.get('rolle_id') == 4:
            self.show_auswertung_menu()
            return
        
        self.page.clean()
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        self.page.horizontal_alignment = ft.CrossAxisAlignment.START
        
        # NEU: Prüfe Anzahl neuer Leads für Badge
        anzahl_neue_leads = 0
        if self.current_user.get('rolle_id') in [1, 2]:
            lead_manager = LeadBearbeitungManager(self.db)
            anzahl_neue_leads = lead_manager.count_neue_leads(self.current_user['benutzer_id'])
        
        # Hamburger Menü
        menu_controls = [
            ft.Container(height=10),
            ft.ListTile(
                title=ft.Text(f"Willkommen, {self.current_user.get('vorname', 'Benutzer')}!"),
                subtitle=ft.Text(self.current_user.get('email', '')),
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.INBOX),
                title=ft.Text("Meine Nachrichten"),
                trailing=ft.Container(
                    content=ft.Text(
                        str(anzahl_neue_leads),
                        color="white",
                        size=12,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor="orange" if anzahl_neue_leads > 0 else "transparent",
                    width=24,
                    height=24,
                    border_radius=12,
                    alignment=ft.alignment.center,
                    visible=anzahl_neue_leads > 0
                ),
                on_click=lambda e: self._show_leads()
            ),

            ft.ListTile(
                leading=ft.Icon(ft.Icons.ASSIGNMENT),
                title=ft.Text("Gesendete Leads"),
                on_click=lambda e: self._show_lead_status()
            ),

            ft.ListTile(
                leading=ft.Icon(ft.Icons.ADD_CIRCLE),
                title=ft.Text("Lead erstellen"),
                on_click=lambda e: self._show_create_lead()
            ),
            
        ]
        
        # Auswertungs-Option nur für rolle_id = 4 anzeigen
        if self.current_user and self.current_user.get('rolle_id') == 4:
            menu_controls.extend([
                ft.Divider(),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ANALYTICS),
                    title=ft.Text("Auswertung"),
                    on_click=lambda e: self._show_auswertung()
                ),
            ])
        
        menu_controls.extend([
            ft.Divider(),
        ])
        
        menu_drawer = ft.NavigationDrawer(controls=menu_controls)
        
        self.page.drawer = menu_drawer
        
        # Profil-Drawer (rechts) mit Abmelden und Passwort ändern
        # Theme-Switch basierend auf aktuellem Modus
        is_dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        profile_controls = [
            ft.Container(height=10),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=40),
                title=ft.Text(f"{self.current_user.get('vorname', '')} {self.current_user.get('nachname', '')}", 
                             weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(self.current_user.get('email', '')),
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DARK_MODE),
                title=ft.Text("Dark Mode"),
                trailing=ft.Switch(
                    value=is_dark_mode,
                    on_change=self._toggle_theme
                )
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOCK),
                title=ft.Text("Passwort ändern"),
                on_click=lambda e: self._show_change_password()
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT),
                title=ft.Text("Abmelden"),
                on_click=self._handle_logout
            ),
        ]
        
        profile_drawer = ft.NavigationDrawer(controls=profile_controls)
        self.page.end_drawer = profile_drawer
        
        # Willkommensbildschirm
        username = self.current_user.get('vorname') or self.current_user.get('email')
        
        self.page.add(
            ft.Container(
                content=ft.Column([
                    # Header mit Hamburger-Button
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.MENU,
                            icon_size=30,
                            on_click=lambda e: self._toggle_drawer()
                        ),
                        ft.Text("Leadify", size=24, weight=ft.FontWeight.BOLD, expand=True),
                        ft.IconButton(
                            icon=ft.Icons.ACCOUNT_CIRCLE,
                            icon_size=30,
                            on_click=lambda e: self._toggle_profile_drawer(),
                            tooltip="Profil"
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    
                    ft.Divider(),
                    
                    # Willkommenstext
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Willkommen zu Leadify!", size=28, weight=ft.FontWeight.BOLD),
                            ft.Text(f"Hallo {username}", size=18, color="grey"),
                            ft.Divider(height=40, color="transparent"),
                            ft.Text("Was möchtest du heute tun?", size=16, weight=ft.FontWeight.W_500),
                        ], spacing=10),
                        padding=20
                    ),
                    
                    ft.Divider(height=20, color="transparent"),
                    
                    # Schnellzugriff-Buttons - dynamisch je nach Rolle
                    self._create_quick_access_buttons(),
                ], expand=True),
                padding=20
            )
        )
    
    def _toggle_drawer(self):
        """Öffnet/Schließt das Hamburger-Menü"""
        self.page.drawer.open = not self.page.drawer.open
        self.page.update()
    
    def _toggle_profile_drawer(self):
        """Öffnet/Schließt das Profil-Menü"""
        self.page.end_drawer.open = not self.page.end_drawer.open
        self.page.update()
    
    def _show_change_password(self):
        """Zeigt Dialog zum Ändern des Passworts"""
        self.page.end_drawer.open = False
        self.page.update()
        
        # Eingabefelder
        old_password_field = ft.TextField(
            label="Altes Passwort",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        new_password_field = ft.TextField(
            label="Neues Passwort",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        confirm_password_field = ft.TextField(
            label="Neues Passwort bestätigen",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        status_text = ft.Text("", color="red", size=12)
        
        def change_password_clicked(e):
            # Validierung
            if not old_password_field.value or not new_password_field.value or not confirm_password_field.value:
                status_text.value = "Bitte fülle alle Felder aus"
                status_text.color = "red"
                self.page.update()
                return
            
            if new_password_field.value != confirm_password_field.value:
                status_text.value = "Neue Passwörter stimmen nicht überein"
                status_text.color = "red"
                self.page.update()
                return
            
            if len(new_password_field.value) < 8:
                status_text.value = "Passwort muss mindestens 8 Zeichen lang sein"
                status_text.color = "red"
                self.page.update()
                return
            
            # Passwort ändern
            success, message = self.auth.change_password(
                self.current_user['benutzer_id'],
                old_password_field.value,
                new_password_field.value
            )
            
            if success:
                self.page.close(password_dialog)
                
                def logout_after_success(e):
                    self.page.close(success_dialog)
                    self._handle_logout(e)
                
                success_dialog = ft.AlertDialog(
                    title=ft.Text("Erfolg", color=ft.Colors.GREEN),
                    content=ft.Text("Passwort wurde erfolgreich geändert! Du wirst jetzt abgemeldet."),
                    actions=[ft.TextButton("OK", on_click=logout_after_success)]
                )
                self.page.open(success_dialog)
            else:
                status_text.value = message
                status_text.color = "red"
                self.page.update()
        
        password_dialog = ft.AlertDialog(
            title=ft.Text("Passwort ändern"),
            content=ft.Container(
                content=ft.Column([
                    old_password_field,
                    new_password_field,
                    confirm_password_field,
                    status_text
                ], tight=True, spacing=15),
                width=350
            ),
            actions=[
                ft.TextButton("Abbrechen", on_click=lambda e: self.page.close(password_dialog)),
                ft.ElevatedButton("Passwort ändern", on_click=change_password_clicked)
            ]
        )
        
        self.page.open(password_dialog)
    
    def _create_quick_access_buttons(self):
        """Erstellt Schnellzugriff-Buttons basierend auf Benutzerrolle"""
        
        # NEU: Prüfe Anzahl neuer Leads für Badge
        anzahl_neue_leads = 0
        if self.current_user.get('rolle_id') in [1, 2]:
            lead_manager = LeadBearbeitungManager(self.db)
            anzahl_neue_leads = lead_manager.count_neue_leads(self.current_user['benutzer_id'])
        
        # Button-Inhalt für "Meine Nachrichten" mit Badge
        nachrichten_content = ft.Stack([
            ft.Column([
                ft.Icon(ft.Icons.INBOX, size=40),
                ft.Text("Meine Nachrichten", size=16, weight=ft.FontWeight.W_500),
                ft.Text("Bearbeite deine Leads", size=12, color="grey")
            ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ])
        
        # Füge Badge hinzu, wenn neue Leads vorhanden
        if anzahl_neue_leads > 0:
            nachrichten_content.controls.append(
                ft.Container(
                    content=ft.Text(
                        str(anzahl_neue_leads),
                        color="white",
                        size=12,
                        weight=ft.FontWeight.BOLD
                    ),
                    bgcolor="orange",
                    width=28,
                    height=28,
                    border_radius=14,
                    alignment=ft.alignment.center,
                    right=10,
                    top=10,
                )
            )
        
        buttons = [
            ft.ElevatedButton(
                content=nachrichten_content,
                width=300,
                height=120,
                on_click=lambda e: self._show_leads()
            ),
            ft.ElevatedButton(
                content=ft.Column([
                    ft.Icon(ft.Icons.ADD_CIRCLE, size=40),
                    ft.Text("Lead erstellen", size=16, weight=ft.FontWeight.W_500),
                    ft.Text("Neuen Lead hinzufügen", size=12, color="grey")
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=300,
                height=120,
                on_click=lambda e: self._show_create_lead()
            ),
            ft.ElevatedButton(
                content=ft.Column([
                    ft.Icon(ft.Icons.ASSIGNMENT, size=40),
                    ft.Text("Meine Leads", size=16, weight=ft.FontWeight.W_500),
                    ft.Text("Status einsehen", size=12, color="grey")
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=300,
                height=120,
                on_click=lambda e: self._show_lead_status()
            ),
        ]
        
        # Auswertungs-Button nur für rolle_id = 4 hinzufügen
        if self.current_user and self.current_user.get('rolle_id') == 4:
            buttons.append(
                ft.ElevatedButton(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ANALYTICS, size=40),
                        ft.Text("Auswertung", size=16, weight=ft.FontWeight.W_500),
                        ft.Text("Alle Leads anzeigen", size=12, color="grey")
                    ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=300,
                    height=120,
                    on_click=lambda e: self._show_auswertung(),
                    bgcolor="#3b82f6",
                    color="white",
                )
            )
        
        return ft.Column(buttons, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    def _show_leads(self):
        """Zeigt die Lead-Bearbeitung UI"""
        self.page.drawer.open = False
        self.page.update()
        
        self.page.clean()
        
        # Lead-Bearbeitung Manager initialisieren
        lead_manager = LeadBearbeitungManager(self.db)
        
        # Erstelle die View nur beim ersten Mal, danach wiederverwenden
        if self.lead_bearbeitung_view is None:
            self.lead_bearbeitung_view = LeadBearbeitungView(self.page, lead_manager, self.current_user)
            self.lead_bearbeitung_view.app_controller = self  # Referenz zum Controller für Navigation
        else:
            # Update Manager, Page und current_user
            self.lead_bearbeitung_view.lead_manager = lead_manager
            self.lead_bearbeitung_view.page = self.page
            self.lead_bearbeitung_view.current_user = self.current_user
        
        self.lead_bearbeitung_view.render()
    
    # ========== NEU: Außendienst-Methode (ersetzt Placeholder) ==========
    def _show_create_lead(self):
        """Zeigt Außendienst-Ansicht für Lead-Erstellung"""
        self.page.drawer.open = False
        self.page.update()
        
        self.page.clean()
        
        # Erstelle die View nur beim ersten Mal, danach wiederverwenden
        if self.aussendienst_view is None:
            self.aussendienst_view = AussendienstView(
                self.page, 
                self.aussendienst_manager, 
                self.current_user
            )
            self.aussendienst_view.app_controller = self  # Referenz zum Controller für Navigation
        else:
            # Update Manager, Page und current_user
            self.aussendienst_view.manager = self.aussendienst_manager
            self.aussendienst_view.page = self.page
            self.aussendienst_view.current_user = self.current_user
            # Setze Schritt auf 1 zurück für neuen Lead
            self.aussendienst_view.current_step = 1
        
        self.aussendienst_view.render()
    # ====================================================================
    
    # ========== NEU: Lead-Status-Methode ==========
    def _show_lead_status(self):
        """Zeigt Status aller von diesem Benutzer erstellten Leads"""
        self.page.drawer.open = False
        self.page.update()
        
        self.page.clean()
        
        # Erstelle die View nur beim ersten Mal, danach wiederverwenden
        if self.lead_status_view is None:
            self.lead_status_view = LeadStatusView(
                self.page,
                self.lead_status_manager,
                self.current_user
            )
            self.lead_status_view.app_controller = self  # Referenz zum Controller für Navigation
        else:
            # Update Manager, Page und current_user
            self.lead_status_view.lead_manager = self.lead_status_manager
            self.lead_status_view.page = self.page
            self.lead_status_view.current_user = self.current_user
        
        self.lead_status_view.render()
    # ==============================================

    
    def show_pending_approval(self):
        """Zeigt Wartebildschirm für Admin-Freigabe"""
        self.page.clean()
        
        def check_approval(e):
            is_logged_in, user_data, message = self.auth.check_auto_login()
            if is_logged_in:
                self.current_user = user_data
                self.show_main_app()
            else:
                status_text.value = message
                self.page.update()
        
        status_text = ft.Text(
            "Deine Registrierung wird noch geprüft.\nBitte warte auf die Freigabe durch einen Administrator.",
            text_align=ft.TextAlign.CENTER
        )
        
        self.page.add(
            ft.Column([
                ft.Icon(ft.Icons.HOURGLASS_EMPTY, size=64, color="orange"),
                status_text,
                ft.Divider(height=20, color="transparent"),
                ft.ElevatedButton(
                    "Status aktualisieren",
                    icon=ft.Icons.REFRESH,
                    on_click=check_approval
                ),
                ft.TextButton(
                    "Zur Anmeldung",
                    on_click=lambda e: self.show_login_screen()
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def show_register_screen(self):
        """Zeigt Registrierungsformular - nur Email + Passwort"""
        self.page.clean()
        
        email_field = ft.TextField(
            label="Firmen-E-Mail-Adresse",
            width=300,
            autofocus=True,
            hint_text="vorname.nachname@firma.de"
        )
        
        password_field = ft.TextField(
            label="Passwort erstellen",
            password=True,
            can_reveal_password=True,
            width=300,
            hint_text="Mindestens 8 Zeichen"
        )
        
        confirm_field = ft.TextField(
            label="Passwort bestätigen",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        status_text = ft.Text("", color="red")
        
        def register_clicked(e):
            email = email_field.value
            password = password_field.value
            confirm = confirm_field.value
            
            # Validierung
            if not email or not password or not confirm:
                status_text.value = "Bitte alle Felder ausfüllen."
                status_text.color = "red"
            elif password != confirm:
                status_text.value = "Die Passwörter stimmen nicht überein."
                status_text.color = "red"
            elif len(password) < 8:
                status_text.value = "Passwort muss mindestens 8 Zeichen lang sein."
                status_text.color = "red"
            else:
                # Registrierung durchführen
                success, message, token = self.auth.register_user(email, password)
                
                if success:
                    status_text.value = message
                    status_text.color = "green"
                    self.page.update()
                    # Warte kurz, dann zum Wartebildschirm
                    import time
                    time.sleep(1.5)
                    self.show_pending_approval()
                else:
                    status_text.value = message
                    status_text.color = "red"
            
            self.page.update()
        
        self.page.add(
            ft.Column([
                ft.Text("Erstmalige Registrierung", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Gib deine Firmen-E-Mail ein und wähle ein Passwort.", 
                       color="grey", size=12),
                ft.Divider(height=20, color="transparent"),
                email_field,
                password_field,
                confirm_field,
                ft.ElevatedButton("Registrieren", width=300, on_click=register_clicked),
                status_text,
                ft.Divider(height=10, color="transparent"),
                ft.TextButton("Bereits registriert? Zur Anmeldung", 
                             on_click=lambda e: self.show_login_screen())
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def show_login_screen(self):
        """Zeigt Login-Formular"""
        self.page.clean()
        
        email_field = ft.TextField(
            label="E-Mail-Adresse",
            width=300,
            autofocus=True
        )
        
        password_field = ft.TextField(
            label="Passwort",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        status_text = ft.Text("", color="red")
        
        def login_clicked(e):
            email = email_field.value
            password = password_field.value
            
            if not email or not password:
                status_text.value = "Bitte alle Felder ausfüllen."
                status_text.color = "red"
                self.page.update()
                return
            
            success, message, user_data = self.auth.login_user(email, password)
            
            if success:
                self.current_user = user_data
                self.show_main_app()
            else:
                status_text.value = message
                status_text.color = "red"
                self.page.update()
        
        self.page.add(
            ft.Column([
                ft.Text("Anmeldung", size=24, weight=ft.FontWeight.BOLD),
                email_field,
                password_field,
                ft.ElevatedButton("Anmelden", width=300, on_click=login_clicked),
                status_text,
                ft.Divider(height=10, color="transparent"),
                ft.TextButton("Noch kein Konto? Registrieren", 
                             on_click=lambda e: self.show_register_screen())
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

    def _handle_logout(self, e):
        """Private Methode für Logout-Logik"""
        # Hamburger-Menü schließen
        if self.page.drawer:
            self.page.drawer.open = False
            self.page.update()
        
        # Profil-Drawer schließen
        if self.page.end_drawer:
            self.page.end_drawer.open = False
            self.page.update()
        
        # Logout durchführen
        self.auth.logout()
        self.current_user = None
        
        # Zur Login-Seite navigieren
        self.show_login_screen()
    
    # ========== Admin-Methoden ==========
    def show_admin_menu(self):
        """Zeigt das Admin-Menü (nur für rolle_id = 0)"""
        if self.current_user.get('rolle_id') != 0:
            # Sicherheitscheck: Nicht-Admins zurück zum normalen Menü
            self.show_main_app()
            return
        
        admin_menu = AdminMenuView(self.page, self.current_user, self)
        admin_menu.render()
    
    def show_delete_leads(self):
        """Zeigt die Lead-Löschungs-Ansicht (nur für Admins)"""
        if self.current_user.get('rolle_id') != 0:
            return
        
        delete_view = LeadLoeschenView(self.page, self.db, self.current_user, self)
        delete_view.render()
    # ====================================
    
    # ========== Auswertungs-Methoden ==========
    def _show_auswertung(self):
        """Zeigt die Auswertungs-Ansicht (nur für rolle_id = 4)"""
        # Rollenüberprüfung
        if self.current_user.get('rolle_id') != 4:
            self._show_access_denied("Auswertung")
            return
        
        # Drawer schließen falls vorhanden
        if self.page.drawer:
            self.page.drawer.open = False
            self.page.update()
        
        self.page.clean()
        
        # Erstelle die View nur beim ersten Mal, danach wiederverwenden
        if self.auswertung_view is None:
            self.auswertung_view = AuswertungView(
                self.page,
                self.auswertung_manager,
                self.current_user
            )
            self.auswertung_view.app_controller = self
        else:
            # Update Manager, Page und current_user
            self.auswertung_view.manager = self.auswertung_manager
            self.auswertung_view.page = self.page
            self.auswertung_view.current_user = self.current_user
        
        self.auswertung_view.render()
    
    def _show_access_denied(self, feature_name):
        """Zeigt Zugriff-verweigert Dialog"""
        def close_dialog(e):
            self.page.close(dialog)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Zugriff verweigert"),
            content=ft.Text(f"Du hast keine Berechtigung für '{feature_name}'."),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
        )
        self.page.open(dialog)
    
    def show_auswertung_menu(self):
        """Zeigt das Auswertungs-Menü für rolle_id = 4 Benutzer"""
        self.page.clean()
        self.page.padding = 0
        
        # Profil-Drawer (rechts) erstellen
        is_dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        
        profile_controls = [
            ft.Container(height=10),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=40),
                title=ft.Text(f"{self.current_user.get('vorname', '')} {self.current_user.get('nachname', '')}", 
                             weight=ft.FontWeight.BOLD),
                subtitle=ft.Text(self.current_user.get('email', '')),
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DARK_MODE),
                title=ft.Text("Dark Mode"),
                trailing=ft.Switch(
                    value=is_dark_mode,
                    on_change=self._toggle_theme
                )
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOCK),
                title=ft.Text("Passwort ändern"),
                on_click=lambda e: self._show_change_password()
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.LOGOUT),
                title=ft.Text("Abmelden"),
                on_click=self._handle_logout
            ),
        ]
        
        profile_drawer = ft.NavigationDrawer(controls=profile_controls)
        self.page.end_drawer = profile_drawer
        
        # Header mit Profil-Icon
        header = ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Text("Leadify", size=20, weight=ft.FontWeight.BOLD),
                    ft.Container(width=20),
                    ft.Text("Auswertung", size=16, color="#64748b"),
                ], spacing=10),
                ft.IconButton(
                    icon=ft.Icons.ACCOUNT_CIRCLE,
                    icon_size=28,
                    on_click=lambda e: self._toggle_profile_drawer(),
                    tooltip="Profil"
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=30, vertical=15),
        )
        
        # Willkommenstext
        welcome_section = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Willkommen zu Leadify!",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"Hallo {self.current_user.get('vorname', 'Benutzer')}",
                    size=16,
                    color="#94a3b8",
                ),
                ft.Container(height=20),
                ft.Text(
                    "Controlling - Alle Leads im Überblick",
                    size=18,
                    weight=ft.FontWeight.W_500,
                ),
            ], spacing=5),
            padding=ft.padding.only(left=30, right=30, top=40, bottom=30),
        )
        
        # Auswertungs-Kachel
        tile_section = ft.Container(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.Icons.ANALYTICS, color="white", size=48),
                        bgcolor="#3b82f6",
                        width=80,
                        height=80,
                        border_radius=12,
                        alignment=ft.alignment.center,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Lead Ansicht öffnen",
                        size=18,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        "Alle Leads anzeigen, filtern und auswerten",
                        size=14,
                        color="#64748b",
                        max_lines=2,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=30,
                border_radius=12,
                width=350,
                height=250,
                on_click=lambda e: self._show_auswertung(),
                ink=True,
                border=ft.border.all(1, ft.Colors.OUTLINE),
            ),
            padding=ft.padding.symmetric(horizontal=30),
            alignment=ft.alignment.center,
        )
        
        # Hauptcontainer
        main_content = ft.Column([
            header,
            welcome_section,
            tile_section,
        ], spacing=0, expand=True)
        
        self.page.add(main_content)
    # ==========================================


def main(page: ft.Page):
    """Entry Point der Anwendung"""
    # Datenbankverbindung
    db = database.Database(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_database,
        port=db_port
    )
    
    # App-Controller initialisieren und starten
    app = AppController(page, db)
    app.start()