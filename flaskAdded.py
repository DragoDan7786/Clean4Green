from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # For session and flash messages

# Path for saving uploaded files (pictures for trash reports)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('CleanForGreen.db')
    conn.row_factory = sqlite3.Row  # To return rows as dictionaries
    return conn

# Ensure uploads directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Route for home page (index.html)
@app.route('/')
@app.route('/index')
def home():
    user_logged_in = 'username' in session  # Check if the user is logged in
    username = session.get('username') if user_logged_in else None
    return render_template('index.html', user_logged_in=user_logged_in, username=username)

# Route for signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Insert user data into the user table
        conn = get_db_connection()
        conn.execute('''INSERT INTO user (userName, pWord, firstName, lastName, email, isSuspended)
                         VALUES (?, ?, ?, ?, ?, ?)''', (username, password, first_name, last_name, email, 0))
        conn.commit()
        conn.close()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('''SELECT * FROM user WHERE userName = ? AND pWord = ?''', (username, password)).fetchone()
        conn.close()

        if user:
            session['user_logged_in'] = True
            session['username'] = user['userName']

            # Redirect to home page
            return redirect(url_for('home')) 

        else:
            flash('Invalid username or password. Please try again.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    # Remove any session variables (user logged in status)
    session.pop('user_logged_in', None)
    session.pop('username', None)
    # Redirect to the login page
    return redirect(url_for('login'))

# Route for trash report submission page
@app.route('/submit-trash-report', methods=['GET', 'POST'])
def submit_trash_report():
    if request.method == 'POST':
        # Retrieve form data
        num_items = request.form['numItems']
        item_type = request.form['itemType']
        item_picture = request.files['itemPicture']

        # Save picture file
        if item_picture and allowed_file(item_picture.filename):
            filename = secure_filename(item_picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            item_picture.save(picture_path)
        else:
            flash('Invalid file format. Only images are allowed.')
            return redirect(request.url)

        # Insert trash report into the submissions table
        user_id = 1  # This should be the logged-in user's ID, which you can get from the session
        conn = get_db_connection()
        conn.execute('''INSERT INTO submissions (submission_date, submission_proof, userID)
                         VALUES (CURRENT_TIMESTAMP, ?, ?)''', (picture_path, user_id))
        conn.commit()
        conn.close()

        flash('Trash report submitted successfully!')
        return redirect(url_for('home'))

    return render_template('trashreport.html')

# Helper function to check if file is an allowed image type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    app.run(debug=True)
