# Leadify REST API für ERP-Integration

## 📋 Übersicht

Die **Leadify REST API** ist eine **Read-Only** REST-Schnittstelle zur Integration des Leadify Lead-Management-Systems mit externen ERP-Systemen. Die API bietet sicheren Zugriff auf Lead-Daten über API-Key-Authentifizierung.

### ✨ Hauptmerkmale

- ✅ **Nur Lesezugriff** – Keine Schreiboperationen möglich
- ✅ **API-Key Authentifizierung** – Sicherer Zugriff über `X-API-KEY` Header
- ✅ **Vollständig aufgelöste Daten** – Keine IDs in Responses, nur lesbare Werte
- ✅ **Saubere Architektur** – Strikte Trennung von Flet-App und API
- ✅ **Auto-generierte Dokumentation** – Swagger UI und ReDoc
- ✅ **Produktionsbereit** – Mit Error-Handling, Logging und Health-Checks

---

## 🏗️ Architektur

```
api/
├── __init__.py           # Paket-Initialisierung
├── main.py               # FastAPI-App & Startup-Logik
├── config.py             # Konfiguration & Settings
├── database.py           # Read-Only DB-Layer
├── dependencies.py       # Auth & Dependency Injection
├── models.py             # Pydantic Response-Models
└── routes.py             # API-Endpunkte & Business-Logik
```

### 🔄 Datenfluss

```
ERP-System → [API-Key] → FastAPI → APIDatabase → MariaDB (leadify2)
                                  ↓
                           Pydantic Models → JSON Response
```

---

## 🚀 Installation & Setup

### 1. Dependencies installieren

```powershell
# In Ihr Projekt-Verzeichnis wechseln
cd "c:\Users\Zaresnuk\Desktop\Schulfächer 2.Schuljahr\Projekt\Tipp-App"

# API-Dependencies installieren
pip install -r requirements-api.txt
```

### 2. Umgebungsvariablen konfigurieren

Erstellen Sie eine `.env` Datei im Hauptverzeichnis:

```powershell
# .env.example kopieren
copy .env.example .env
```

Öffnen Sie `.env` und passen Sie die Werte an:

```env
# WICHTIG: Generieren Sie sichere API-Keys!
API_KEYS=ihr-sicherer-api-key-hier

# Datenbank (bereits konfiguriert für Ihr System)
DB_HOST=localhost
DB_USER=WIV_Denis
DB_PASSWORD=denisHDD1996
DB_DATABASE=leadify2
DB_PORT=3306

# Server
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=False
```

**Sicherheitshinweis:** Verwenden Sie für Produktion sichere, zufällige API-Keys (z.B. 32+ Zeichen)!

### 3. API starten

```powershell
# Direkt mit Python
python -m api.main

# ODER mit uvicorn (empfohlen für Produktion)
uvicorn api.main:app --host 127.0.0.1 --port 8000

# Für Entwicklung mit Auto-Reload
uvicorn api.main:app --reload
```

Nach dem Start ist die API erreichbar unter:
- **API:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## 📚 API-Endpunkte

### 🟢 GET `/api/leads`

Gibt alle Leads zurück (mit Pagination und Filterung).

**Query-Parameter:**
- `limit` (optional): Maximale Anzahl Ergebnisse (1-1000)
- `offset` (optional): Anzahl zu überspringende Ergebnisse
- `status` (optional): Filter nach Status (z.B. "offen")

**Beispiel-Request:**
```bash
curl -H "X-API-KEY: ihr-api-key" http://127.0.0.1:8000/api/leads?limit=10&status=offen
```

**Response:**
```json
{
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
  ]
}
```

---

### 🟢 GET `/api/leads/{id}`

Gibt einen einzelnen Lead zurück.

**Path-Parameter:**
- `id` (required): Lead-ID

**Beispiel-Request:**
```bash
curl -H "X-API-KEY: ihr-api-key" http://127.0.0.1:8000/api/leads/5
```

**Response:**
```json
{
  "lead_id": 5,
  "datum_erfasst": "2025-02-20",
  "status": "offen",
  "quelle": "Internet",
  "produktgruppe": "Stapler",
  "produkt": "Hubarbeitsbühne",
  "zustand": "Neu",
  "firma": { ... },
  "ansprechpartner": { ... }
}
```

---

### 🟢 GET `/health`

Health-Check für Monitoring.

**Response:**
```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "database": "connected"
}
```

---

## 🔐 Authentifizierung

Alle Endpunkte (außer `/`, `/health`, `/docs`) erfordern einen gültigen API-Key.

**Header:**
```
X-API-KEY: ihr-api-key-hier
```

**Status-Codes:**
- `401 Unauthorized`: API-Key fehlt
- `403 Forbidden`: Ungültiger API-Key
- `404 Not Found`: Ressource nicht gefunden
- `500 Internal Server Error`: Serverfehler

---

## 🧪 API testen

### Mit curl (PowerShell)

```powershell
# Alle Leads abrufen
curl -H "X-API-KEY: ihr-api-key" http://127.0.0.1:8000/api/leads

# Lead mit ID 5 abrufen
curl -H "X-API-KEY: ihr-api-key" http://127.0.0.1:8000/api/leads/5

# Mit Pagination
curl -H "X-API-KEY: ihr-api-key" "http://127.0.0.1:8000/api/leads?limit=5&offset=0"

# Health-Check
curl http://127.0.0.1:8000/health
```

### Mit Swagger UI

1. Öffnen Sie http://127.0.0.1:8000/docs
2. Klicken Sie auf **"Authorize"** (🔒)
3. Geben Sie Ihren API-Key ein
4. Testen Sie die Endpunkte interaktiv

---

## 🗄️ Datenbankstruktur

Die API liest aus folgenden Tabellen (Read-Only):

```
lead (Haupttabelle)
├── status          → Lesbare Status-Namen
├── quelle          → Lead-Quelle (z.B. "Internet")
├── produktgruppe   → Produktgruppe
├── produkte        → Produktname
├── produktzustand  → Zustand (Neu/Gebraucht)
├── ansprechpartner
│   ├── firma
│   │   └── ort
│   └── position
```

**Alle IDs werden aufgelöst** – Die API gibt nur lesbare Werte zurück, keine Datenbank-IDs.

---

## 🔧 Konfiguration

### Environment-Variablen

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `API_KEYS` | Komma-getrennte API-Keys | - |
| `DB_HOST` | Datenbank-Host | `localhost` |
| `DB_USER` | Datenbank-User | `WIV_Denis` |
| `DB_PASSWORD` | Datenbank-Passwort | - |
| `DB_DATABASE` | Datenbank-Name | `leadify2` |
| `DB_PORT` | Datenbank-Port | `3306` |
| `API_HOST` | Server-Host | `127.0.0.1` |
| `API_PORT` | Server-Port | `8000` |
| `API_RELOAD` | Auto-Reload (Dev) | `False` |

---

## 🚀 Produktions-Deployment

### Mit systemd (Linux)

```ini
[Unit]
Description=Leadify API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/pfad/zum/projekt
Environment="PATH=/pfad/zum/venv/bin"
ExecStart=/pfad/zum/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

### Mit Docker (optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-api.txt .
RUN pip install -r requirements-api.txt

COPY api/ api/
COPY db_config.py .

ENV API_HOST=0.0.0.0
ENV API_PORT=8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Reverse Proxy (nginx)

```nginx
location /api {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

---

## 🛡️ Sicherheit

### Best Practices

1. ✅ **Sichere API-Keys verwenden** (32+ Zeichen, zufällig generiert)
2. ✅ **HTTPS in Produktion** (z.B. mit nginx + Let's Encrypt)
3. ✅ **.env nie committen** (bereits in `.gitignore`)
4. ✅ **CORS einschränken** (in `api/main.py`)
5. ✅ **Rate-Limiting** (z.B. mit `slowapi`)
6. ✅ **Logs überwachen** (Console-Output oder File-Logging)

### API-Key generieren (PowerShell)

```powershell
# Sicheren zufälligen API-Key generieren
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

---

## 🐛 Troubleshooting

### Problem: "API-Keys nicht konfiguriert"

**Lösung:** Setzen Sie `API_KEYS` in der `.env` Datei.

### Problem: "Verbindung zur Datenbank fehlgeschlagen"

**Lösung:** Prüfen Sie die DB-Credentials in `.env` und stellen Sie sicher, dass MariaDB läuft.

### Problem: "Module 'api' not found"

**Lösung:** Führen Sie den Server aus dem Hauptverzeichnis aus:
```powershell
cd "c:\Users\Zaresnuk\Desktop\Schulfächer 2.Schuljahr\Projekt\Tipp-App"
python -m api.main
```

### Problem: Port 8000 bereits belegt

**Lösung:** Ändern Sie `API_PORT` in `.env` oder stoppen Sie den anderen Prozess:
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📝 Erweiterungen

### Neue Endpunkte hinzufügen

1. **Route definieren** in `api/routes.py`
2. **Model erstellen** in `api/models.py` (falls nötig)
3. **Business-Logic** in `routes.py` implementieren

### Beispiel: Status-Liste abrufen

```python
# In api/routes.py
@router.get("/status")
async def get_all_status(db: APIDatabase = Depends(get_db)):
    """Gibt alle verfügbaren Status zurück"""
    rows = db.fetch_all("SELECT id, status FROM status ORDER BY status")
    return {"status_list": [row["status"] for row in rows]}
```

---

## 📞 Support

Bei Fragen oder Problemen:
1. Prüfen Sie die Logs in der Console
2. Testen Sie mit `/health` Endpoint
3. Nutzen Sie Swagger UI für interaktive Tests

---

## 📄 Lizenz

Teil des Leadify Lead-Management-Systems.

---

**Version:** 1.0.0  
**Datum:** Februar 2026  
**Dokumentation:** http://127.0.0.1:8000/docs
