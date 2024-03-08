import sqlite3
import csv
import json
import datetime
import logging
import operator
import pandas as pd

from functools import reduce
from database_handler import DatabaseHandler

class SpecialCases:
    """
    SpecialCases class handles special cases when adding data to the database. 
    The special cases are defined in a json file as a list of cases with the following structure:
    [{
        "condition": [
            { 
                "col": str, // Name of the column
                "value": str // String that the value of the column should be compared to
                ("operator": str) // If col represents a date, then operator needs to be provided
            },
            // ... more conditions ... ]
        },
        "replacement": [
            {
                "col": str, // Name of the column
                "value": str // String that the value of the column should be replaced with
            },
            // ... more replacements ... ] 
    } ... more cases ... ]
    """
    def __init__(self, file_path: str):
        """
        Parameters:
        file_path (str): Path to json file containing special cases.
        """
        # Read special cases from json file
        special_cases_file = open(file_path, "r")
        self.special_cases = json.load(special_cases_file)
        special_cases_file.close()

        # Define a mapping from operator strings to functions
        self.ops = {
            "==": operator.eq,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
            "!=": operator.ne
        }
    
    def apply_cases(self, df : pd.DataFrame) -> None:
        """
        Applies the special cases to a pandas DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame to apply the special cases to.
        """
        for conditions, replacements in self.special_cases:
            mask_funs = []
            for condition in conditions:
                # Create a list of functions that check if a row matches a special case
                op = self.ops.get(condition.get("operator", "=="))  # default to "=="
                mask_funs.append(lambda x: op(x[condition["col"]], condition["value"]))
            # Apply all mask functions to the dataframe and get a mask
            mask = reduce(lambda f, g: f & g, map(lambda x: x(df), mask_funs))
            # Apply all replacements to the dataframe
            for replacement in replacements:
                df.loc[mask, replacement["col"]] = replacement["value"]


class CSVMapper:
    """
    CSVMapper class handles mapping rows from a transaction csv, to a standard format that can be added to the database.
    """
    def __init__(self, csv_mapping_file: str):
        """
        Parameters:
        csv_file (str): Path to the json file that contains the mapping.
        """
        self.csv_mapping_file = csv_mapping_file
        self.mapping_idx = None
        with open(self.csv_mapping_file, "r") as file:
            self.mappings = json.load(file)

    def set_mapping(self, header: str) -> None:
        """
        Takes a string of semicolon separated column names and find the correct mapping to use.

        Parameters:
        header (list): List of column names.
        """

        # Iterate over all mappings and find the index that matches the header row
        for i, mappings in enumerate(self.mappings):
            if header == mappings["header_row"]:
                self.mapping_idx = i
                return

        # If no mapping is found, throw an error
        raise ValueError("No mapping found for header: {}".format(header))

    @property
    def bank(self) -> str:
        """
        Returns:
        str: The bank that the mapping is for, if the mapping has been set.
        """
        return self.mappings[self.mapping_idx]["bank"] if self.mapping_idx != None else None
    
    @property
    def date_format(self) -> str:
        """
        Returns:
        str: The date format that the mapping uses, if the mapping has been set.
        """
        return self.mappings[self.mapping_idx]["date_format"] if self.mapping_idx != None else None
    
    def get_column_id(self, col: str) -> int:
        """
        Returns the index of the column with the given name.

        Parameters:
        col (str): The name of the column to get the index of.

        Returns:
        int: The index of the column.
        """
        # If the mapping has not been set, throw an error
        if self.mapping_idx == None:
            raise ValueError("Mapping has not been set.")
        if col == "date":
            return self.mappings[self.mapping_idx]["date_col"]
        elif col == "from_account":
            return self.mappings[self.mapping_idx]["from_account_col"]
        elif col == "to_account":
            return self.mappings[self.mapping_idx]["to_account_col"]
        elif col == "amount":
            return self.mappings[self.mapping_idx]["amount_col"]
        elif col == "text":
            return self.mappings[self.mapping_idx]["text_col"]
        else:
            raise ValueError("Column {} does not exist in mapping".format(col))
    
    def map_row(self, row: str) -> dict:
        """
        Maps a row from the csv file to a dictionary with keys that correspond to the database columns.

        Parameters:
        row (str): A semicolon separated row from the csv file.

        Returns:
        dict: A dictionary with keys that correspond to the database columns.
        """

        # If the mapping has not been set, throw an error
        if self.mapping_idx == None:
            raise ValueError("Mapping has not been set.")
        # Create a dictionary with keys that correspond to the database columns and values from the row, as 
        # well as the bank that the mapping is for
        mapped_row = {}
        mapped_row["date"] = datetime.datetime.strptime(row[self.get_column_id("date")], self.date_format).date() if self.get_column_id("date") != None else None
        mapped_row["amount"] = float(row[self.get_column_id("amount")].replace(",",".")) if self.get_column_id("amount") != None else None
        mapped_row["to_account"] = row[self.get_column_id("to_account")] if self.get_column_id("to_account") != None else None
        mapped_row["from_account"] = row[self.get_column_id("from_account")] if self.get_column_id("from_account") != None else None
        mapped_row["text"] = row[self.get_column_id("text")] if self.get_column_id("text") != None else None
        mapped_row["bank"] = self.bank
        mapped_row["adjusted_amount"] = mapped_row["amount"]

        # Check if amount is negative then use from_account as account, otherwise use to_account
        # This might be a bit to specific to how Nordea handles transactions, might need to implement more general logic for other banks.
        if mapped_row["amount"] < 0:
            mapped_row["account"] = mapped_row["from_account"]
        else:
            mapped_row["account"] = mapped_row["to_account"]

        return mapped_row
    
    def map_rows(self, rows: list) -> pd.DataFrame:
        """
        Maps a list of rows from the csv file to a pandas DataFrame with columns that correspond to the database columns.

        Parameters:
        rows (list): A list of semicolon separated rows from the csv file.

        Returns:
        pd.DataFrame: A DataFrame with columns that correspond to the database columns.
        """
        # Map each row in the list of rows
        mapped_rows = [self.map_row(row) for row in rows]
        # Return the list of dictionaries as a pandas DataFrame
        return pd.DataFrame(mapped_rows)



class DataParser:
    """
    DataParser class handles the processing of transactions in the database.
    """
    def __init__(self, database : DatabaseHandler, csv_map_file : str, special_cases_file : str = None):
        """
        Parameters:
        database (DatabaseHandler): The database to add data to.
        csv_map_file (str): Path to the json file that contains the mapping for csv files.
        """
        self.db_handler = database
        self.db_handler.connect()

        # Two cursors are used, one for handling writing processed lines and one responsible for keeping track of unprocessed lines
        self._data_cur = None
        self._transaction_cur = None

        # Initialize a CSVMapper object with the csv_map_file
        self.csv_mapper = CSVMapper(csv_map_file)

        # Initialize a SpecialCases object with the special_cases_file
        if special_cases_file != None:
            self.special_cases = SpecialCases(special_cases_file)
        else:
            self.special_cases = None

        # Since get_account_id gets used on each row, store the account_id for each account in a dictionary
        self._account_ids = {}

    def __del__(self):
        """
        Disconnects from the database when the object is deleted.
        """
        self.db_handler.disconnect()

    # Getter function for self.data_cur
    @property
    def data_cur(self) -> sqlite3.Cursor:
        """
        Returns:
        sqlite3.Cursor: Cursor for creating new transactions in the database.
        """
        # If self._data_cursor is None, ask the database for a cursor
        if self._data_cur is None:
            self._data_cur = self.db_handler.get_cursor()
        return self._data_cur
    
    # Getter function for self.transaction_cur
    @property
    def transaction_cur(self) -> sqlite3.Cursor:
        """
        Returns:
        sqlite3.Cursor: Cursor for iterating over transactions in the database.
        """
        # If self._transaction_cur is None, ask the database for a cursor
        if self._transaction_cur is None:
            self._transaction_cur = self.db_handler.get_cursor()
        return self._transaction_cur

    def get_account_id(self, account_number: str) -> int:
        """
        Returns the account_id of the account with the given name. If the account does not exist, it is added to the database.

        Parameters:
        account_number (str): The number string of the account to get the id of.

        Returns:
        int: The id of the account.
        """
        # Check that account_number is a string and not empty or None
        if not isinstance(account_number, str) or account_number == "" or account_number == None:
            raise ValueError("account_number must be a non-empty string")
        # If account_id is already stored in the dictionary, return it
        if account_number in self._account_ids:
            return self._account_ids[account_number]
        # Get account id from database
        account_id = self.data_cur.execute("SELECT id FROM accounts WHERE number = ?",(account_number,)).fetchone()
        # If account does not exist, add it to the database
        if account_id is None:
            self.data_cur.execute("INSERT INTO accounts(number) VALUES(?)",(account_number,))
            account_id = self.data_cur.execute("SELECT id FROM accounts WHERE number = ?",(account_number,)).fetchone()
        # Store the account_id in the dictionary and return it
        self._account_ids[account_number] = account_id[0]
        return account_id[0]

    def add_data(self, file_path: str) -> int:
        """
        Takes a path to a csv file downloaded from Avanza and adds the data to the database.

        Parameters:
        file_path (str): Path to csv file downloaded from Avanza.

        Returns:
        int: Number of rows added to the database.
        """
        # Open the csv file and read the data
        # Use utf-8-sig to handle BOM in the csv file
        transaction_data_file = open(file_path,"r", encoding='utf-8-sig')
        transaction_data = csv.reader(transaction_data_file, delimiter=';')
        # next() used to skip header row and to find out the mapping of the header row
        header_row = next(transaction_data)
        self.csv_mapper.set_mapping(header_row)
        
        # Map data using csv_mapper. Returns a pandas DataFrame
        data = self.csv_mapper.map_rows(transaction_data)

        # Apply special cases on the rows. This is done before everything else since the special cases might change the data
        if self.special_cases != None:
            self.special_cases.apply_cases(data)

        # Get the account_id for each account
        data["account_id"] = data["account"].apply(self.get_account_id)

        # Find overlapping transactions to avoid adding douplicates
        max_date = data["date"].max()
        min_date = data["date"].min()
        logging.debug("Date range of transactions to be added: {} - {}".format(min_date,max_date))

        # Variable to keep track of number of rows added to the database
        rows_added = 0

        # Get existing rows from database within the date range
        existing_rows = self.data_cur.execute("SELECT date, account_id, amount, transaction_text FROM transactions WHERE date >= ? and date <= ?",(min_date,max_date)).fetchall()

        #Add transactions to database
        cur = self.data_cur
        for i, transaction in data.iterrows():
            row = (\
                transaction["date"],\
                transaction["account_id"],\
                transaction["amount"],\
                transaction["text"],\
                transaction["adjusted_amount"]\
            )

            # If row is not in existing_rows, add it to the database. Don't check adjusted_amount since it might be manually changed.
            if row[0:4] not in existing_rows:
                logging.debug("Adding row {} to database: {}".format(i,row))
                cur.execute('INSERT INTO transactions(date, account_id, amount, transaction_text, adjusted_amount) VALUES(?,?,?,?,?)', row)
                rows_added += 1
            else:
                logging.debug("Row {} already in database: {}".format(i,row))

        # Commit changes to database and disconnect
        self.db_handler.commit()
        self.db_handler.disconnect()

        # Return number of rows added to the database
        logging.info("Added {} rows to the database".format(rows_added))
        return rows_added
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = DatabaseHandler("test.db")
    parser = DataParser(db, "csv_mapping.json")
    parser.add_data("konto_gemensamt.csv")