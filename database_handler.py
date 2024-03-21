import sqlite3

class DatabaseHandler:
    """
    A class that handles connection to a sqllite3 database.
    """

    def __init__(self, db_file: str):
        """
        Parameters:
        db_file (str): Path to the database file.
        """
        self.db_file = db_file
        self.conn = None
        self.connect()
        self.tables = self.create_tables()
        self.disconnect()

    def connect(self) -> None:
        """
        Connects to the database with PARSE_DECLTYPES and PARSE_COLNAMES enabled.
        """
        # PARSE_DECLTYPES is used to convert sqlite3 date objects to python datetime objects
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.PARSE_DECLTYPES
        # PARSE_COLNAMES is used to access columns by name
        # https://docs.python.org/3/library/sqlite3.html#sqlite3.PARSE_COLNAMES
        self.conn = sqlite3.connect(self.db_file, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    def disconnect(self) -> None:
        """
        Disconnects from the database. Sets self.conn to None.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def commit(self) -> None:
        """
        Commits changes to the database. Raises exception if no connection is established.
        """
        if self.conn:
            self.conn.commit()
        else:
            raise Exception("Cannot commit changes, database connection not established.")
        
    def get_cursor(self) -> sqlite3.Cursor:
        """
        Returns a cursor to the database.

        Returns:
        sqlite3.Cursor: Cursor to the database.
        """
        if self.conn == None:
            self.connect()
        return self.conn.cursor()

    def create_tables(self) -> list:
        """
        Creates transaction tables in the database if they do not exist. Raises exception if no connection is established.

        Returns:
        list: List of tables in the database (wether existing or created).
        """
        if not self.conn:
            raise Exception("Database connection not established.")

        cursor = self.conn.cursor()

        # Enable foreign key support, used by month_assets table to reference assets and month_data
        cursor.execute("PRAGMA foreign_keys = ON;")

        # accounts contains id, number and name of accounts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts(
                id INTEGER PRIMARY KEY,
                number TEXT NOT NULL,
                name TEXT DEFAULT ""
                )""")
        
        # categories contains the categories and their parent categories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories(
                id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                parent_category INTEGER DEFAULT NULL,
                FOREIGN KEY(parent_category) REFERENCES categories(id)
                )""")
        
        # text_matches contain an category and a regular expression to match transaction text
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS text_matches(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                reg_ex TEXT NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
                )""")

        # id_matches contain a category and a transaction id to match
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS id_matches(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                transaction_id INTEGER NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id)
                )""")

        # transactions contains all raw transactions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,       
                date DATE NOT NULL, 
                account_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                adjusted_amount REAL NOT NULL,
                transaction_text TEXT NOT NULL,
                comment TEXT DEFAULT "",
                category_id INTEGER DEFAULT NULL,
                text_match_id INTEGER DEFAULT NULL,
                id_match_id INTEGER DEFAULT NULL,
                processed INT DEFAULT 0,
                FOREIGN KEY(account_id) REFERENCES accounts(id),
                FOREIGN KEY(category_id) REFERENCES categories(id),
                FOREIGN KEY(text_match_id) REFERENCES text_matches(id),
                FOREIGN KEY(id_match_id) REFERENCES id_matches(id)       
                )""")


        self.conn.commit()

        # Return a list of tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [table[0] for table in cursor.fetchall()]

    def reset_table(self, table: str) -> int:
        """
        Deletes all rows from the specified table. Raises exception if the table does not exist.

        Parameters:
        table (str): Name of the table to be reset.

        Returns:
        int: Number of rows deleted from the table.
        """
        if not table in self.tables:
            raise Exception("Table {} does not exist.".format(table))
        
        cursor = self.get_cursor()

        cursor.execute("DELETE FROM {}".format(table))

        self.commit()

        return cursor.rowcount
    
    def reset_tables(self) -> int:
        """
        Deletes all rows from all tables.

        Returns:
        int: Number of rows deleted from all tables.
        """

        cursor = self.get_cursor()

        # Delete all rows from all tables
        for table in self.tables:
            cursor.execute("DELETE FROM {}".format(table))

        self.commit()

        return cursor.rowcount

    def get_db_stats(self, stats: list) -> dict:
        """
        Returns a dictionary with the requested stats from the database. Available stats are:
        * "Transactions" - Number of transactions
        * "Unprocessed" - Number of unprocessed transactions
        * "Processed" - Number of processed transactions
        * "Categories" - Number of unique assets
        * "Text Matches" - Number of text matches cases
        * "ID Matches" - Number of ID matches cases
        * "Tables" - Number of tables in the database

        Parameters:
        stats (list): List of stats to be retreived from the database.

        Returns:
        dict: Dictionary with the requested stats from the database.
        """
        if not self.conn:
            raise Exception("Database connection not established.")

        cursor = self.conn.cursor()

        # Create a dictionary to store the stats
        stat_value = {}

        # Get number of transactions
        if "Transactions" in stats:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            stat_value["Transactions"] = cursor.fetchone()[0]

        # Get number of processed transactions
        if "Processed" in stats:
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE processed = 1")
            stat_value["Processed"] = cursor.fetchone()[0]

        # Get number of unprocessed transactions
        if "Unprocessed" in stats:
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE processed = 0")
            stat_value["Unprocessed"] = cursor.fetchone()[0]

        # Get number of unique categories
        if "Categories" in stats:
            cursor.execute("SELECT COUNT(*) FROM categories")
            stat_value["Categories"] = cursor.fetchone()[0]

        # Get number of text matches cases
        if "Text Matches" in stats:
            cursor.execute("SELECT COUNT(*) FROM text_matches")
            stat_value["Text Matches"] = cursor.fetchone()[0]

        # Get number of ID matches cases
        if "ID Matches" in stats:
            cursor.execute("SELECT COUNT(*) FROM id_matches")
            stat_value["ID Matches"] = cursor.fetchone()[0]

        # Get number of tables
        if "Tables" in stats:
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            stat_value["Tables"] = cursor.fetchone()[0]

        return stat_value

    def get_db_stat(self, stat: str) -> float:
        """
        Function that takes a single string corresponding to a stat in get_db_stats

        Parameters:
        stat (str): String corresponding to a stat in get_db_stats

        Returns:
        int or float: Value of the requested stat
        """
        return self.get_db_stats([stat])[stat]

# Example Usage
if __name__ == "__main__":
    # Connect to asset_data.db sqllite3 database
    db_handler = DatabaseHandler('./data/asset_data.db')
    db_handler.connect()

    # Create table for storing transactions if it does not exist
    db_handler.create_tables()

    # Get stats from database
    stats = ["Transactions", "Processed", "Unprocessed", "Categories", "Text Matches", "ID Matches", "Tables"]
    stats = db_handler.get_db_stats(stats)

    # Print each stat and its value
    for stat in stats:
        print(stat, stats[stat])

    db_handler.disconnect()

