import sqlite3
conn = sqlite3.connect('eka_ai.db')
cursor = conn.cursor()
cursor.execute("UPDATE alembic_version SET version_num = '0021_refresh_tokens'")
conn.commit()
conn.close()
print("Updated alembic_version to 0021_refresh_tokens")
