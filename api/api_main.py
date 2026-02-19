"""
Einstiegspunkt für die Leadify-API.

Start mit:  uvicorn api.api_main:app --reload
(aus dem Projektverzeichnis heraus)
"""

import sys
import os

# Projektverzeichnis zum Pfad hinzufügen, damit backend.* importiert werden kann
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI
from api.api_routes import router

app = FastAPI(
    title="Leadify API",
    description="REST-API-Schnittstelle für das Leadify Lead-Management-System. "
                "Das Frontend kommuniziert ausschließlich über diese API mit dem Backend.",
    version="1.0.0",
)

app.include_router(router)
