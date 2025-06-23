import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Memuat environment variables dari file .env
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    """Fungsi untuk membuat koneksi ke database."""
    # Mengambil konfigurasi dari environment variables
    # Aplikasi akan mencoba koneksi berulang kali jika database belum siap
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv("DATABASE_HOST"),
                database=os.getenv("POSTGRES_DB"),
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD")
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print("Koneksi database gagal, mencoba lagi...")
            time.sleep(5)
    # Jika semua percobaan gagal
    raise Exception("Tidak dapat terhubung ke database.")


@app.before_first_request
def create_table():
    """Membuat tabel 'tasks' jika belum ada."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            status VARCHAR(50) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    """Menampilkan semua task."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY id;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=('POST',))
def add():
    """Menambahkan task baru."""
    title = request.form['title']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title, status) VALUES (%s, %s)",
                (title, 'Belum Selesai'))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:id>', methods=('POST',))
def update(id):
    """Mengubah status task (Selesai/Belum Selesai)."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Cek status saat ini
    cur.execute("SELECT status FROM tasks WHERE id = %s", (id,))
    current_status = cur.fetchone()[0]
    
    new_status = 'Selesai' if current_status == 'Belum Selesai' else 'Belum Selesai'
    
    cur.execute("UPDATE tasks SET status = %s WHERE id = %s",
                (new_status, id))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    """Menghapus task."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # host='0.0.0.0' agar bisa diakses dari luar container
    app.run(host='0.0.0.0', port=5000, debug=True)