import mariadb
import sys

class Database:
    _instance = None  # Singleton, um nur eine Verbindung zu haben (Wichtig bei Modularisierung)

    def __new__(cls, *args, **kwargs): # <- Beliebig, viele Argumente übergeben
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance # Es wird nur einmal eine Datenbankinstanz erstellt, wenn variable _instance "None" ist und in cls._instance gespeichert.

    def __init__(self, host, user, password, database, port):
        if not hasattr(self, "initialized"):
            try:
                # Parameter speichern
                self.host = host
                self.user = user
                self.password = password
                self.database = database
                self.port = int(port)

                # Verbindung aufbauen
                self.conn = mariadb.connect(
                    host=self.host,
                    user=self.user,
                    port=self.port,
                    password=self.password,
                    database=self.database
                )
                self.cursor = self.conn.cursor(dictionary=True)
                self.initialized = True
                print("[OK] Datenbankverbindung erfolgreich hergestellt.")
            except mariadb.Error as e:
                print(f"[ERROR] Fehler beim Verbinden mit MariaDB: {e}")
                sys.exit(1)


    # Standard Query mit Commit (INSERT, UPDATE, DELETE etc.)
    def query(self, sql, params=None): # <- No SQL-Injection  
        """Einfacher Query-Wrapper mit automatischem Commit."""
        try:
            self.cursor.execute(sql, params or ())
            self.conn.commit()
            # Speichere insert_id SOFORT nach commit, bevor sie verloren geht
            self.last_insert_id = self.cursor.insert_id
            return self.cursor
        except mariadb.Error as e:
            print(f"[ERROR] SQL-Fehler: {e}")
            return None

    # Nur Daten abrufen (SELECT)
    def fetch_all(self, sql, params=None):
        """Führt SELECT-Abfrage aus und gibt alle Ergebnisse als Liste zurück."""
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchall()
            return result
        except mariadb.Error as e:
            print(f"[ERROR] SQL-Fehler: {e}")
            return []

    def fetch_one(self, sql, params=None):
        """Führt SELECT-Abfrage aus und gibt nur das erste Ergebnis zurück."""
        try:
            self.cursor.execute(sql, params or ())
            result = self.cursor.fetchone()
            return result
        except mariadb.Error as e:
            print(f"[ERROR] SQL-Fehler: {e}")
            return None

    def reconnect(self):
        """Verbindung neu aufbauen mit den gespeicherten Parametern."""
        try:
            if hasattr(self, "conn") and self.conn: #<- Überprüfung ob conn im Objekt überhaupt existiert
                self.conn.close()
            self.conn = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("[OK] Verbindung erfolgreich wiederhergestellt.")
            return True
        except mariadb.Error as e:
            print(f"[ERROR] Reconnect fehlgeschlagen: {e}")
            return False


    def is_connected(self):
        """Prüft, ob die DB-Verbindung noch aktiv ist."""
        try:
            self.cursor.execute("SELECT 1")
            return True
        except mariadb.Error:
            return False
        
    def close(self):
        """Verbindung sauber schließen."""
        if hasattr(self, "cursor") and self.cursor:
            self.cursor.close()
        if hasattr(self, "conn") and self.conn: #<- hasattr prüft ob cursor und conn im Objekt existiert
            self.conn.close()
        print("[OK] Verbindung geschlossen.")

