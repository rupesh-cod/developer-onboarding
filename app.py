from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS onboarding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            experience TEXT NOT NULL,
            languages TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.json
    email = data['email']
    username = data['username']
    password = data['password']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (email, username, password) VALUES (?, ?, ?)',
              (email, username, password))
    conn.commit()
    user_id = c.lastrowid
    conn.close()

    return jsonify({'user_id': user_id})

@app.route('/onboard', methods=['POST'])
def onboard():
    data = request.json
    user_id = data['user_id']
    experience = data['experience']
    languages = ','.join(data['languages'])

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO onboarding (user_id, experience, languages) VALUES (?, ?, ?)',
              (user_id, experience, languages))
    conn.commit()
    conn.close()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
