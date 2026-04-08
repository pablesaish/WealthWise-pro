import mysql.connector  # This was missing!

class Database:
    def __init__(self):
        try:
            self.con = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Yuti#6002",  # <--- Change to your actual password
                database="expensedb"
            )
            self.cursor = self.con.cursor(buffered=True)
            print("Connected to MySQL Successfully!")
        except Exception as e:
            print(f"Database Connection Error: {e}")

    # This method is what the error 'AttributeError' was complaining about
    def execute(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor

    def commit(self):
        self.con.commit()