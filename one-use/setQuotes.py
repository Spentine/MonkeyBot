import sqlite3

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

def createTable():
  cursor.execute('''
  CREATE TABLE IF NOT EXISTS quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT,
    speaker TEXT,
    dispid INTEGER
  )
  ''')
  
  conn.commit()

def resetDatabase():
  cursor.execute("DROP TABLE IF EXISTS quotes")
  createTable()
  conn.commit()

def addQuote(quote, speaker):
  cursor.execute("SELECT MAX(dispid) FROM quotes")
  largest = cursor.fetchone()[0]
  if largest == None:
    largest = 0
  cursor.execute("INSERT INTO quotes (quote, speaker, dispid) VALUES (?, ?, ?)", (quote, speaker, largest + 1))
  conn.commit()

resetDatabase()
createTable()

quotes = [
  ["QUOTE 1", "SPEAKER 1"],
  ["QUOTE 2", "SPEAKER 2"],
  # etc.
]

for i in quotes:
  addQuote(i[0], i[1])

conn.close()
