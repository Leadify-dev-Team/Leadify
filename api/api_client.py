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
                    print(f"Config-Datei gefunden: {location}")
                    return location
                # Sonst teste ob wir schreiben können
                test_file = location.parent / ".test_write"
                test_file.write_text("test")
                test_file.unlink()
                print(f"Config-Pfad gewählt: {location}")
                return location
            except Exception as e:
                print(f"Pfad {location} nicht verfügbar: {e}")
                continue
        
        # Fallback
        return locations[-1] if locations else Path(".leadify_server_config.json")
    except Exception as e:
        print(f"Fehler beim Ermitteln des Config-Pfades: {e}")
        return Path(".leadify_server_config.json")


def load_server_ip():
    """Lädt die gespeicherte Server-IP-Adresse aus der Konfigurationsdatei."""
    try:
        config_file = get_config_file_path()
        print(f"Versuche IP zu laden von: {config_file}")
        if config_file and config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                ip = config.get('server_ip')
                print(f"IP geladen: {ip}")
                return ip
    except Exception as e:
        print(f"Fehler beim Laden der Server-IP: {e}")
        import traceback
        traceback.print_exc()
    return None


def save_server_ip(ip_address: str):
    """Speichert die Server-IP-Adresse in der Konfigurationsdatei."""
    try:
        config_file = get_config_file_path()
        print(f"Versuche IP zu speichern in: {config_file}")
        if config_file:
            # Stelle sicher, dass das Verzeichnis existiert
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                json.dump({'server_ip': ip_address}, f)
            
            print(f"IP erfolgreich gespeichert: {ip_address}")
            
            # Verifiziere, dass die Datei geschrieben wurde
            if config_file.exists():
                with open(config_file, 'r') as f:
                    verify = json.load(f)
                    if verify.get('server_ip') == ip_address:
                        print("IP-Speicherung verifiziert")
                        return True
            return True
    except Exception as e:
        print(f"Fehler beim Speichern der Server-IP: {e}")
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
    print(f"API_BASE_URL gesetzt auf: {API_BASE_URL}")


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


# Client-Initialisierung - IMMER sicherstellen, dass _client initialisiert ist
try:
    saved_ip = load_server_ip()
    if saved_ip:
        set_api_base_url(saved_ip)
    else:
        _client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)
except Exception as e:
    print(f"Fehler bei der Client-Initialisierung: {e}")
    # Fallback: Initialisiere mit Standard-URL
    try:
        _client = httpx.Client(base_url=API_BASE_URL, timeout=30.0)
    except Exception as e2:
        print(f"Kritischer Fehler bei Client-Initialisierung: {e2}")
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
    """Ersetzt AuthManager – ruft /api/auth/* auf."""

    def register_user(self, email: str, password: str):
        try:
            r = _client.post("/auth/register", json={"email": email, "password": password})
            data = r.json()
            return data["success"], data["message"], data.get("token")
        except Exception as e:
            print(f"Fehler bei register_user: {e}")
            return False, f"Verbindungsfehler: {str(e)}", None

    def login_user(self, email: str, password: str):
        try:
            r = _client.post("/auth/login", json={"email": email, "password": password})
            data = r.json()
            return data["success"], data["message"], data.get("user")
        except Exception as e:
            print(f"Fehler bei login_user: {e}")
            return False, f"Verbindungsfehler: {str(e)}", None

    def check_auto_login(self):
        try:
            r = _client.post("/auth/auto-login")
            data = r.json()
            return data["is_logged_in"], data.get("user"), data["message"]
        except Exception as e:
            print(f"Fehler bei check_auto_login: {e}")
            return False, None, "Keine Verbindung zum Server"

    def logout(self):
        try:
            _client.post("/auth/logout")
        except Exception as e:
            print(f"Fehler bei logout: {e}")

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
            print(f"Fehler bei change_password: {e}")
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
