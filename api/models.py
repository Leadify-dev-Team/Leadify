"""
Pydantic Response Models
Definiert die Struktur der API-Antworten
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class FirmaResponse(BaseModel):
    """Firmen-Informationen"""
    name: str = Field(..., description="Firmenname")
    strasse: Optional[str] = Field(None, description="Straßenname")
    hausnummer: Optional[str] = Field(None, description="Hausnummer")
    plz: Optional[str] = Field(None, description="Postleitzahl")
    ort: Optional[str] = Field(None, description="Ortsname")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Muster GmbH",
                "strasse": "Hauptstraße",
                "hausnummer": "10",
                "plz": "80331",
                "ort": "München"
            }
        }


class AnsprechpartnerResponse(BaseModel):
    """Ansprechpartner-Informationen"""
    anrede: Optional[str] = Field(None, description="Anrede (Herr/Frau)")
    vorname: Optional[str] = Field(None, description="Vorname")
    nachname: Optional[str] = Field(None, description="Nachname")
    email: Optional[EmailStr] = Field(None, description="E-Mail-Adresse")
    telefon: Optional[str] = Field(None, description="Telefonnummer")
    position: Optional[str] = Field(None, description="Position/Funktion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "anrede": "Herr",
                "vorname": "Max",
                "nachname": "Mustermann",
                "email": "max@muster.de",
                "telefon": "012345678",
                "position": "Geschäftsführer"
            }
        }


class LeadResponse(BaseModel):
    """Lead-Informationen (vollständig aufgelöst, keine IDs)"""
    lead_id: int = Field(..., description="Lead-ID")
    datum_erfasst: date = Field(..., description="Erfassungsdatum")
    status: str = Field(..., description="Lead-Status (z.B. offen, in Bearbeitung)")
    quelle: Optional[str] = Field(None, description="Quelle des Leads")
    produktgruppe: Optional[str] = Field(None, description="Produktgruppe")
    produkt: Optional[str] = Field(None, description="Produktname")
    zustand: Optional[str] = Field(None, description="Produktzustand (Neu/Gebraucht)")
    firma: Optional[FirmaResponse] = Field(None, description="Firmen-Informationen")
    ansprechpartner: Optional[AnsprechpartnerResponse] = Field(None, description="Ansprechpartner-Informationen")
    
    class Config:
        json_schema_extra = {
            "example": {
                "lead_id": 5,
                "datum_erfasst": "2025-02-20",
                "status": "offen",
                "quelle": "Internet",
                "produktgruppe": "Stapler",
                "produkt": "Hubarbeitsbühne",
                "zustand": "Neu",
                "firma": {
                    "name": "Muster GmbH",
                    "strasse": "Hauptstraße",
                    "hausnummer": "10",
                    "plz": "80331",
                    "ort": "München"
                },
                "ansprechpartner": {
                    "anrede": "Herr",
                    "vorname": "Max",
                    "nachname": "Mustermann",
                    "email": "max@muster.de",
                    "telefon": "012345678",
                    "position": "Geschäftsführer"
                }
            }
        }


class LeadListResponse(BaseModel):
    """Liste von Leads mit Metadaten"""
    total: int = Field(..., description="Gesamtanzahl der Leads")
    leads: List[LeadResponse] = Field(..., description="Lead-Liste")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 42,
                "leads": [
                    {
                        "lead_id": 5,
                        "datum_erfasst": "2025-02-20",
                        "status": "offen",
                        "quelle": "Internet",
                        "produktgruppe": "Stapler",
                        "produkt": "Hubarbeitsbühne",
                        "zustand": "Neu",
                        "firma": {"name": "Muster GmbH", "strasse": "Hauptstraße", "hausnummer": "10", "plz": "80331", "ort": "München"},
                        "ansprechpartner": {"anrede": "Herr", "vorname": "Max", "nachname": "Mustermann", "email": "max@muster.de", "telefon": "012345678", "position": "Geschäftsführer"}
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Fehler-Antwort"""
    error: str = Field(..., description="Fehlermeldung")
    detail: Optional[str] = Field(None, description="Detaillierte Fehlerinformation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "detail": "Lead mit ID 999 wurde nicht gefunden"
            }
        }
