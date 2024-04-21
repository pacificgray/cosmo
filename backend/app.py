from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import csv
from psycopg2 import connect, sql, Error

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = os.urandom(24)

# Configuration
app.config['UPLOAD_FOLDER'] = "C:/Users/trung/Documents/Project/final-project-cloud/backend/uploads" # Specify the directory to store uploaded files
DATABASE_URL = "postgresql://postgres:123456@localhost/postgres"

try:
    conn = connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    """))
    conn.commit()
    print("Table created successfully")
except Error as e:
    print(f"Error: {str(e)}")
finally:
    if cur:
        cur.close()
    if conn:
        conn.close()

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/signup', methods=['POST'])
def signup():
    username = request.json.get("username")
    password = request.json.get("password")
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(sql.SQL("INSERT INTO users (username, password) VALUES (%s, %s)"), (username, hashed_password))
        conn.commit()
        return jsonify({'success': 'User created successfully'}), 201
    except Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    try:
        conn = connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(sql.SQL("SELECT * FROM users WHERE username = %s"), (username,))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return jsonify({'success': 'Logged in successfully'}), 200
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    except Error as e:
        return jsonify({'error': str(e)}), 400

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': 'Logged out successfully'}), 200

# Upload Endpoint
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        insert_into_postgres(filename)
        return jsonify({'success': 'File uploaded successfully'})

    return jsonify({'error': 'File type not allowed'})

# Helper function to check if the file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}


# Helper function to insert data into PostgreSQL
def insert_into_postgres(filename):
    connection = connect(DATABASE_URL)
    cursor = connection.cursor()

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  
        column_definitions = []
        for column_name in header:
            column_definitions.append(f"{column_name} TEXT")  # Assuming all columns are TEXT type for simplicity

        create_table_query = f"CREATE TABLE IF NOT EXISTS uploaded_data ({', '.join(column_definitions)})"
        cursor.execute(create_table_query)
        
        for row in reader:
            placeholders = ', '.join(['%s' for _ in row])
            insert_query = f"INSERT INTO uploaded_data VALUES ({placeholders})"
            cursor.execute(insert_query, row)

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    app.run(debug=True)
