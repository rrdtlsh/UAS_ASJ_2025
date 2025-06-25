import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'kunci-rahasia-yang-sulit-ditebak'

def get_db_connection():
    """Fungsi untuk membuat koneksi ke database."""
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
    raise Exception("Tidak dapat terhubung ke database.")

def setup_database():
    """Membuat tabel 'makeup' jika belum ada, tanpa data contoh."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS makeup (
            id SERIAL PRIMARY KEY,
            nama_produk VARCHAR(255) NOT NULL,
            deskripsi TEXT,
            tahun_terbit INTEGER NOT NULL,
            harga INTEGER NOT NULL,
            url_gambar TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

with app.app_context():
    setup_database()

def validate_product(data):
    """Fungsi untuk memvalidasi input data produk."""
    errors = []
    try:
        tahun = int(data['tahun_terbit'])
        if tahun <= 1900:
            errors.append("Tahun terbit harus lebih besar dari 1900.")
    except ValueError:
        errors.append("Tahun terbit harus berupa angka.")

    try:
        harga = int(data['harga'])
        if harga < 0:
            errors.append("Harga tidak boleh negatif.")
    except ValueError:
        errors.append("Harga harus berupa angka.")

    if not data['nama_produk'] or not isinstance(data['nama_produk'], str):
        errors.append("Nama Produk harus diisi dan berupa string.")
    
    if not data['url_gambar'] or not isinstance(data['url_gambar'], str):
        errors.append("URL Gambar harus diisi.")

    return errors

@app.route('/')
def home():
    """Halaman utama."""
    return render_template('home.html', body_class='home-bg')


@app.route('/makeup')
def makeup_list():
    """Halaman untuk menampilkan semua data makeup."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM makeup ORDER BY id;")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('makeup_list.html', products=products, body_class='list-bg')

@app.route('/add', methods=('GET', 'POST'))
def add():
    """Halaman untuk menambah data makeup baru."""
    if request.method == 'POST':
        data = {
            'nama_produk': request.form['nama_produk'],
            'deskripsi': request.form['deskripsi'],
            'tahun_terbit': request.form['tahun_terbit'],
            'harga': request.form['harga'],
            'url_gambar': request.form['url_gambar']
        }
        
        errors = validate_product(data)
        
        if not errors:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO makeup (nama_produk, deskripsi, tahun_terbit, harga, url_gambar) VALUES (%s, %s, %s, %s, %s)",
                        (data['nama_produk'], data['deskripsi'], data['tahun_terbit'], data['harga'], data['url_gambar']))
            conn.commit()
            cur.close()
            conn.close()
            flash('Produk makeup berhasil ditambahkan!', 'success')
            return redirect(url_for('makeup_list'))
        else:
            for error in errors:
                flash(error, 'danger')
    
    return render_template('add_makeup.html', body_class='form-bg')


@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    """Halaman untuk mengedit data makeup."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM makeup WHERE id = %s", (id,))
    product = cur.fetchone()

    if request.method == 'POST':
        data = {
            'nama_produk': request.form['nama_produk'],
            'deskripsi': request.form['deskripsi'],
            'tahun_terbit': request.form['tahun_terbit'],
            'harga': request.form['harga'],
            'url_gambar': request.form['url_gambar']
        }

        errors = validate_product(data)

        if not errors:
            cur.execute("""
                UPDATE makeup SET nama_produk = %s, deskripsi = %s, tahun_terbit = %s, harga = %s, url_gambar = %s
                WHERE id = %s
            """, (data['nama_produk'], data['deskripsi'], data['tahun_terbit'], data['harga'], data['url_gambar'], id))
            conn.commit()
            flash('Data produk berhasil diperbarui!', 'success')
            return redirect(url_for('makeup_list'))
        else:
            for error in errors:
                flash(error, 'danger')
            product = [id] + list(data.values())
    
    cur.close()
    conn.close()
    return render_template('edit_makeup.html', product=product, body_class='form-bg')


@app.route('/delete/<int:id>', methods=('POST',))
def delete(id):
    """Fungsi untuk menghapus data."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM makeup WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('Produk berhasil dihapus.', 'success')
    return redirect(url_for('makeup_list'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)