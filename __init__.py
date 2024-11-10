from flask import Flask, render_template, request
import sqlite3


# Connect to an SQLite database
connection = sqlite3.connect("CleanForGreen.db")  # Replace with your database name
cursor = connection.cursor()

#create User Table
cursor.execute('''CREATE TABLE IF NOT EXISTS user (
    userID INTEGER PRIMARY KEY AUTOINCREMENT
    ,userName VARCHAR(250) NOT NULL UNIQUE
    ,pWord VARCHAR(250) NOT NULL
    ,firstName VARCHAR(250) NOT NULL
    ,lastName VARCHAR(250) NOT NULL
    ,email VARCHAR(250) NOT NULL
    ,isSuspended BINARY
);''')

#create Submissions Table
cursor.execute('''CREATE TABLE IF NOT EXISTS submissions (
     SubID INTEGER PRIMARY KEY AUTOINCREMENT
    ,submission_date DATETIME NOT NULL
    ,submission_proof BLOB NOT NULL
    ,userID INTEGER NOT NULL
    ,FOREIGN KEY (userID) REFERENCES user(userID)
     );''')

cursor.execute('''INSERT INTO user (userName, pWord, firstName, lastName, email, isSuspended)
    VALUES (?, ?, ?, ?, ?, ?)
''', ('johndoe', 'password123', 'John', 'Doe', 'john.doe@example.com', 0))





connection.commit()
connection.close()