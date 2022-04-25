from datetime import date
from typing import List

import pyodbc

import src.config as c


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

    def get_dates(self, table: str = c.postgres_tab_name, ts_col: str = c.tab_col[11]):
        return self.cursor.execute("SELECT DISTINCT date(" + ts_col + ") FROM " + table + " ORDER BY date(" + ts_col + ");").fetchall()
    

    def get_from_date(self, web_site:str = "", date_to_querry:str = "", table: str = c.postgres_tab_name, ts_col: str = c.tab_col[11], web_site_col:str = c.tab_col[0]) -> list:
        
        if date_to_querry == "":
            date_to_querry = date.today().strftime('%Y/%m/%d')

        if web_site == "":
            return self.cursor.execute("SELECT * FROM " + table + " WHERE TO_DATE('"+ date_to_querry +"','YYYY-MM-DD')=" + ts_col + "::date;").fetchall()
        else:
            return self.cursor.execute("SELECT * FROM " + table + " WHERE TO_DATE('"+ date_to_querry +"','YYYY-MM-DD')=" + ts_col + "::date and " + web_site_col + "='" + web_site +"';").fetchall()

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

    def upsert(self, vals: List[dict], table: str = c.postgres_tab_name, headers: List[str] = None) -> int:

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

        all_vals = ""
        for row in vals:

            all_cols_vals_str = "("

            for col in headers:
                if col not in row:
                    row[col] = "'+infinity'"
                all_cols_vals_str += row[col] + ", " if col != headers[-1] else row[col] + ")"
                
            all_cols_vals_str += ", " if row != vals[-1] else " "

            all_vals += all_cols_vals_str
        
        upd_ins_str = (
                            "INSERT INTO " + table + " (" + headers_str + ")" 
                            " VALUES " + all_vals + ""
                            "ON CONFLICT (" + self.pk_str + ") DO UPDATE " 
                            "SET " + c.tab_col[5] + " = excluded." + c.tab_col[5] + ", "
                                + c.tab_col[6] + " = excluded." + c.tab_col[6] + ", "
                                + c.tab_col[7] + " = excluded." + c.tab_col[7] + ", "
                                + c.tab_col[8] + " = excluded." + c.tab_col[8] + ", "
                                + c.tab_col[9] + " = excluded." + c.tab_col[9] + ", "
                                + c.tab_col[10] + " = excluded." + c.tab_col[10] + ";"
                        )

        num_of_rows = self.cursor.execute(upd_ins_str).rowcount
        print("Inserted/Updated " + str(num_of_rows) + " rows.")
        return 0

    def close(self):
        self.cnxn.close()
