import uuid
import json
import os
from pathlib import Path
import bcrypt
from datetime import datetime


class AuthManager:
    """Verwaltet Authentifizierung und Session-Tokens"""
    
    def __init__(self, db):
        self.db = db
        self.token_file = self._get_token_path()
    
    def _get_token_path(self):
        """Bestimmt den Speicherort für das Token (plattformunabhängig)"""
        # Für Flet-Apps: Im User-Verzeichnis speichern
        app_data = Path.home() / ".myapp"
        app_data.mkdir(exist_ok=True)
        return app_data / "session.json"
    
    def register_user(self, email, password):
        """
        Registriert einen Mitarbeiter (setzt Passwort für existierende Email)
        Returns: (success: bool, message: str, token: str or None)
        """
        # Prüfen ob Email im System existiert (Mitarbeiter muss bereits angelegt sein)
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
        
        # Session-Token generieren
        token = str(uuid.uuid4())
        
        # Passwort und Token setzen (is_approved=0, muss vom Admin freigegeben werden)
        result = self.db.query(
            """UPDATE benutzer 
               SET passwort_hash = ?, session_token = ?, token_created_at = NOW(), is_approved = 0
               WHERE benutzer_id = ?""",
            (hashed, token, user['benutzer_id'])
        )
        
        if result:
            # Token lokal speichern (aber noch nicht "genehmigt")
            self._save_token(token, email, approved=False)
            return True, "Registrierung erfolgreich! Warte auf Admin-Freigabe.", token
        
        return False, "Fehler bei der Registrierung.", None
    
    def login_user(self, email, password):
        """
        Meldet einen Benutzer an
        Returns: (success: bool, message: str, user_data: dict or None)
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
        
        # Prüfen ob überhaupt ein Passwort gesetzt wurde (Registrierung erfolgt?)
        if not user['passwort_hash'] or user['passwort_hash'].strip() == '':
            return False, "Für diese E-Mail wurde noch kein Passwort gesetzt. Bitte erst registrieren.", None
        
        # Passwort prüfen (mit Fehlerbehandlung für ungültige Hashes)
        try:
            password_correct = bcrypt.checkpw(password.encode(), user['passwort_hash'].encode())
        except (ValueError, AttributeError) as e:
            # Falls Hash ungültig ist
            print(f"⚠️ Ungültiger Passwort-Hash für {email}: {e}")
            return False, "E-Mail oder Passwort falsch.", None
        
        if not password_correct:
            return False, "E-Mail oder Passwort falsch.", None
        
        # Prüfen ob vom Admin freigegeben
        if not user['is_approved']:
            return False, "Dein Account wurde noch nicht freigeschaltet.", None
        
        # Neues Token generieren
        token = str(uuid.uuid4())
        
        # Token in DB speichern
        self.db.query(
            "UPDATE benutzer SET session_token = ?, token_created_at = NOW() WHERE benutzer_id = ?",
            (token, user['benutzer_id'])
        )
        
        # Token lokal speichern
        self._save_token(token, email, approved=True)
        
        return True, "Login erfolgreich!", user
    
    def check_auto_login(self):
        """
        Prüft bei App-Start, ob ein gültiges Token vorhanden ist
        Returns: (is_logged_in: bool, user_data: dict or None, message: str)
        """
        # Token aus lokalem Speicher laden
        token_data = self._load_token()
        
        if not token_data or not token_data.get('token'):
            return False, None, "Kein gespeichertes Token gefunden."
        
        token = token_data['token']
        
        # Token in Datenbank prüfen
        user = self.db.fetch_one(
            """SELECT benutzer_id, email, vorname, nachname, rolle_id, is_approved
               FROM benutzer 
               WHERE session_token = ? AND is_approved = 1""",
            (token,)
        )
        
        if user:
            return True, user, "Automatisch angemeldet."
        
        # Token ungültig oder nicht genehmigt
        self._clear_token()
        
        # Prüfen ob nur die Genehmigung fehlt
        pending = self.db.fetch_one(
            """SELECT benutzer_id, email FROM benutzer 
               WHERE session_token = ? AND is_approved = 0""",
            (token,)
        )
        
        if pending:
            return False, None, "Warte noch auf Admin-Freigabe."
        
        return False, None, "Token ungültig. Bitte neu anmelden."
    
    def logout(self):
        """Meldet den Benutzer ab"""
        token_data = self._load_token()
        
        if token_data and token_data.get('token'):
            # Token aus DB entfernen
            self.db.query(
                "UPDATE benutzer SET session_token = NULL WHERE session_token = ?",
                (token_data['token'],)
            )
        
        # Lokales Token löschen
        self._clear_token()
    
    def _save_token(self, token, email, approved=True):
        """Speichert Token lokal"""
        data = {
            'token': token,
            'email': email,
            'approved': approved,
            'created_at': datetime.now().isoformat()
        }
        
        with open(self.token_file, 'w') as f:
            json.dump(data, f)
    
    def _load_token(self):
        """Lädt Token aus lokalem Speicher"""
        if not self.token_file.exists():
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                return json.load(f)
        except:
            return None
    
    def _clear_token(self):
        """Löscht lokales Token"""
        if self.token_file.exists():
            os.remove(self.token_file)