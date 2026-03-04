"""
API Test-Utility
Testet die API-Endpunkte mit verschiedenen Szenarien
"""

import requests
import sys
from pprint import pprint


# Konfiguration
API_BASE_URL = "http://127.0.0.1:8000"
API_KEY = "mein-test-api-key-123"  # Muss mit .env übereinstimmen!


def test_health():
    """Testet Health-Check Endpoint"""
    print("\n" + "="*60)
    print("TEST: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        pprint(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_root():
    """Testet Root Endpoint"""
    print("\n" + "="*60)
    print("TEST: Root Endpoint")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        print(f"Status: {response.status_code}")
        pprint(response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_get_all_leads():
    """Testet GET /api/leads"""
    print("\n" + "="*60)
    print("TEST: GET /api/leads")
    print("="*60)
    
    headers = {"X-API-KEY": API_KEY}
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/leads?limit=5", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total Leads: {data['total']}")
            print(f"Returned: {len(data['leads'])}")
            if data['leads']:
                print("\nErster Lead:")
                pprint(data['leads'][0])
            return True
        else:
            print(f"[ERROR] {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_get_lead_by_id(lead_id: int = 1):
    """Testet GET /api/leads/{id}"""
    print("\n" + "="*60)
    print(f"TEST: GET /api/leads/{lead_id}")
    print("="*60)
    
    headers = {"X-API-KEY": API_KEY}
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/leads/{lead_id}", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            pprint(response.json())
            return True
        else:
            print(f"Response: {response.json()}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_auth_missing_key():
    """Testet fehlenden API-Key"""
    print("\n" + "="*60)
    print("TEST: Authentifizierung (fehlender Key)")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/leads")
        print(f"Status: {response.status_code} (erwartet: 401)")
        pprint(response.json())
        return response.status_code == 401
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_auth_invalid_key():
    """Testet ungültigen API-Key"""
    print("\n" + "="*60)
    print("TEST: Authentifizierung (ungültiger Key)")
    print("="*60)
    
    headers = {"X-API-KEY": "invalid-key-123"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/leads", headers=headers)
        print(f"Status: {response.status_code} (erwartet: 403)")
        pprint(response.json())
        return response.status_code == 403
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def main():
    """Führt alle Tests aus"""
    print("\n" + "#"*60)
    print("#  Leadify API Test Suite")
    print("#"*60)
    
    # API-Key prüfen
    if API_KEY == "ihr-api-key-hier":
        print("\n[WARNING] Bitte setzen Sie einen gültigen API-Key in test_api.py!")
        print("Authentifizierungs-Tests werden fehlschlagen.")
        print()
    
    results = {
        "Health Check": test_health(),
        "Root Endpoint": test_root(),
        "Auth - Missing Key": test_auth_missing_key(),
        "Auth - Invalid Key": test_auth_invalid_key(),
        "GET /api/leads": test_get_all_leads(),
        "GET /api/leads/{id}": test_get_lead_by_id(1),
    }
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("ZUSAMMENFASSUNG")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {test}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n[SUCCESS] Alle Tests erfolgreich!")
        sys.exit(0)
    else:
        print("\n[FAILURE] Einige Tests fehlgeschlagen.")
        sys.exit(1)


if __name__ == "__main__":
    main()
