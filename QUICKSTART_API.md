# 🚀 Leadify API - Schnellstart

In 3 Minuten zur laufenden API!

## 1️⃣ Dependencies installieren

```powershell
pip install -r requirements-api.txt
```

## 2️⃣ .env Datei erstellen

```powershell
copy .env.example .env
```

Öffnen Sie `.env` und setzen Sie einen API-Key:

```env
API_KEYS=mein-sicherer-api-key-hier
```

## 3️⃣ API starten

**Option A - Mit Batch-Datei:**
```powershell
.\start_api.bat
```

**Option B - Direkt mit Python:**
```powershell
python -m api.main
```

**Option C - Mit uvicorn:**
```powershell
uvicorn api.main:app --reload
```

## 4️⃣ API testen

Öffnen Sie in Ihrem Browser:

📚 **Swagger UI:** http://127.0.0.1:8000/docs

Oder nutzen Sie curl:

```powershell
curl -H "X-API-KEY: mein-sicherer-api-key-hier" http://127.0.0.1:8000/api/leads
```

## ✅ Fertig!

Die API läuft jetzt und ist bereit für die ERP-Integration.

---

**Vollständige Dokumentation:** [README_API.md](README_API.md)

**Test-Script:** `python test_api.py` (API-Key vorher anpassen!)
