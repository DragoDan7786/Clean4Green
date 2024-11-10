from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def index():
    conn = sqlite3.connect('CleanForGreen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user')
    users = cursor.fetchall()
    conn.close()
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
def add_user():
    userName = request.form['userName']
    pWord = request.form['pWord']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']

    conn = sqlite3.connect('CleanForGreen.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user (userName, pWord, firstName, lastName, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (userName, pWord, firstName, lastName, email))
    conn.commit()
    conn.close()

    return 'User added successfully!'

if __name__ == '__main__':
    app.run(debug=True)