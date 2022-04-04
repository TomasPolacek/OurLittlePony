import config as c
import pyodbc

class DB_Handler:

    def __init__(self):
        # Specifying the ODBC driver, server name, database, etc. directly
        conn_str = (
            "DRIVER={PostgreSQL Unicode(x64)};"
            "SERVER="+ c.postgres_host+";"
            "PORT="+ c.postgres_port +";"
            "UID="+ c.postgres_user + ";"
            "PWD="+ c.postgres_pass + ";"
            "DATABASE="+ c.postgres_db +";"
            )
        self.cnxn = pyodbc.connect(conn_str, autocommit=True)

        # Create a cursor from the connection
        self.cursor = self.cnxn.cursor()

        # All headers
        self.all_headers = ", ".join(c.tab_col)

        # Composite primary key
        self.pk_str = c.tab_col[0] + ", " + c.tab_col[1] + ", " + c.tab_col[2] + ", " + c.tab_col[3] + ", " + c.tab_col[4]+ ", " + c.tab_col[11]


    def delete_older(self, ts: str = "current_timestamp(0)", table: str = c.postgres_tab_name, ts_col: str = c.tab_col[11]) -> int:
        """

        Delete records older than ts. 
        Returns number of affected rows.

        Arguments:

        ts (optional) : Specifies time and date in psql format timestamp ('YYYY-MM-DD hh:mm:ss'), default = current_timestamp
        table (optional) : Name of a table to remove records from, default = config.postgres_tab_name
        ts_col (optional) : Name of a column which contains timestamp values, default = config.tab_col[11]
        """
        num_of_rows = self.cursor.execute("DELETE FROM " + table + " WHERE " + ts_col + " < " + ts + ";").rowcount
        print("Deleted " + str(num_of_rows) + " old records")
        return 0

    def upsert(self, vals: dict, table: str = c.postgres_tab_name, headers: list[str] = None) -> int:
        """
        Insert values into a table. If record exists, update odds columns instead.
        Returns number of affected rows.

        Arguments:

        vals : Values to insert/update into a table
        table (optional) : Name of a table to insert/update records, default = config.postgres_tab_name
        headers (optional) : Name of columns, default = all
        
        """
        if headers == None:
            headers = c.tab_col
            headers_str = self.all_headers

        if len(headers) != len(vals): 
            raise Exception("Error: Assignment - headers(" + str(len(headers)) + ") != vals(" + str(len(vals)) + ")")

        all_cols_vals_str = "("
        for col in headers:
            all_cols_vals_str += vals[col] + ", " if col != headers[-1] else vals[col] + ") "
        
        upd_ins_str = (
                            "INSERT INTO " + table + " (" + headers_str + ")" 
                            " VALUES " + all_cols_vals_str + ""
                            "ON CONFLICT (" + self.pk_str + ") DO UPDATE " 
                            "SET " + c.tab_col[5] + " = " + vals[c.tab_col[5]] + ", "
                                + c.tab_col[6] + " = " + vals[c.tab_col[6]] + ", "
                                + c.tab_col[7] + " = " + vals[c.tab_col[7]] + ", "
                                + c.tab_col[8] + " = " + vals[c.tab_col[8]] + ", "
                                + c.tab_col[9] + " = " + vals[c.tab_col[9]] + ", "
                                + c.tab_col[10] + " = " + vals[c.tab_col[10]] + ";"
                        )
        
        num_of_rows = self.cursor.execute(upd_ins_str).rowcount
        print("Inserted/Updated " + str(num_of_rows) + " rows.")
        print("Values: " + all_cols_vals_str)
        return 0

    def close(self):
        self.cnxn.close()