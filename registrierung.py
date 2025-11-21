import flet as ft
from db_config import db_host, db_user, db_password, db_databse, db_port
import database
from auth_manager import AuthManager


class AppController:
    """Hauptsteuerung der Anwendung - verwaltet Navigation und Benutzer-Status"""
    
    def __init__(self, page: ft.Page, db: database.Database):
        self.page = page
        self.db = db
        self.auth = AuthManager(db)
        self.current_user = None
        
        # Page-Konfiguration
        self.page.title = "Firmen-App"
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.padding = 20
    
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
        """Zeigt die Hauptanwendung nach erfolgreichem Login"""
        self.page.clean()
        
        username = self.current_user.get('vorname') or self.current_user.get('email')
        
        self.page.add(
            ft.Column([
                ft.Text(f"Willkommen, {username}!", 
                       size=24, weight=ft.FontWeight.BOLD),
                ft.Text(f"E-Mail: {self.current_user['email']}", color="grey"),
                ft.Text(f"Rolle ID: {self.current_user['rolle_id']}", color="grey"),
                ft.Divider(height=30),
                ft.ElevatedButton(
                    "Abmelden",
                    icon=ft.Icons.LOGOUT,
                    on_click=self._handle_logout
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
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
        self.auth.logout()
        self.current_user = None
        self.show_login_screen()


def main(page: ft.Page):
    """Entry Point der Anwendung"""
    # Datenbankverbindung
    db = database.Database(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_databse,
        port=db_port
    )
    
    # App-Controller initialisieren und starten
    app = AppController(page, db)
    app.start()


# App starten
ft.app(target=main)