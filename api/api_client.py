"""
API-Client für Leadify – Proxy-Klassen, die die gleichen Schnittstellen wie
die Backend-Manager bieten, intern aber HTTP-Anfragen an die FastAPI-Endpunkte
senden.

Das Frontend importiert diese Klassen anstelle der Backend-Manager.
"""

import httpx
from pathlib import Path
from datetime import datetime
import json
import os

# ============================================================================
# KONFIGURATION
# ============================================================================

API_BASE_URL = "http://127.0.0.1:8000/api"
_client = None


def get_config_file_path():
    """Gibt den Pfad zur IP-Konfigurationsdatei zurück."""
    try:
        # Versuche verschiedene Speicherorte in Prioritätsreihenfolge
        locations = []
        
        # 1. App-spezifisches Datenverzeichnis (Android-freundlich)
        if 'FLET_APP_STORAGE_DATA' in os.environ:
            locations.append(Path(os.environ['FLET_APP_STORAGE_DATA']) / "leadify_server_config.json")
        
        # 2. Home-Verzeichnis
        try:
            locations.append(Path.home() / ".leadify_server_config.json")
        except:
            pass
        
        # 3. Temporäres Verzeichnis
        try:
            import tempfile
            locations.append(Path(tempfile.gettempdir()) / ".leadify_server_config.json")
        except:
            pass
        
        # 4. Aktuelles Verzeichnis
        locations.append(Path(".leadify_server_config.json"))
        
        # Verwende den ersten schreibbaren Pfad
        for location in locations:
            try:
                # Teste ob wir in dieses Verzeichnis schreiben können
                location.parent.mkdir(parents=True, exist_ok=True)
                # Wenn die Datei existiert, verwende sie
                if location.exists():
                    return location
                # Sonst teste ob wir schreiben können
                test_file = location.parent / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                return location
            except Exception as e:
                continue
        
        # Fallback
        return locations[-1] if locations else Path(".leadify_server_config.json")
    except Exception as e:
        return Path(".leadify_server_config.json")


def load_server_ip():
    """Lädt die gespeicherte Server-IP-Adresse aus der Konfigurationsdatei."""
    try:
        config_file = get_config_file_path()
        if config_file and config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                ip = config.get('server_ip')
                return ip
    except Exception as e:
        import traceback
        traceback.print_exc()
    return None


def save_server_ip(ip_address: str):
    """Speichert die Server-IP-Adresse in der Konfigurationsdatei."""
    try:
        config_file = get_config_file_path()
        if config_file:
            # Stelle sicher, dass das Verzeichnis existiert
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump({'server_ip': ip_address}, f)
            
            
            # Verifiziere, dass die Datei geschrieben wurde
            if config_file.exists():
                with open(config_file, 'r') as f:
                    verify = json.load(f)
                    if verify.get('server_ip') == ip_address:
                        return True
            return True
    except Exception as e:
        import traceback
        traceback.print_exc()
    return False


def set_api_base_url(ip_address: str, port: int = 8000):
    """Setzt die API-Basis-URL basierend auf der IP-Adresse."""
    global API_BASE_URL, _client
    # Entferne http:// oder https:// falls vorhanden
    ip_clean = ip_address.replace("http://", "").replace("https://", "").strip()
    # Entferne Port falls in IP enthalten
    if ":" in ip_clean:
        ip_clean = ip_clean.split(":")[0]
    
    API_BASE_URL = f"http://{ip_clean}:{port}/api"
    _client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)


def get_client():
    """Gibt den HTTP-Client zurück. Initialisiert ihn bei Bedarf."""
    global _client
    if _client is None:
        # Standard-IP verwenden
        set_api_base_url("127.0.0.1")
    return _client


def is_server_configured():
    """Prüft, ob eine Server-IP bereits konfiguriert wurde."""
    try:
        return load_server_ip() is not None
    except:
        return False


# ============================================================================
# DEVICE-ID UND TOKEN MANAGEMENT (Client-seitig)
# ============================================================================

import uuid
import platform


def get_device_file_path(filename):
    """Gibt den Pfad zu einer geräte-spezifischen Datei zurück."""
    try:
        locations = []
        
        # 1. App-spezifisches Datenverzeichnis (Android-freundlich)
        if 'FLET_APP_STORAGE_DATA' in os.environ:
            locations.append(Path(os.environ['FLET_APP_STORAGE_DATA']) / filename)
        
        # 2. Home-Verzeichnis
        try:
            locations.append(Path.home() / f".leadify_{filename}")
        except:
            pass
        
        # 3. Temporäres Verzeichnis
        try:
            import tempfile
            locations.append(Path(tempfile.gettempdir()) / f".leadify_{filename}")
        except:
            pass
        
        # 4. Aktuelles Verzeichnis
        locations.append(Path(f".leadify_{filename}"))
        
        # Verwende den ersten verfügbaren/schreibbaren Pfad
        for location in locations:
            try:
                location.parent.mkdir(parents=True, exist_ok=True)
                if location.exists():
                    return location
                # Teste Schreibbarkeit
                test_file = location.parent / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                return location
            except:
                continue
        
        return locations[-1] if locations else Path(f".leadify_{filename}")
    except Exception as e:
        return Path(f".leadify_{filename}")


def get_or_create_device_id():
    """Generiert oder lädt die eindeutige Device-ID für dieses Gerät."""
    device_file = get_device_file_path("device_id.json")
    
    try:
        if device_file.exists():
            with open(device_file, 'r') as f:
                data = json.load(f)
                device_id = data.get('device_id')
                if device_id:
                    return device_id
    except Exception as e:
        pass
    
    # Neue Device-ID generieren
    device_id = str(uuid.uuid4())
    
    try:
        device_file.parent.mkdir(parents=True, exist_ok=True)
        with open(device_file, 'w') as f:
            json.dump({'device_id': device_id}, f)
    except Exception as e:
        pass
    
    return device_id


def get_device_name():
    """Generiert einen lesbaren Gerätenamen."""
    try:
        system = platform.system()
        node = platform.node() or "Unbekannt"
        
        if system == "Windows":
            return f"Windows – {node}"
        elif system == "Darwin":
            return f"macOS – {node}"
        elif system == "Linux":
            # Android wird als Linux erkannt
            if 'ANDROID_ROOT' in os.environ or 'ANDROID_DATA' in os.environ:
                model = os.environ.get('ANDROID_MODEL', 'Android-Gerät')
                return f"Android – {model}"
            return f"Linux – {node}"
        else:
            return f"{system} – {node}"
    except:
        return "Unbekanntes Gerät"


def save_session(token, device_id, email):
    """Speichert Session-Daten lokal (geräte-spezifisch)."""
    session_file = get_device_file_path("session.json")
    data = {
        'token': token,
        'device_id': device_id,
        'email': email,
        'created_at': datetime.now().isoformat()
    }
    
    try:
        session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(session_file, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        return False


def load_session():
    """Lädt Session-Daten aus lokalem Speicher."""
    session_file = get_device_file_path("session.json")
    
    try:
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
                return data
    except Exception as e:
        pass
    
    return None


def clear_session():
    """Löscht lokale Session-Daten."""
    session_file = get_device_file_path("session.json")
    
    try:
        if session_file.exists():
            os.remove(session_file)
            return True
    except Exception as e:
        pass
    
    return False


# Client-Initialisierung - IMMER sicherstellen, dass _client initialisiert ist
try:
    saved_ip = load_server_ip()
    if saved_ip:
        set_api_base_url(saved_ip)
    else:
        _client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)
except Exception as e:
    # Fallback: Initialisiere mit Standard-URL
    try:
        _client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)
    except Exception as e2:
        _client = None


# ============================================================================
# HILFSKLASSE – dict → Objekt mit Attribut-Zugriff
# ============================================================================

class DictProxy:
    """Erlaubt Attribut-Zugriff auf ein dict (z.B. obj.lead_id statt obj['lead_id'])."""

    def __init__(self, data: dict):
        self.__dict__.update(data)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __getitem__(self, key):
        return self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return f"DictProxy({self.__dict__})"


# Typalias für Lead / LeadAktion / LeadKommentar – damit die Frontend-Imports
# identisch bleiben können (z.B. ``from api.api_client import Lead``).
Lead = DictProxy
LeadAktion = DictProxy
LeadKommentar = DictProxy


# ============================================================================
# AUTH CLIENT
# ============================================================================

class AuthClient:
    """Ersetzt AuthManager – ruft /api/auth/* auf und verwaltet Sessions lokal."""
    
    def __init__(self):
        self.device_id = get_or_create_device_id()
        self.device_name = get_device_name()

    def register_user(self, email: str, password: str):
        try:
            r = _client.post("/auth/register", json={"email": email, "password": password})
            data = r.json()
            return data["success"], data["message"], data.get("token")
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}", None

    def login_user(self, email: str, password: str):
        try:
            r = _client.post("/auth/login", json={
                "email": email,
                "password": password,
                "device_id": self.device_id,
                "device_name": self.device_name
            })
            data = r.json()
            
            if data["success"] and data.get("result"):
                result = data["result"]
                # Session lokal speichern
                save_session(result["token"], result["device_id"], email)
                return data["success"], data["message"], result.get("user")
            
            return data["success"], data["message"], None
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}", None

    def check_auto_login(self):
        try:
            # Lokale Session laden
            session = load_session()
            
            if not session or not session.get('token') or not session.get('device_id'):
                return False, None, "Keine Session gefunden"
            
            # Session beim Server validieren
            r = _client.post("/auth/auto-login", json={
                "token": session['token'],
                "device_id": session['device_id']
            })
            data = r.json()
            
            if not data["is_logged_in"]:
                # Session ungültig - lokal löschen
                clear_session()
            
            return data["is_logged_in"], data.get("user"), data["message"]
        except Exception as e:
            return False, None, "Keine Verbindung zum Server"

    def logout(self):
        try:
            # Lokale Session laden
            session = load_session()
            
            if session and session.get('token') and session.get('device_id'):
                # Server-seitig abmelden
                _client.post("/auth/logout", json={
                    "token": session['token'],
                    "device_id": session['device_id']
                })
            
            # Lokal löschen
            clear_session()
        except Exception as e:
            # Trotzdem lokal löschen
            clear_session()

    def change_password(self, benutzer_id: int, old_password: str, new_password: str):
        try:
            r = _client.put("/auth/change-password", json={
                "benutzer_id": benutzer_id,
                "old_password": old_password,
                "new_password": new_password,
            })
            data = r.json()
            return data["success"], data["message"]
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}"


# ============================================================================
# LEAD-BEARBEITUNG CLIENT
# ============================================================================

class LeadBearbeitungClient:
    """Ersetzt LeadBearbeitungManager – ruft /api/leads/* auf."""

    def get_my_leads(self, bearbeiter_id: int):
        r = _client.get(f"/leads/my/{bearbeiter_id}")
        return [Lead(d) for d in r.json()]

    def get_neue_leads(self, bearbeiter_id: int):
        r = _client.get(f"/leads/neue/{bearbeiter_id}")
        return [Lead(d) for d in r.json()]

    def count_neue_leads(self, bearbeiter_id: int) -> int:
        r = _client.get(f"/leads/neue/count/{bearbeiter_id}")
        return r.json()["anzahl"]

    def get_lead_by_id(self, lead_id: int):
        r = _client.get(f"/leads/{lead_id}")
        if r.status_code == 404:
            return None
        return Lead(r.json())

    def accept_lead(self, lead_id: int, bearbeiter_id: int):
        r = _client.put(f"/leads/{lead_id}/accept", params={"bearbeiter_id": bearbeiter_id})
        return r.json()["success"]

    def accept_lead_with_comment(self, lead_id: int, bearbeiter_id: int, kommentar: str):
        r = _client.put(
            f"/leads/{lead_id}/accept-with-comment",
            params={"bearbeiter_id": bearbeiter_id},
            json={"kommentar": kommentar},
        )
        return r.json()["success"]

    def reject_lead(self, lead_id: int, bearbeiter_id: int, kommentar: str):
        r = _client.put(
            f"/leads/{lead_id}/reject",
            params={"bearbeiter_id": bearbeiter_id},
            json={"kommentar": kommentar},
        )
        return r.json()["success"]

    def complete_lead(self, lead_id: int, bearbeiter_id: int):
        r = _client.put(f"/leads/{lead_id}/complete", params={"bearbeiter_id": bearbeiter_id})
        return r.json()["success"]

    def forward_lead(self, lead_id: int, von_benutzer_id: int, zu_benutzer_id: int, kommentar: str = ""):
        r = _client.put(f"/leads/{lead_id}/forward", json={
            "von_benutzer_id": von_benutzer_id,
            "zu_benutzer_id": zu_benutzer_id,
            "kommentar": kommentar,
        })
        return r.json()["success"]

    def create_angebot(self, lead_id: int, bearbeiter_id: int):
        r = _client.put(f"/leads/{lead_id}/angebot", params={"bearbeiter_id": bearbeiter_id})
        return r.json()["success"]

    def get_lead_aktionen(self, lead_id: int):
        r = _client.get(f"/leads/{lead_id}/aktionen")
        return [LeadAktion(d) for d in r.json()]

    def get_lead_kommentare(self, lead_id: int):
        r = _client.get(f"/leads/{lead_id}/kommentare")
        return [LeadKommentar(d) for d in r.json()]

    def add_kommentar(self, lead_id: int, text: str):
        r = _client.post(f"/leads/{lead_id}/kommentar", json={"text": text})
        return r.json().get("success", False)

    def get_verfuegbare_bearbeiter(self):
        r = _client.get("/leads/bearbeiter/verfuegbar")
        return r.json()


# ============================================================================
# AUSSENDIENST CLIENT
# ============================================================================

class AussendienstClient:
    """Ersetzt AussendienstManager – ruft /api/aussendienst/* auf."""

    def get_alle_firmen(self):
        r = _client.get("/aussendienst/firmen")
        return r.json()

    def get_ansprechpartner_by_firma(self, firma_id: int):
        r = _client.get(f"/aussendienst/firmen/{firma_id}/ansprechpartner")
        return r.json()

    def get_produktgruppen(self):
        r = _client.get("/aussendienst/produktgruppen")
        return r.json()

    def get_produkte_by_gruppe(self, produktgruppe_id: int):
        r = _client.get(f"/aussendienst/produkte/{produktgruppe_id}")
        return r.json()

    def get_produktzustaende(self):
        r = _client.get("/aussendienst/produktzustaende")
        return r.json()

    def get_quellen(self):
        r = _client.get("/aussendienst/quellen")
        return r.json()

    def get_verfuegbare_bearbeiter(self):
        r = _client.get("/aussendienst/bearbeiter")
        return r.json()

    def create_lead(self, ansprechpartner_id, produkt_id, produktgruppe_id,
                    produktzustand_id, quelle_id, erfasser_id,
                    bearbeiter_id=None, beschreibung=None, bild_pfad=None):
        r = _client.post("/aussendienst/leads", json={
            "ansprechpartner_id": ansprechpartner_id,
            "produkt_id": produkt_id,
            "produktgruppe_id": produktgruppe_id,
            "produktzustand_id": produktzustand_id,
            "quelle_id": quelle_id,
            "erfasser_id": erfasser_id,
            "bearbeiter_id": bearbeiter_id,
            "beschreibung": beschreibung,
            "bild_pfad": bild_pfad,
        })
        data = r.json()
        if r.status_code >= 400:
            return None
        return data.get("lead_id")


# ============================================================================
# AUSWERTUNG CLIENT
# ============================================================================

class AuswertungClient:
    """Ersetzt AuswertungManager – ruft /api/auswertung/* auf."""

    def get_all_leads(self):
        r = _client.get("/auswertung/leads")
        return r.json()

    def get_statistics(self):
        r = _client.get("/auswertung/statistiken")
        return r.json()

    def get_all_erfasser(self):
        r = _client.get("/auswertung/erfasser")
        return r.json()

    def get_lead_by_id(self, lead_id: int):
        r = _client.get(f"/auswertung/leads/{lead_id}")
        if r.status_code == 404:
            return None
        return r.json()

    def get_lead_aktionen(self, lead_id: int):
        r = _client.get(f"/auswertung/leads/{lead_id}/aktionen")
        return r.json()

    def get_lead_kommentare(self, lead_id: int):
        r = _client.get(f"/auswertung/leads/{lead_id}/kommentare")
        return r.json()

    def export_to_excel(self, all_leads, current_filter_status=None,
                        current_filter_erfasser=None, search_query="",
                        erfasser_name_for_filter=""):
        """Lädt die Excel-Datei von der API herunter und speichert sie lokal."""
        try:
            r = _client.post("/auswertung/export", json={
                "filter_status": current_filter_status,
                "filter_erfasser": current_filter_erfasser,
                "search_query": search_query,
                "erfasser_name": erfasser_name_for_filter,
            })

            if r.status_code >= 400:
                detail = r.json().get("detail", "Export fehlgeschlagen")
                return (False, None, detail)

            # Datei lokal speichern
            export_dir = Path.home() / "Downloads"
            export_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = export_dir / f"leads_export_{timestamp}.xlsx"
            filepath.write_bytes(r.content)

            return (True, filepath, f"Excel-Datei wurde erfolgreich gespeichert:\n{filepath}")
        except Exception as exc:
            return (False, None, f"Fehler beim Export: {exc}")


# ============================================================================
# ADMIN-MENÜ CLIENT
# ============================================================================

class AdminMenuClient:
    """Ersetzt AdminMenuManager – ruft /api/admin/* auf."""

    def get_pending_leads_count(self) -> int:
        r = _client.get("/admin/pending-leads-count")
        return r.json()["count"]

    def get_pending_users_count(self) -> int:
        r = _client.get("/admin/pending-users-count")
        return r.json()["count"]

    def get_notification_count(self) -> int:
        r = _client.get("/admin/notification-count")
        return r.json()["count"]


# ============================================================================
# BENUTZERFREIGABE CLIENT
# ============================================================================

class BenutzerfreigabeClient:
    """Ersetzt BenutzerfreigabeManager – ruft /api/admin/* auf."""

    def get_pending_users(self):
        r = _client.get("/admin/pending-users")
        return r.json()

    def approve_user(self, user_id: int) -> bool:
        r = _client.put(f"/admin/users/{user_id}/approve")
        return r.status_code < 400

    def reject_user(self, user_id: int) -> bool:
        r = _client.delete(f"/admin/users/{user_id}/reject")
        return r.status_code < 400


# ============================================================================
# LEAD-LÖSCHEN CLIENT
# ============================================================================

class LeadLoeschenClient:
    """Ersetzt LeadLoeschenManager – ruft /api/admin/* auf."""

    def get_leads_for_deletion(self):
        r = _client.get("/admin/leads-for-deletion")
        return r.json()

    def delete_leads(self, lead_ids: list):
        r = _client.request("DELETE", "/admin/leads", json={"lead_ids": lead_ids})
        if r.status_code >= 400:
            detail = r.json().get("detail", "Fehler beim Löschen")
            return (False, 0, detail)
        data = r.json()
        return (True, data["deleted_count"], None)


# ============================================================================
# LEAD-STATUS CLIENT
# ============================================================================

class LeadStatusClient:
    """Ersetzt LeadStatusManager – ruft /api/lead-status/* auf."""

    def get_my_created_leads(self, erfasser_id: int):
        r = _client.get(f"/lead-status/my/{erfasser_id}")
        return [Lead(d) for d in r.json()]

    def get_lead_by_id(self, lead_id: int):
        r = _client.get(f"/lead-status/{lead_id}")
        if r.status_code == 404:
            return None
        return r.json()

    def get_lead_aktionen(self, lead_id: int):
        r = _client.get(f"/lead-status/{lead_id}/aktionen")
        return r.json()

    def get_lead_kommentare(self, lead_id: int):
        r = _client.get(f"/lead-status/{lead_id}/kommentare")
        return r.json()

    def update_kommentar(self, kommentar_id: int, new_text: str):
        r = _client.put(f"/lead-status/kommentar/{kommentar_id}", json={"new_text": new_text})
        return r.json().get("success", False)

    def has_recent_action(self, lead_id: int, erfasser_id: int = None) -> bool:
        params = {}
        if erfasser_id is not None:
            params["erfasser_id"] = erfasser_id
        r = _client.get(f"/lead-status/{lead_id}/has-recent-action", params=params)
        return r.json()["has_update"]

    def mark_lead_as_viewed(self, lead_id: int, benutzer_id: int):
        _client.post(f"/lead-status/{lead_id}/mark-viewed", json={"benutzer_id": benutzer_id})

    def mark_lead_for_deletion(self, lead_id: int, benutzer_id: int, kommentar: str = None):
        r = _client.post(f"/lead-status/{lead_id}/mark-for-deletion", json={
            "benutzer_id": benutzer_id,
            "kommentar": kommentar,
        })
        data = r.json()
        return data["success"], data["message"]

    def is_lead_marked_for_deletion(self, lead_id: int) -> bool:
        r = _client.get(f"/lead-status/{lead_id}/is-marked-for-deletion")
        return r.json()["is_marked"]
