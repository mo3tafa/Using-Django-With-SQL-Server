import pyodbc 
import pandas as pd
cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                    #   "Driver": "ODBC Driver 17 for SQL Server",
                      "Server=DESKTOP-MTSC260;"
                      "Database=user_leveling_db;"
                      "Trusted_Connection=yes;")

# df = pd.read_sql_query('select * from tbl_user', cnxn)
# print(df)
cursor = cnxn.cursor()
cursor.execute('SELECT * FROM [tbl_user]')

for row in cursor:
    print('row = %r' % (row,))
