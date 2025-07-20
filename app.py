
# flask adalah framework yang digunakan untuk membangun aplikasi web dengan Python
from flask import Flask, render_template, request, redirect, session, url_for
# flask_mysqldb adalah library untuk menghubungkan Flask dengan MySQL
from flask_mysqldb import MySQL
#matplotlib adalah library untuk membuat grafik
import matplotlib.pyplot as plt
# io adalah library untuk menangani input/output
import io
# base64 adalah library untuk encoding dan decoding data dalam format base64
import base64
# hashlib adalah library untuk hashing data
import hashlib
from functions import isAdmin

# Membuat instance Flask
app = Flask(__name__)

@app.context_processor
def inject_functions():
    return dict(is_admin=isAdmin)
# Fungsi ini akan mengembalikan True jika pengguna adalah admin

# Konfigurasi session
# session adalah objek yang digunakan untuk menyimpan data pengguna
# secret_key digunakan untuk mengamankan session
# Anda bisa mengganti dengan kunci rahasia yang lebih kuat
# Jangan gunakan kunci ini di lingkungan produksi
app.secret_key = 'secretkey123'

# Konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'iqbaljackpot'
app.config['MYSQL_DB'] = 'kehadiran_db'

# Inisialisasi MySQL
# MySQL adalah objek yang digunakan untuk menghubungkan Flask dengan MySQL
mysql = MySQL(app)

# Route untuk halaman utama
# Route adalah decorator yang digunakan untuk menentukan URL yang akan dipetakan ke fungsi tertentu
@app.route('/')
def index():
    if 'loggedin' in session:  # Cek apakah pengguna sudah login   
        return redirect(url_for('dashboard'))   # Jika sudah login, redirect ke dashboard
    return render_template('login.html')    # Jika belum login, tampilkan halaman login


# Route untuk halaman login
# Route ini akan menangani permintaan POST dari form login
@app.route('/login', methods=['POST'])  # Fungsi ini akan menangani permintaan POST dari form login
# Fungsi ini akan menangani permintaan POST dari form login
def login():       
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.md5(password.encode()).hexdigest() # Hash password menggunakan MD5

    # Cek apakah username dan password ada di database
    # Menggunakan cursor untuk mengeksekusi query SQL
    # cursor adalah objek yang digunakan untuk mengeksekusi query SQL
    
    cur = mysql.connection.cursor() # Mengambil cursor dari koneksi MySQL
    # Menggunakan parameterized query untuk mencegah SQL injection
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password_hash)) 
    user = cur.fetchone() # Mengambil satu baris hasil query
    if user:
        session['loggedin'] = True # Menyimpan status login di session
        session['username'] = user[1] # Menyimpan username di session
        session['role'] = user[3] # Menyimpan role di session
        # Jika login berhasil, redirect ke dashboard
        return redirect(url_for('dashboard'))  # Jika login berhasil, redirect ke dashboard
    return render_template('login.html', error='Invalid credentials')   # Jika login gagal, tampilkan pesan error

@app.route('/logout') # Route untuk logout 
def logout(): # Fungsi ini akan menangani permintaan logout
    # Menghapus session untuk logout
    session.clear()
    return redirect(url_for('index')) # Redirect ke halaman login
# Route untuk halaman dashboard

@app.route('/dashboard') # Route untuk halaman dashboard
# Fungsi ini akan menangani permintaan ke halaman dashboard
def dashboard():
    if 'loggedin' not in session : # Cek apakah pengguna sudah login
        return redirect(url_for('index')) # Jika belum login, redirect ke halaman login
    return render_template('dashboard.html', username=session['username'])  # Tampilkan halaman dashboard dengan username pengguna

# Route untuk halaman users
# Route ini akan menampilkan daftar pengguna
@app.route('/users')
def users():

    if 'loggedin' not in session:  # Cek apakah pengguna sudah login
       return redirect(url_for('index')) # Jika belum login, redirect ke halaman login
    if not isAdmin():  # Cek apakah pengguna adalah admin
       return redirect(url_for('dashboard')) # Jika bukan admin, redirect ke dashboard
    
    cur = mysql.connection.cursor()     # Mengambil cursor dari koneksi MySQL
    # Menggunakan cursor untuk mengeksekusi query SQL
    cur.execute("SELECT * FROM users")
    data = cur.fetchall() # Mengambil semua baris hasil query
    return render_template('users.html', users=data) # Tampilkan halaman users dengan data pengguna

@app.route('/add_user', methods=['POST']) # Route ini akan menangani permintaan POST dari form tambah pengguna
# Fungsi ini akan menangani permintaan POST dari form tambah pengguna
def add_user():
    username = request.form['username'] # Mengambil username dari form
    password = request.form['password'] # Mengambil password dari form
    role = request.form.get('role')  # Akan bernilai None jika tidak ada
    if role not in ['admin', 'user']: # Validasi role
        role = 'guest' # Jika role tidak valid, set role ke user
    password_hash = hashlib.md5(password.encode()).hexdigest() # Hash password menggunakan MD5
    cur = mysql.connection.cursor() # Mengambil cursor dari koneksi MySQL
    cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", (username, password_hash, role  ))    # Menyimpan data pengguna ke database
    mysql.connection.commit() # Menyimpan perubahan ke database
    return redirect(url_for('users')) # Redirect ke halaman users

@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cursor.fetchone()
        print("user:", user[4])  # Debugging: cetak data pengguna yang diambil


    
    if request.method == 'POST':
        name = request.form['name'] # Mengambil nama dari form
        is_enabled = request.form.get('is_enabled') # Mengambil status enabled dari form
        username = request.form['username'] # Mengambil username dari form
        password = request.form['password'] # Mengambil password dari form
        password_hash = hashlib.md5(password.encode()).hexdigest() # Hash password menggunakan MD5
        cur = mysql.connection.cursor() # Mengambil cursor dari koneksi MySQL
        cur.execute("UPDATE users SET name = %s , username = %s, password = %s, is_enable = %s WHERE id = %s ", (name, username, password_hash, is_enabled,id ))    # Menyimpan data pengguna ke database
        mysql.connection.commit() # Menyimpan perubahan ke database
        return redirect(url_for('users')) # Redirect ke halaman users
    else:
        return render_template('users_edit.html', user=user)


@app.route('/delete_user/<int:id>') # Route ini akan menangani permintaan untuk menghapus pengguna
def delete_user(id):   # Fungsi ini akan menangani permintaan untuk menghapus pengguna
    cur = mysql.connection.cursor() # Mengambil cursor dari koneksi MySQL
    cur.execute("DELETE FROM users WHERE id=%s", (id,)) # Menghapus pengguna dari database
    mysql.connection.commit() # Menyimpan perubahan ke database
    return redirect(url_for('users')) # Redirect ke halaman users

@app.route('/attendance') # Route untuk halaman kehadiran
# Fungsi ini akan menangani permintaan ke halaman kehadiran
def attendance():
    cur = mysql.connection.cursor() # Mengambil cursor dari koneksi MySQL
    cur.execute("SELECT * FROM attendance") # Menggunakan cursor untuk mengeksekusi query SQL
    data = cur.fetchall() # Mengambil semua baris hasil query
    return render_template('attendance.html', data=data) # Tampilkan halaman kehadiran dengan data kehadiran
 
 # Route untuk menambahkan kehadiran
# Route ini akan menangani permintaan POST dari form tambah kehadiran
@app.route('/add_attendance', methods=['POST'])
# Fungsi ini akan menangani permintaan POST dari form tambah kehadiran
def add_attendance():
    name = request.form['name'] # Mengambil nama dari form
    status = request.form['status'] # Mengambil status dari form
    # Menggunakan cursor untuk mengeksekusi query SQL
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO attendance (name, status) VALUES (%s, %s)", (name, status)) # Menyimpan data kehadiran ke database
    mysql.connection.commit() # Menyimpan perubahan ke database
    return redirect(url_for('attendance')) # Redirect ke halaman kehadiran

# Route untuk menghapus kehadiran
@app.route('/chart') # Route untuk halaman grafik
# Fungsi ini akan menangani permintaan ke halaman grafik
def chart():
    cur = mysql.connection.cursor() # Mengambil cursor dari koneksi MySQL
    # Menggunakan cursor untuk mengeksekusi query SQL
    cur.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status") 
    result = cur.fetchall()    # Mengambil semua baris hasil query
    # Mengambil label dan nilai dari hasil query
    labels = [row[0] for row in result]
    values = [row[1] for row in result]

    plt.clf() # Membersihkan grafik sebelumnya
    plt.bar(labels, values, color='skyblue')  # Membuat grafik batang
    plt.title('Rekap Kehadiran') # Judul grafik
    img = io.BytesIO() # Membuat objek BytesIO untuk menyimpan gambar
    plt.savefig(img, format='png') # Menyimpan grafik ke objek BytesIO
    img.seek(0) # Mengatur posisi pointer ke awal objek BytesIO
    plot_url = base64.b64encode(img.getvalue()).decode() # Mengencode gambar ke format base64
    return render_template('chart.html', plot_url=plot_url) # Tampilkan halaman grafik dengan gambar grafik

if __name__ == '__main__': # Jika file ini dijalankan langsung 
    # app.run() adalah metode untuk menjalankan aplikasi Flask
    # debug=True adalah parameter untuk menjalankan aplikasi dalam mode debug
    # debug=True akan menampilkan pesan kesalahan dan memperbarui aplikasi secara otomatis saat ada perubahan
    app.run(debug=True) # Menjalankan aplikasi Flask dalam mode debug
# Mode debug akan menampilkan pesan kesalahan dan memperbarui aplikasi secara otomatis saat ada perubahan
# Pastikan untuk mengganti password database sesuai dengan yang Anda gunakan
