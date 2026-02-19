# Leadify

Lead Management App zur systematischen Generierung und Bearbeitung von eingehenden Leads über eine mobile, sowie Desktop-Anwendung.

---

## 🏗️ 3-Schichten-Modell

Die Anwendung folgt einer modernen **3-Schichten-Architektur**:

```
┌──────────────────────────────────────┐
│  Frontend (Flet 0.80)                │  ← Benutzerinterface (Mobile & Desktop)
└─────────────┬────────────────────────┘
              │ HTTP-Requests
┌─────────────▼────────────────────────┐
│  API Layer (FastAPI)                 │  ← REST-API & Abhängigkeiten
│  /api/auth, /api/leads, ...          │
└─────────────┬────────────────────────┘
              │ DB-Queries
┌─────────────▼────────────────────────┐
│  Backend (Manager-Klassen)           │  ← Business-Logik & Datenbankzugriff
│  Database (MariaDB)                  │
└──────────────────────────────────────┘
```

**Vorteil:** Frontend und Backend sind vollständig entkoppelt. Das Frontend kommuniziert **ausschließlich über die FastAPI**, nicht direkt mit der Datenbank.

---

## 🚀 Quickstart

### Voraussetzung: API starten
Die **FastAPI muss zuerst laufen**, damit das Frontend funktioniert!

```bash
uvicorn api.api_main:app --reload
```

Die API läuft dann unter `http://127.0.0.1:8000/api` und stellt alle Endpunkte bereit:
- `/api/auth/` - Authentifizierung (Login, Register, Logout)
- `/api/leads/` - Lead-Bearbeitung
- `/api/aussendienst/` - Außendienst & Lead-Erstellung
- `/api/auswertung/` - Reporting & Excel-Export
- `/api/admin/` - Admin-Funktionen
- `/api/lead-status/` - Lead-Status (Erfasser-Sicht)

### Frontend starten
In einem **zweiten Terminal**:

```bash
python main.py
```

Das Flet-Frontend startet die App und verbindet sich automatisch mit der FastAPI.

---

## 📋 Anforderungen

- Python 3.12+
- MariaDB mit konfigurierter `db_config.env`
- Dependencies: `uv sync`

---