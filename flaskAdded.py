from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
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
    conn = sqlite3.connect('CleanForGreen.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
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
        user = conn.execute('SELECT * FROM user WHERE userName = ? AND pWord = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['userID']  # Ensure user ID is set here
            session['username'] = user['userName']
            session['user_logged_in'] = True  # Optional: set a general logged-in flag

            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.')

    return render_template('login.html')

@app.route('/account')
def account():
    if 'user_id' not in session:
        flash("Please log in to view your account.")
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Retrieve user submissions for history
    conn = get_db_connection()
    submissions = conn.execute('SELECT * FROM submissions WHERE userID = ?', (user_id,)).fetchall()
    conn.close()

    return render_template('account.html', submissions=submissions)

# Route to serve uploaded files (images from the uploads directory)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clears all session data
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))

@app.route('/submit-trash-report', methods=['GET', 'POST'])
def submit_trash_report():
    if 'user_id' not in session:
        flash("Please log in to submit a trash report.")
        return redirect(url_for('login'))

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

        # Get user ID from session
        user_id = session['user_id']  # Now it's safe to use user_id

        # Insert trash report into the submissions table
        conn = get_db_connection()
        conn.execute('''INSERT INTO submissions (submission_date, submission_proof, numItems, itemType, userID)
                        VALUES (CURRENT_TIMESTAMP, ?, ?, ?, ?)''', 
                     (filename, num_items, item_type, user_id))  # Save only filename to DB
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
