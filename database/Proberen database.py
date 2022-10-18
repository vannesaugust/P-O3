import sqlite3
'''
sqlite3.connect('Test_Database')

conn = sqlite3.connect('test_database')
c = conn.cursor()

c.execute(''
          CREATE TABLE IF NOT EXISTS products
          ([product_id] INTEGER PRIMARY KEY, [product_name] TEXT)
          '')

c.execute(''
          CREATE TABLE IF NOT EXISTS prices
          ([product_id] INTEGER PRIMARY KEY, [price] INTEGER)
          '')

conn.commit()

print(c)
'''


con = sqlite3.connect("tutorial.db")
cur = con.cursor()
cur.execute("CREATE TABLE movie(title, year, score)")

res = cur.execute("SELECT name FROM sqlite_master")
print(res.fetchone())

res = cur.execute("SELECT name FROM sqlite_master WHERE name='spam'")
print(res.fetchone())

cur.execute("""
        INSERT INTO movie VALUES
            ('film 1', 1950, 7.2),
            ('film 2', 1990, 8)
        """)
con.commit()

res = cur.execute("SELECT score FROM movie")
print(res.fetchall())

data = [
    ("Monty Python Live at the Hollywood Bowl", 1982, 7.9),
    ("Monty Python's The Meaning of Life", 1983, 7.5),
    ("Monty Python's Life of Brian", 1979, 8.0),
]
cur.executemany("INSERT INTO movie VALUES(?, ?, ?)", data)
con.commit()
res = cur.execute("SELECT score FROM movie")
print(res.fetchall())
