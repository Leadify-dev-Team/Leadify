"""
API Routes für Lead-Abruf
Implementiert GET /api/leads und GET /api/leads/{id}
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, Dict, Any
from api.database import APIDatabase
from api.dependencies import verify_api_key, get_db
from api.models import (
    LeadResponse,
    LeadListResponse,
    FirmaResponse,
    AnsprechpartnerResponse,
    ErrorResponse
)


router = APIRouter(
    prefix="/api/leads",
    tags=["Leads"],
    dependencies=[Depends(verify_api_key)]
)


# ============================================================================
# SQL QUERIES
# ============================================================================

LEAD_BASE_QUERY = """
    SELECT 
        l.lead_id,
        l.datum_erfasst,
        
        -- Status & Quelle (lesbare Werte)
        s.status as status_name,
        q.quelle as quelle_name,
        
        -- Produkt-Informationen
        pg.produkt as produktgruppe_name,
        p.produkt as produkt_name,
        pz.zustand as produktzustand_name,
        
        -- Firma
        f.id as firma_id,
        f.name as firma_name,
        f.strasse as firma_strasse,
        f.hausnummer as firma_hausnummer,
        o.ort as ort_name,
        
        -- Ansprechpartner
        ap.id as ansprechpartner_id,
        ap.vorname as ansprechpartner_vorname,
        ap.nachname as ansprechpartner_nachname,
        ap.email as ansprechpartner_email,
        ap.telefon as ansprechpartner_telefon,
        pos.bezeichnung as position_name
        
    FROM lead l
    
    -- Stammdaten JOINs
    LEFT JOIN status s ON l.status_id = s.id
    LEFT JOIN quelle q ON l.quelle_id = q.id_quelle
    LEFT JOIN produktgruppe pg ON l.produktgruppe_id = pg.produkt_id
    LEFT JOIN produkte p ON l.produkt_id = p.produkt_id
    LEFT JOIN produktzustand pz ON l.produktzustand_id = pz.id
    
    -- Ansprechpartner & Firma
    LEFT JOIN ansprechpartner ap ON l.ansprechpartner_id = ap.id
    LEFT JOIN firma f ON ap.firma_id = f.id
    LEFT JOIN ort o ON f.ort_id = o.id_ort
    LEFT JOIN position pos ON ap.position_id = pos.id
"""


# ============================================================================
# MAPPER-FUNKTIONEN (DB-Row → Pydantic-Model)
# ============================================================================

def map_firma(row: Dict[str, Any]) -> Optional[FirmaResponse]:
    """
    Mappt DB-Zeile auf FirmaResponse
    
    Args:
        row: Datenbank-Zeile mit firma_* Feldern
    
    Returns:
        FirmaResponse oder None
    """
    if not row.get("firma_id"):
        return None
    
    return FirmaResponse(
        name=row.get("firma_name") or "",
        strasse=row.get("firma_strasse"),
        hausnummer=row.get("firma_hausnummer"),
        plz=None,  # PLZ nicht in Datenbank vorhanden
        ort=row.get("ort_name")
    )


def map_ansprechpartner(row: Dict[str, Any]) -> Optional[AnsprechpartnerResponse]:
    """
    Mappt DB-Zeile auf AnsprechpartnerResponse
    
    Args:
        row: Datenbank-Zeile mit ansprechpartner_* Feldern
    
    Returns:
        AnsprechpartnerResponse oder None
    """
    if not row.get("ansprechpartner_id"):
        return None
    
    return AnsprechpartnerResponse(
        anrede=None,  # Anrede nicht in Datenbank vorhanden
        vorname=row.get("ansprechpartner_vorname"),
        nachname=row.get("ansprechpartner_nachname"),
        email=row.get("ansprechpartner_email"),
        telefon=row.get("ansprechpartner_telefon"),
        position=row.get("position_name")
    )


def map_lead(row: Dict[str, Any]) -> LeadResponse:
    """
    Mappt DB-Zeile auf LeadResponse
    
    Args:
        row: Vollständige Datenbank-Zeile mit allen JOINs
    
    Returns:
        LeadResponse mit allen verschachtelten Objekten
    """
    return LeadResponse(
        lead_id=row["lead_id"],
        datum_erfasst=row["datum_erfasst"],
        status=row.get("status_name") or "Unbekannt",
        quelle=row.get("quelle_name"),
        produktgruppe=row.get("produktgruppe_name"),
        produkt=row.get("produkt_name"),
        zustand=row.get("produktzustand_name"),
        firma=map_firma(row),
        ansprechpartner=map_ansprechpartner(row)
    )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "",
    response_model=LeadListResponse,
    summary="Alle Leads abrufen",
    description="Gibt alle Leads mit vollständig aufgelösten Daten zurück (keine IDs, nur lesbare Werte)",
    responses={
        200: {"description": "Liste aller Leads"},
        401: {"model": ErrorResponse, "description": "API-Key fehlt"},
        403: {"model": ErrorResponse, "description": "Ungültiger API-Key"},
        500: {"model": ErrorResponse, "description": "Serverfehler"}
    }
)
async def get_all_leads(
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximale Anzahl Ergebnisse"),
    offset: Optional[int] = Query(0, ge=0, description="Anzahl zu überspringende Ergebnisse"),
    status: Optional[str] = Query(None, description="Filter nach Status (z.B. 'offen')"),
    db: APIDatabase = Depends(get_db)
):
    """
    Ruft alle Leads ab
    
    Query-Parameter:
    - limit: Maximale Anzahl Ergebnisse (Standard: alle)
    - offset: Überspringt n Ergebnisse (für Pagination)
    - status: Filtert nach Status-Name (z.B. "offen", "abgeschlossen")
    """
    try:
        # Query zusammenbauen
        query = LEAD_BASE_QUERY
        params = []
        
        # Status-Filter
        if status:
            query += " WHERE s.status = ?"
            params.append(status)
        
        # Sortierung
        query += " ORDER BY l.datum_erfasst DESC"
        
        # Pagination
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        if offset:
            query += " OFFSET ?"
            params.append(offset)
        
        # Query ausführen
        rows = db.fetch_all(query, tuple(params))
        
        # Mapping
        leads = [map_lead(row) for row in rows]
        
        # Gesamtanzahl ermitteln (ohne LIMIT)
        count_query = "SELECT COUNT(*) as total FROM lead l"
        if status:
            count_query += " LEFT JOIN status s ON l.status_id = s.id WHERE s.status = ?"
            count_result = db.fetch_one(count_query, (status,))
        else:
            count_result = db.fetch_one(count_query)
        
        total = count_result["total"] if count_result else 0
        
        return LeadListResponse(total=total, leads=leads)
    
    except Exception as e:
        print(f"[API ERROR] get_all_leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen der Leads: {str(e)}"
        )


@router.get(
    "/{lead_id}",
    response_model=LeadResponse,
    summary="Lead nach ID abrufen",
    description="Gibt einen einzelnen Lead mit vollständig aufgelösten Daten zurück",
    responses={
        200: {"description": "Lead gefunden"},
        404: {"model": ErrorResponse, "description": "Lead nicht gefunden"},
        401: {"model": ErrorResponse, "description": "API-Key fehlt"},
        403: {"model": ErrorResponse, "description": "Ungültiger API-Key"},
        500: {"model": ErrorResponse, "description": "Serverfehler"}
    }
)
async def get_lead_by_id(
    lead_id: int,
    db: APIDatabase = Depends(get_db)
):
    """
    Ruft einen einzelnen Lead ab
    
    Path-Parameter:
    - lead_id: ID des Leads
    """
    try:
        query = LEAD_BASE_QUERY + " WHERE l.lead_id = ?"
        row = db.fetch_one(query, (lead_id,))
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead mit ID {lead_id} wurde nicht gefunden"
            )
        
        return map_lead(row)
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] get_lead_by_id({lead_id}): {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen des Leads: {str(e)}"
        )
