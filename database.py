import mysql.connector

class Database:
    def __init__(self):
        self.config = {
            "host": "metro.proxy.rlwy.net",
            "user": "root",
            "password": "kctpCPRkEPRAlMekYBSHqhrYNGwCIvAg",
            "database": "railway",
            "port": 32408,
            "buffered": True
        }
        self.connect()

    def connect(self):
        try:
            self.con = mysql.connector.connect(**self.config)
            self.cursor = self.con.cursor(buffered=True)
            print("✅ CLOUD DATABASE ENGINE: ONLINE")
        except Exception as e:
            print(f"❌ CONNECTION FAILURE: {e}")

    def execute(self, query, params=None):
        # 🔥 THE FIX: Auto-Reconnect check
        try:
            self.con.ping(reconnect=True, attempts=3, delay=1)
        except:
            self.connect()
            
        try:
            self.cursor.execute(query, params or ())
            return self.cursor
        except Exception as e:
            print(f"SQL Logic Error: {e}")
            return None

    def commit(self):
        self.con.commit()