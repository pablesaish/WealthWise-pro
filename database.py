import mysql.connector
from mysql.connector import pooling

class Database:
    def __init__(self):
        self.config = {
            "host": "metro.proxy.rlwy.net",
            "user": "root",
            "password": "kctpCPRkEPRAlMekYBSHqhrYNGwCIvAg",
            "database": "railway",
            "port": 32408,
        }
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="wealthwise_pool",
                pool_size=5,
                pool_reset_session=True,
                **self.config
            )
            print("[OK] CLOUD DATABASE ENGINE: ONLINE (Connection Pool)")
        except Exception as e:
            print(f"[ERROR] CONNECTION FAILURE: {e}")
            self.pool = None

    def get_connection(self):
        """Get a connection from the pool"""
        try:
            return self.pool.get_connection()
        except Exception:
            # Fallback: create a direct connection
            try:
                return mysql.connector.connect(**self.config)
            except Exception as e:
                print(f"[ERROR] FALLBACK CONNECTION FAILURE: {e}")
                return None

    def execute(self, query, params=None):
        """Execute a query using a pooled connection, returns (cursor, connection) tuple.
        For backward compatibility, also sets self.cursor"""
        con = self.get_connection()
        if not con:
            return None
        try:
            cursor = con.cursor(buffered=True)
            cursor.execute(query, params or ())
            # Store for backward compat (dashboard, analysis etc.)
            self._last_con = con
            self.cursor = cursor
            return cursor
        except Exception as e:
            print(f"[SQL ERROR] {e}")
            try:
                con.close()
            except:
                pass
            return None

    def commit(self):
        """Commit using the last used connection"""
        try:
            if hasattr(self, '_last_con') and self._last_con:
                self._last_con.commit()
        except Exception as e:
            print(f"[COMMIT ERROR] {e}")

    def query_value(self, query, params=None):
        """Execute a query and return the first column of the first row as float.
        Uses its own connection so it's safe from concurrent cursor access."""
        con = self.get_connection()
        if not con:
            return 0.0
        try:
            cursor = con.cursor(buffered=True)
            cursor.execute(query, params or ())
            row = cursor.fetchone()
            cursor.close()
            con.close()
            return float(row[0]) if row and row[0] else 0.0
        except Exception as e:
            print(f"[QUERY ERROR] {e}")
            try:
                con.close()
            except:
                pass
            return 0.0