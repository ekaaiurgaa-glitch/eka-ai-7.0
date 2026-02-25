import sqlite3
con = sqlite3.connect("eka_ai.db")
cur = con.cursor()
res = cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = res.fetchall()
for table in tables:
    print(table[0])
con.close()
