import sqlite3

# Connect to an SQLite database
connection = sqlite3.connect("CleanForGreen.db")  # Replace with your database name
cursor = connection.cursor()

cursor.execute('SELECT * FROM user')

userTest = cursor.fetchall()
print(userTest)


connection.commit()
connection.close()