import uuid
import json
import os
import platform
from pathlib import Path
import bcrypt
from datetime import datetime


class AuthManager:
    """Verwaltet Authentifizierung mit Multi-Device-Support (Android + Desktop)"""
    
    def __init__(self, db):
        self.db = db
        print(f"🔧 AuthManager initialisiert")
    
    def register_user(self, email, password):
        """
        Registriert einen Mitarbeiter (setzt Passwort für existierende Email)
        Returns: (success: bool, message: str, token: str or None)
        """
        # Prüfen ob Email im System existiert
        user = self.db.fetch_one(
            "SELECT benutzer_id, passwort_hash, vorname, nachname FROM benutzer WHERE email = ?",
            (email,)
        )
        
        if not user:
            return False, "Diese E-Mail-Adresse ist nicht im System hinterlegt.", None
        
        # Prüfen ob bereits ein Passwort gesetzt wurde
        if user['passwort_hash']:
            return False, "Für diese E-Mail wurde bereits ein Passwort gesetzt. Bitte anmelden.", None
        
        # Passwort hashen
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Passwort setzen (is_approved=0, muss vom Admin freigegeben werden)
        result = self.db.query(
            """UPDATE benutzer 
               SET passwort_hash = ?, is_approved = 0
               WHERE benutzer_id = ?""",
            (hashed, user['benutzer_id'])
        )
        
        if result:
            print(f"✅ Benutzer registriert: {email} (wartet auf Freigabe)")
            return True, "Registrierung erfolgreich! Warte auf Admin-Freigabe.", None
        
        return False, "Fehler bei der Registrierung.", None
    
    def login_user(self, email, password, device_id=None, device_name=None):
        """
        Meldet einen Benutzer an und erstellt eine Device-spezifische Session
        Returns: (success: bool, message: str, result: dict or None)
                 result = {"user": user_data, "token": token, "device_id": device_id}
        """
        # Benutzer aus DB abrufen
        user = self.db.fetch_one(
            """SELECT benutzer_id, email, passwort_hash, is_approved, 
                      vorname, nachname, rolle_id 
               FROM benutzer WHERE email = ?""",
            (email,)
        )
        
        if not user:
            return False, "E-Mail oder Passwort falsch.", None
        
        # Prüfen ob überhaupt ein Passwort gesetzt wurde
        if not user['passwort_hash'] or user['passwort_hash'].strip() == '':
            return False, "Für diese E-Mail wurde noch kein Passwort gesetzt. Bitte erst registrieren.", None
        
        # Passwort prüfen
        try:
            password_correct = bcrypt.checkpw(password.encode(), user['passwort_hash'].encode())
        except (ValueError, AttributeError) as e:
            print(f"⚠️ Ungültiger Passwort-Hash für {email}: {e}")
            return False, "E-Mail oder Passwort falsch.", None
        
        if not password_correct:
            return False, "E-Mail oder Passwort falsch.", None
        
        # Prüfen ob vom Admin freigegeben
        if not user['is_approved']:
            return False, "Dein Account wurde noch nicht freigeschaltet.", None
        
        # Device-ID generieren falls nicht übergeben
        if not device_id:
            device_id = str(uuid.uuid4())
        
        if not device_name:
            device_name = "Unbekanntes Gerät"
        
        # Session-Token generieren
        token = str(uuid.uuid4())
        
        # Prüfen ob bereits eine Session für dieses Gerät existiert
        existing_session = self.db.fetch_one(
            """SELECT session_id FROM sessions 
               WHERE benutzer_id = ? AND device_id = ?""",
            (user['benutzer_id'], device_id)
        )
        
        if existing_session:
            # Existierende Session aktualisieren
            self.db.query(
                """UPDATE sessions 
                   SET token = ?, last_used = NOW() 
                   WHERE session_id = ?""",
                (token, existing_session['session_id'])
            )
            print(f"🔄 Session aktualisiert für {email} auf {device_name}")
        else:
            # Neue Session erstellen
            self.db.query(
                """INSERT INTO sessions (benutzer_id, token, device_id, device_name, created_at, last_used)
                   VALUES (?, ?, ?, ?, NOW(), NOW())""",
                (user['benutzer_id'], token, device_id, device_name)
            )
            print(f"✅ Neue Session erstellt für {email} auf {device_name}")
        
        # User-Daten + Token + Device-ID zurückgeben
        result = {
            "user": {
                'benutzer_id': user['benutzer_id'],
                'email': user['email'],
                'vorname': user['vorname'],
                'nachname': user['nachname'],
                'rolle_id': user['rolle_id']
            },
            "token": token,
            "device_id": device_id
        }
        
        return True, "Login erfolgreich!", result
    
    def check_auto_login(self, token, device_id):
        """
        Prüft ob ein Token für ein bestimmtes Gerät noch gültig ist
        Returns: (is_logged_in: bool, user_data: dict or None, message: str)
        """
        if not token or not device_id:
            print("ℹ️ Token oder Device-ID fehlt")
            return False, None, "Token oder Device-ID fehlt."
        
        # Session in Datenbank prüfen (nur für dieses Gerät!)
        session = self.db.fetch_one(
            """SELECT s.session_id, s.benutzer_id, b.email, b.vorname, b.nachname, 
                      b.rolle_id, b.is_approved
               FROM sessions s
               JOIN benutzer b ON s.benutzer_id = b.benutzer_id
               WHERE s.token = ? AND s.device_id = ? AND b.is_approved = 1""",
            (token, device_id)
        )
        
        if session:
            # Session aktualisieren (last_used)
            self.db.query(
                "UPDATE sessions SET last_used = NOW() WHERE session_id = ?",
                (session['session_id'],)
            )
            
            # User-Daten zurückgeben
            user_data = {
                'benutzer_id': session['benutzer_id'],
                'email': session['email'],
                'vorname': session['vorname'],
                'nachname': session['nachname'],
                'rolle_id': session['rolle_id']
            }
            print(f"✅ Auto-Login erfolgreich: {session['email']}")
            return True, user_data, "Automatisch angemeldet."
        
        # Prüfen ob nur die Genehmigung fehlt
        pending = self.db.fetch_one(
            """SELECT b.benutzer_id, b.email 
               FROM sessions s
               JOIN benutzer b ON s.benutzer_id = b.benutzer_id
               WHERE s.token = ? AND s.device_id = ? AND b.is_approved = 0""",
            (token, device_id)
        )
        
        if pending:
            print(f"⏳ Benutzer {pending['email']} wartet auf Admin-Freigabe")
            return False, None, "Warte noch auf Admin-Freigabe."
        
        print("❌ Token ungültig oder abgelaufen")
        return False, None, "Token ungültig. Bitte neu anmelden."
    
    def logout(self, token, device_id):
        """Meldet das angegebene Gerät ab (andere Geräte bleiben angemeldet)"""
        if token and device_id:
            # Session aus DB entfernen (nur für dieses Gerät)
            self.db.query(
                "DELETE FROM sessions WHERE token = ? AND device_id = ?",
                (token, device_id)
            )
            print(f"✅ Logout erfolgreich für Device-ID {device_id[:8]}...")
            return True, "Erfolgreich abgemeldet."
        return False, "Token oder Device-ID fehlt."
    
    def logout_all_devices(self, benutzer_id):
        """Meldet alle Geräte eines Benutzers ab"""
        self.db.query(
            "DELETE FROM sessions WHERE benutzer_id = ?",
            (benutzer_id,)
        )
        print(f"✅ Alle Geräte abgemeldet für Benutzer-ID {benutzer_id}")
        return True, f"Alle Geräte abgemeldet."
    
    def get_active_sessions(self, benutzer_id, current_device_id=None):
        """Gibt alle aktiven Sessions eines Benutzers zurück"""
        sessions = self.db.fetch_all(
            """SELECT session_id, device_name, created_at, last_used, 
                      device_id, (device_id = ?) as is_current
               FROM sessions 
               WHERE benutzer_id = ?
               ORDER BY last_used DESC""",
            (current_device_id or "", benutzer_id)
        )
        return sessions or []
    
    def revoke_session(self, session_id):
        """Entfernt eine bestimmte Session"""
        self.db.query(
            "DELETE FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        print(f"✅ Session {session_id} widerrufen")
    
    def change_password(self, benutzer_id, old_password, new_password):
        """Ändert das Passwort eines Benutzers"""
        try:
            # Benutzer abrufen
            user = self.db.fetch_one(
                "SELECT passwort_hash FROM benutzer WHERE benutzer_id = ?",
                (benutzer_id,)
            )
            
            if not user:
                return False, "Benutzer nicht gefunden"
            
            # Altes Passwort überprüfen
            if not bcrypt.checkpw(old_password.encode('utf-8'), user['passwort_hash'].encode('utf-8')):
                return False, "Altes Passwort ist falsch"
            
            # Neues Passwort hashen
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # Passwort in DB aktualisieren
            self.db.query(
                "UPDATE benutzer SET passwort_hash = ? WHERE benutzer_id = ?",
                (hashed_password.decode('utf-8'), benutzer_id)
            )
            
            print(f"✅ Passwort geändert für Benutzer-ID {benutzer_id}")
            return True, "Passwort erfolgreich geändert"
            
        except Exception as e:
            return False, f"Fehler beim Ändern des Passworts: {str(e)}"
