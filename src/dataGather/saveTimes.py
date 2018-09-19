import sqlite3

conn = sqlite3.connect('disneyRides.db')
cur = conn.cursor()

cur.execute('select * from Ride')

for row in cur:
    print(row)
