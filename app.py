from flask import Flask, request, redirect, render_template
import sqlite3
import random
import string
import os

app = Flask(__name__)

# Get the absolute path for the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "url_shortener.db")

def generate_short_url():
    """Generates a random short URL string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def init_db():
    """Initializes the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS urls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        original_url TEXT NOT NULL,
                        short_url TEXT NOT NULL UNIQUE
                    )''')
        conn.commit()
        conn.close()
        print("Database initialized successfully. Table 'urls' is ready.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        original_url = request.form['original_url']

        try:
            # Check if the URL already exists in the database
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('SELECT short_url FROM urls WHERE original_url = ?', (original_url,))
            result = c.fetchone()

            if result:
                # If the URL exists, display a message with the existing short URL
                short_url = result[0]
                conn.close()
                return render_template('index.html', short_url=short_url, message="URL has already been shortened:", message_color="red")

            # Generate a new short URL if it doesn't exist
            short_url = generate_short_url()
            c.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            return f"Database error: {e}", 500

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

init_db()

@app.route('/<short_url>')
def redirect_to_url(short_url):
    """Redirects to the original URL based on the short URL."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
        result = c.fetchone()
        conn.close()

        if result:
            return redirect(result[0])
        else:
            return "URL not found", 404
    except sqlite3.Error as e:
        return f"Database error: {e}", 500

if __name__ == '__main__':
    # Initialize the database explicitly before starting the app
    app.run(debug=True)

