"""
API-Routen für Leadify – Schnittstelle zwischen Frontend und Backend.

Alle Backend-Manager werden hier über FastAPI-Endpunkte bereitgestellt.
Das Frontend ruft ausschließlich diese API auf, das Backend bleibt verdeckt.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import sys

# ── Pfad-Setup, damit "backend.*" importiert werden kann ────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "db_config.env"))

# ── Backend-Imports ─────────────────────────────────────────────────────────
from backend.database import Database
from backend.auth_manager import AuthManager
from backend.lead_bearbeitung_manager import LeadBearbeitungManager
from backend.Außendienst import AussendienstManager
from backend.auswertung_manager import AuswertungManager
from backend.admin_menu_manager import AdminMenuManager
from backend.benutzerfreigabe_manager import BenutzerfreigabeManager
from backend.lead_loeschen_manager import LeadLoeschenManager
from backend.lead_status_manager import LeadStatusManager


# ============================================================================
# DEPENDENCY – Datenbankverbindung (Singleton)
# ============================================================================

_db_instance: Database | None = None


def get_db() -> Database:
    """Liefert die Singleton-Datenbankinstanz."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(
            host=os.getenv("db_host"),
            user=os.getenv("db_user"),
            password=os.getenv("db_password"),
            database=os.getenv("database"),
            port=os.getenv("db_port"),
        )
    return _db_instance


# ============================================================================
# PYDANTIC REQUEST-MODELS
# ============================================================================

# ── Auth ────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    benutzer_id: int
    old_password: str
    new_password: str


class AutoLoginRequest(BaseModel):
    token: str


# ── Leads (Bearbeitung) ────────────────────────────────────────────────────

class AcceptLeadWithCommentRequest(BaseModel):
    kommentar: str


class RejectLeadRequest(BaseModel):
    kommentar: str


class ForwardLeadRequest(BaseModel):
    von_benutzer_id: int
    zu_benutzer_id: int
    kommentar: str = ""


class AddKommentarRequest(BaseModel):
    text: str


class UpdateKommentarRequest(BaseModel):
    new_text: str


# ── Außendienst (Lead erstellen) ────────────────────────────────────────────

class CreateLeadRequest(BaseModel):
    ansprechpartner_id: int
    produkt_id: int
    produktgruppe_id: int
    produktzustand_id: int
    quelle_id: int
    erfasser_id: int
    bearbeiter_id: Optional[int] = None
    beschreibung: Optional[str] = None
    bild_pfad: Optional[str] = None


# ── Admin / Lead-Löschen ────────────────────────────────────────────────────

class DeleteLeadsRequest(BaseModel):
    lead_ids: list[int]


# ── Lead-Status: Vormerken zum Löschen ──────────────────────────────────────

class MarkForDeletionRequest(BaseModel):
    benutzer_id: int
    kommentar: Optional[str] = None


class MarkViewedRequest(BaseModel):
    benutzer_id: int


# ── Auswertung: Excel-Export ────────────────────────────────────────────────

class ExcelExportRequest(BaseModel):
    filter_status: Optional[int] = None
    filter_erfasser: Optional[int] = None
    search_query: str = ""
    erfasser_name: str = ""


# ============================================================================
# HILFS-FUNKTIONEN – Backend-Objekte → dict (JSON-serialisierbar)
# ============================================================================

def _lead_to_dict(lead) -> dict:
    """Konvertiert ein Lead-Objekt in ein JSON-serialisierbares dict."""
    d = lead.__dict__.copy()
    # datetime-Felder konvertieren
    for key, val in d.items():
        if isinstance(val, datetime):
            d[key] = val.isoformat()
    return d


def _aktion_to_dict(aktion) -> dict:
    d = aktion.__dict__.copy()
    for key, val in d.items():
        if isinstance(val, datetime):
            d[key] = val.isoformat()
    return d


def _kommentar_to_dict(kommentar) -> dict:
    d = kommentar.__dict__.copy()
    for key, val in d.items():
        if isinstance(val, datetime):
            d[key] = val.isoformat()
    return d


def _rows_to_dicts(rows: list) -> list[dict]:
    """Konvertiert eine Liste von DB-Rows (dicts) – datetime → isoformat."""
    if not rows:
        return []
    result = []
    for row in rows:
        converted = {}
        for k, v in row.items():
            converted[k] = v.isoformat() if isinstance(v, datetime) else v
        result.append(converted)
    return result


def _row_to_dict(row: dict | None) -> dict | None:
    if row is None:
        return None
    converted = {}
    for k, v in row.items():
        converted[k] = v.isoformat() if isinstance(v, datetime) else v
    return converted


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(prefix="/api")


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  AUTH – Registrierung, Login, Logout, Passwort ändern                     ║
# ╚════════════════════════════════════════════════════════════════════════════╝

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register")
def register(req: RegisterRequest, db: Database = Depends(get_db)):
    auth = AuthManager(db)
    success, message, token = auth.register_user(req.email, req.password)
    return {"success": success, "message": message, "token": token}


@auth_router.post("/login")
def login(req: LoginRequest, db: Database = Depends(get_db)):
    auth = AuthManager(db)
    success, message, user_data = auth.login_user(req.email, req.password)
    return {
        "success": success,
        "message": message,
        "user": _row_to_dict(user_data) if user_data else None,
    }


@auth_router.post("/auto-login")
def auto_login(db: Database = Depends(get_db)):
    """Prüft Auto-Login anhand des lokal gespeicherten Tokens."""
    auth = AuthManager(db)
    is_logged_in, user_data, message = auth.check_auto_login()
    return {
        "is_logged_in": is_logged_in,
        "user": _row_to_dict(user_data) if user_data else None,
        "message": message,
    }


@auth_router.post("/logout")
def logout(db: Database = Depends(get_db)):
    auth = AuthManager(db)
    auth.logout()
    return {"success": True, "message": "Erfolgreich abgemeldet."}


@auth_router.put("/change-password")
def change_password(req: ChangePasswordRequest, db: Database = Depends(get_db)):
    auth = AuthManager(db)
    success, message = auth.change_password(
        req.benutzer_id, req.old_password, req.new_password
    )
    return {"success": success, "message": message}


router.include_router(auth_router)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  LEADS – Lead-Bearbeitung (Innendienst)                                  ║
# ╚════════════════════════════════════════════════════════════════════════════╝

leads_router = APIRouter(prefix="/leads", tags=["Lead-Bearbeitung"])


@leads_router.get("/my/{bearbeiter_id}")
def get_my_leads(bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    leads = mgr.get_my_leads(bearbeiter_id)
    return [_lead_to_dict(l) for l in leads]


@leads_router.get("/neue/{bearbeiter_id}")
def get_neue_leads(bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    leads = mgr.get_neue_leads(bearbeiter_id)
    return [_lead_to_dict(l) for l in leads]


@leads_router.get("/neue/count/{bearbeiter_id}")
def count_neue_leads(bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    return {"anzahl": mgr.count_neue_leads(bearbeiter_id)}


@leads_router.get("/{lead_id}")
def get_lead(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    lead = mgr.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    return _lead_to_dict(lead)


@leads_router.put("/{lead_id}/accept")
def accept_lead(lead_id: int, bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    success = mgr.accept_lead(lead_id, bearbeiter_id)
    return {"success": success}


@leads_router.put("/{lead_id}/accept-with-comment")
def accept_lead_with_comment(
    lead_id: int,
    bearbeiter_id: int,
    req: AcceptLeadWithCommentRequest,
    db: Database = Depends(get_db),
):
    mgr = LeadBearbeitungManager(db)
    success = mgr.accept_lead_with_comment(lead_id, bearbeiter_id, req.kommentar)
    return {"success": success}


@leads_router.put("/{lead_id}/reject")
def reject_lead(
    lead_id: int,
    bearbeiter_id: int,
    req: RejectLeadRequest,
    db: Database = Depends(get_db),
):
    mgr = LeadBearbeitungManager(db)
    success = mgr.reject_lead(lead_id, bearbeiter_id, req.kommentar)
    return {"success": success}


@leads_router.put("/{lead_id}/complete")
def complete_lead(lead_id: int, bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    success = mgr.complete_lead(lead_id, bearbeiter_id)
    return {"success": success}


@leads_router.put("/{lead_id}/forward")
def forward_lead(
    lead_id: int, req: ForwardLeadRequest, db: Database = Depends(get_db)
):
    mgr = LeadBearbeitungManager(db)
    success = mgr.forward_lead(
        lead_id, req.von_benutzer_id, req.zu_benutzer_id, req.kommentar
    )
    return {"success": success}


@leads_router.put("/{lead_id}/angebot")
def create_angebot(lead_id: int, bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    success = mgr.create_angebot(lead_id, bearbeiter_id)
    return {"success": success}


@leads_router.get("/{lead_id}/aktionen")
def get_lead_aktionen(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    aktionen = mgr.get_lead_aktionen(lead_id)
    return [_aktion_to_dict(a) for a in aktionen]


@leads_router.get("/{lead_id}/kommentare")
def get_lead_kommentare(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    kommentare = mgr.get_lead_kommentare(lead_id)
    return [_kommentar_to_dict(k) for k in kommentare]


@leads_router.post("/{lead_id}/kommentar")
def add_kommentar(
    lead_id: int, req: AddKommentarRequest, db: Database = Depends(get_db)
):
    mgr = LeadBearbeitungManager(db)
    result = mgr.add_kommentar(lead_id, req.text)
    return {"success": result is not None}


@leads_router.get("/bearbeiter/verfuegbar")
def get_verfuegbare_bearbeiter(db: Database = Depends(get_db)):
    mgr = LeadBearbeitungManager(db)
    return _rows_to_dicts(mgr.get_verfuegbare_bearbeiter())


router.include_router(leads_router)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  AUSSENDIENST – Firmen, Ansprechpartner, Produkte, Lead erstellen        ║
# ╚════════════════════════════════════════════════════════════════════════════╝

ad_router = APIRouter(prefix="/aussendienst", tags=["Außendienst"])


@ad_router.get("/firmen")
def get_firmen(db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_alle_firmen())


@ad_router.get("/firmen/{firma_id}")
def get_firma(firma_id: int, db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    firma = mgr.get_firma_by_id(firma_id)
    if not firma:
        raise HTTPException(status_code=404, detail="Firma nicht gefunden")
    return _row_to_dict(firma)


@ad_router.get("/firmen/{firma_id}/ansprechpartner")
def get_ansprechpartner(firma_id: int, db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_ansprechpartner_by_firma(firma_id))


@ad_router.get("/produktgruppen")
def get_produktgruppen(db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_produktgruppen())


@ad_router.get("/produkte/{produktgruppe_id}")
def get_produkte(produktgruppe_id: int, db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_produkte_by_gruppe(produktgruppe_id))


@ad_router.get("/produktzustaende")
def get_produktzustaende(db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_produktzustaende())


@ad_router.get("/quellen")
def get_quellen(db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_quellen())


@ad_router.get("/bearbeiter")
def get_ad_bearbeiter(db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    return _rows_to_dicts(mgr.get_verfuegbare_bearbeiter())


@ad_router.post("/leads")
def create_lead(req: CreateLeadRequest, db: Database = Depends(get_db)):
    mgr = AussendienstManager(db)
    lead_id = mgr.create_lead(
        ansprechpartner_id=req.ansprechpartner_id,
        produkt_id=req.produkt_id,
        produktgruppe_id=req.produktgruppe_id,
        produktzustand_id=req.produktzustand_id,
        quelle_id=req.quelle_id,
        erfasser_id=req.erfasser_id,
        bearbeiter_id=req.bearbeiter_id,
        beschreibung=req.beschreibung,
        bild_pfad=req.bild_pfad,
    )
    if lead_id is None:
        raise HTTPException(status_code=500, detail="Lead konnte nicht erstellt werden")
    return {"success": True, "lead_id": lead_id}


router.include_router(ad_router)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  AUSWERTUNG – Alle Leads, Statistiken, Excel-Export                      ║
# ╚════════════════════════════════════════════════════════════════════════════╝

auswertung_router = APIRouter(prefix="/auswertung", tags=["Auswertung"])


@auswertung_router.get("/leads")
def get_all_leads(db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    return _rows_to_dicts(mgr.get_all_leads())


@auswertung_router.get("/leads/bearbeiter/{bearbeiter_id}")
def get_leads_by_bearbeiter(bearbeiter_id: int, db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    return _rows_to_dicts(mgr.get_leads_by_bearbeiter(bearbeiter_id))


@auswertung_router.get("/leads/status/{status_id}")
def get_leads_by_status(status_id: int, db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    return _rows_to_dicts(mgr.get_leads_by_status(status_id))


@auswertung_router.get("/erfasser")
def get_all_erfasser(db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    return _rows_to_dicts(mgr.get_all_erfasser())


@auswertung_router.get("/statistiken")
def get_statistics(db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    stats = mgr.get_statistics()
    return _row_to_dict(stats) if stats else {}


@auswertung_router.get("/leads/{lead_id}")
def get_auswertung_lead(lead_id: int, db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    lead = mgr.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    return _row_to_dict(lead)


@auswertung_router.get("/leads/{lead_id}/aktionen")
def get_auswertung_aktionen(lead_id: int, db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    return _rows_to_dicts(mgr.get_lead_aktionen(lead_id))


@auswertung_router.get("/leads/{lead_id}/kommentare")
def get_auswertung_kommentare(lead_id: int, db: Database = Depends(get_db)):
    mgr = AuswertungManager(db)
    return _rows_to_dicts(mgr.get_lead_kommentare(lead_id))


@auswertung_router.post("/export")
def export_leads_excel(req: ExcelExportRequest, db: Database = Depends(get_db)):
    """Erzeugt eine Excel-Datei und gibt den Dateipfad zurück."""
    mgr = AuswertungManager(db)

    # Alle Leads laden (Manager filtert intern per Excel-AutoFilter)
    all_leads = mgr.get_all_leads()

    success, filepath, message = mgr.export_to_excel(
        all_leads,
        current_filter_status=req.filter_status,
        current_filter_erfasser=req.filter_erfasser,
        search_query=req.search_query,
        erfasser_name_for_filter=req.erfasser_name,
    )

    if not success:
        raise HTTPException(status_code=500, detail=message)

    return FileResponse(
        path=str(filepath),
        filename=filepath.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


router.include_router(auswertung_router)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  ADMIN – Benachrichtigungen, Benutzerfreigabe, Lead-Löschung             ║
# ╚════════════════════════════════════════════════════════════════════════════╝

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Benachrichtigungen ──────────────────────────────────────────────────────

@admin_router.get("/pending-leads-count")
def get_pending_leads_count(db: Database = Depends(get_db)):
    mgr = AdminMenuManager(db)
    return {"count": mgr.get_pending_leads_count()}


@admin_router.get("/pending-users-count")
def get_pending_users_count(db: Database = Depends(get_db)):
    mgr = AdminMenuManager(db)
    return {"count": mgr.get_pending_users_count()}


@admin_router.get("/notification-count")
def get_notification_count(db: Database = Depends(get_db)):
    mgr = AdminMenuManager(db)
    return {"count": mgr.get_notification_count()}


# ── Benutzerfreigabe ────────────────────────────────────────────────────────

@admin_router.get("/pending-users")
def get_pending_users(db: Database = Depends(get_db)):
    mgr = BenutzerfreigabeManager(db)
    return _rows_to_dicts(mgr.get_pending_users())


@admin_router.put("/users/{user_id}/approve")
def approve_user(user_id: int, db: Database = Depends(get_db)):
    mgr = BenutzerfreigabeManager(db)
    success = mgr.approve_user(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Freigabe fehlgeschlagen")
    return {"success": True}


@admin_router.delete("/users/{user_id}/reject")
def reject_user(user_id: int, db: Database = Depends(get_db)):
    mgr = BenutzerfreigabeManager(db)
    success = mgr.reject_user(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Ablehnung fehlgeschlagen")
    return {"success": True}


# ── Lead-Löschung ───────────────────────────────────────────────────────────

@admin_router.get("/leads-for-deletion")
def get_leads_for_deletion(db: Database = Depends(get_db)):
    mgr = LeadLoeschenManager(db)
    return _rows_to_dicts(mgr.get_leads_for_deletion())


@admin_router.delete("/leads")
def delete_leads(req: DeleteLeadsRequest, db: Database = Depends(get_db)):
    mgr = LeadLoeschenManager(db)
    success, deleted_count, error_message = mgr.delete_leads(req.lead_ids)
    if not success:
        raise HTTPException(status_code=500, detail=error_message)
    return {"success": True, "deleted_count": deleted_count}


router.include_router(admin_router)


# ╔════════════════════════════════════════════════════════════════════════════╗
# ║  LEAD-STATUS – Gesendete Leads einsehen (Erfasser-Sicht)                 ║
# ╚════════════════════════════════════════════════════════════════════════════╝

status_router = APIRouter(prefix="/lead-status", tags=["Lead-Status"])


@status_router.get("/my/{erfasser_id}")
def get_my_created_leads(erfasser_id: int, db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    leads = mgr.get_my_created_leads(erfasser_id)
    return [_lead_to_dict(l) for l in leads]


@status_router.get("/{lead_id}")
def get_lead_status_detail(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    lead = mgr.get_lead_by_id(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead nicht gefunden")
    return _row_to_dict(lead)


@status_router.get("/{lead_id}/aktionen")
def get_lead_status_aktionen(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    return _rows_to_dicts(mgr.get_lead_aktionen(lead_id))


@status_router.get("/{lead_id}/kommentare")
def get_lead_status_kommentare(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    return _rows_to_dicts(mgr.get_lead_kommentare(lead_id))


@status_router.put("/kommentar/{kommentar_id}")
def update_kommentar(
    kommentar_id: int, req: UpdateKommentarRequest, db: Database = Depends(get_db)
):
    mgr = LeadStatusManager(db)
    result = mgr.update_kommentar(kommentar_id, req.new_text)
    return {"success": result is not None}


@status_router.get("/{lead_id}/has-recent-action")
def has_recent_action(
    lead_id: int,
    erfasser_id: Optional[int] = Query(None),
    db: Database = Depends(get_db),
):
    mgr = LeadStatusManager(db)
    return {"has_update": mgr.has_recent_action(lead_id, erfasser_id)}


@status_router.post("/{lead_id}/mark-viewed")
def mark_lead_viewed(
    lead_id: int, req: MarkViewedRequest, db: Database = Depends(get_db)
):
    mgr = LeadStatusManager(db)
    mgr.mark_lead_as_viewed(lead_id, req.benutzer_id)
    return {"success": True}


@status_router.post("/{lead_id}/mark-for-deletion")
def mark_lead_for_deletion(
    lead_id: int, req: MarkForDeletionRequest, db: Database = Depends(get_db)
):
    mgr = LeadStatusManager(db)
    success, message = mgr.mark_lead_for_deletion(
        lead_id, req.benutzer_id, req.kommentar
    )
    return {"success": success, "message": message}


@status_router.get("/{lead_id}/is-marked-for-deletion")
def is_lead_marked_for_deletion(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    return {"is_marked": mgr.is_lead_marked_for_deletion(lead_id)}


@status_router.get("/marked-for-deletion/count")
def count_marked_for_deletion(db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    return {"count": mgr.get_count_marked_for_deletion()}


@status_router.get("/{lead_id}/last-action-type")
def get_last_action_type(lead_id: int, db: Database = Depends(get_db)):
    mgr = LeadStatusManager(db)
    return {"aktion_typ": mgr.get_last_action_type(lead_id)}


router.include_router(status_router)
