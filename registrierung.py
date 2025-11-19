import flet as ft
import database
from auth_manager import AuthManager

def registration ():

    def main(page: ft.Page):
        page.title = "Meine App"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.padding = 20
        
        # Datenbankverbindung
        from db_config import db_host, db_user, db_password, db_databse, db_port

        db = database.Database(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_databse,
            port=db_port
        )
        
        auth = AuthManager(db)
        
        # --- Views ---
        
        def show_main_app(user_data):
            """Hauptanwendung nach erfolgreichem Login"""
            page.clean()
            
            def logout_clicked(e):
                auth.logout()
                show_login_screen()
            
            page.add(
                ft.Column([
                    ft.Text(f"Willkommen, {user_data.get('vorname', user_data['email'])}!", 
                        size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Rolle ID: {user_data['rolle_id']}"),
                    ft.ElevatedButton("Abmelden", on_click=logout_clicked)
                ])
            )
        
        def show_pending_approval():
            """Wartebildschirm für Admin-Freigabe"""
            page.clean()
            
            def check_approval(e):
                is_logged_in, user_data, message = auth.check_auto_login()
                if is_logged_in:
                    show_main_app(user_data)
                else:
                    status_text.value = message
                    page.update()
            
            status_text = ft.Text("Deine Registrierung wird noch geprüft.\nBitte warte auf die Freigabe durch einen Administrator.")
            
            page.add(
                ft.Column([
                    ft.Icon(ft.Icons.HOURGLASS_EMPTY, size=64, color="orange"),
                    status_text,
                    ft.ElevatedButton("Status aktualisieren", on_click=check_approval),
                    ft.TextButton("Zur Anmeldung", on_click=lambda e: show_login_screen())
                ])
            )
        
        def show_register_screen():
            """Registrierungsformular - nur Email + Passwort"""
            page.clean()
            
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
                    success, message, token = auth.register_user(email, password)
                    
                    if success:
                        status_text.value = message
                        status_text.color = "green"
                        page.update()
                        # Warte kurz, dann zum Wartebildschirm
                        import time
                        time.sleep(1.5)
                        show_pending_approval()
                    else:
                        status_text.value = message
                        status_text.color = "red"
                
                page.update()
            
            page.add(
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
                                on_click=lambda e: show_login_screen())
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        
        def show_login_screen():
            """Login-Formular"""
            page.clean()
            
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
                    page.update()
                    return
                
                success, message, user_data = auth.login_user(email, password)
                
                if success:
                    show_main_app(user_data)
                else:
                    status_text.value = message
                    status_text.color = "red"
                    page.update()
            
            page.add(
                ft.Column([
                    ft.Text("Anmeldung", size=24, weight=ft.FontWeight.BOLD),
                    email_field,
                    password_field,
                    ft.ElevatedButton("Anmelden", width=300, on_click=login_clicked),
                    status_text,
                    ft.TextButton("Noch kein Konto? Registrieren", 
                                on_click=lambda e: show_register_screen())
                ])
            )
        
        # --- App-Start: Auto-Login prüfen ---
        is_logged_in, user_data, message = auth.check_auto_login()
        
        if is_logged_in:
            show_main_app(user_data)
        elif "Warte noch auf Admin-Freigabe" in message:
            show_pending_approval()
        else:
            show_login_screen()


    ft.app(target=main)