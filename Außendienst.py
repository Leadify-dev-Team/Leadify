from database import Database

db = Database(
    host="127.0.0.1",
    user="WIV_Denis",
    password="denisHDD1996",  
    database="leadify",
    port=3306
)

# -------------------------------------------------
# READ-FUNKTIONEN FÜRS AUSSENDIENSTMODUL
# -------------------------------------------------

def get_alle_firmen():
    """
    Gibt alle Firmen mit Basisinformationen zurück.
    """
    sql = """
        SELECT 
            f.id,
            f.name AS firma,
            f.strasse,
            f.hausnummer,
            b.name AS branche,     
            o.ort AS ort
        FROM firma f
        LEFT JOIN branche b ON f.branche_id = b.id
        LEFT JOIN ort o ON f.ort_id = o.id
        ORDER BY f.name ASC;
    """
    return db.fetch_all(sql)


def get_firma_by_id(firma_id):
    """
    Gibt eine einzelne Firma inklusive Branche und Ort zurück.
    """
    sql = """
        SELECT 
            f.id,
            f.name AS firma,
            f.strasse,
            f.hausnummer,
            b.name AS branche,
            o.ort AS ort
        FROM firma f
        LEFT JOIN branche b ON f.branche_id = b.id
        LEFT JOIN ort o ON f.ort_id = o.id
        WHERE f.id = %s;
    """
    return db.fetch_one(sql, (firma_id,))


def get_ansprechpartner_by_firma(firma_id):
    """
    Gibt alle Ansprechpartner einer Firma zurück.
    """
    sql = """
        SELECT 
            a.id,
            an.anrede,
            a.vorname,
            a.nachname,
            a.email,
            a.telefon,
            p.positionsname AS position
        FROM ansprechpartner a
        LEFT JOIN anrede an ON a.anrede_id = an.id
        LEFT JOIN position p ON a.position_id = p.id
        WHERE a.firma_id = %s
        ORDER BY a.nachname ASC;
    """
    return db.fetch_all(sql, (firma_id,))


# -------------------------------------------------
# TESTBLOCK (wird nur ausgeführt bei: python Außendienst.py)
# -------------------------------------------------
if __name__ == "__main__":
    print("Starte Test...")
    print(get_alle_firmen())
