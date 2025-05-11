from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
import matplotlib.pyplot as plt
import io
import base64
import hashlib

app = Flask(__name__)
app.secret_key = 'secretkey123'

# Konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'toor'
app.config['MYSQL_DB'] = 'kehadiran_db'

mysql = MySQL(app)

@app.route('/')
def index():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.md5(password.encode()).hexdigest()

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password_hash))
    user = cur.fetchone()
    if user:
        session['loggedin'] = True
        session['username'] = user[1]
        session['role'] = user[3]
        return redirect(url_for('dashboard'))
    return render_template('login.html', error='Invalid credentials')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/users')
def users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    return render_template('users.html', users=data)

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    password = request.form['password']
    password_hash = hashlib.md5(password.encode()).hexdigest()
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password_hash))
    mysql.connection.commit()
    return redirect(url_for('users'))

@app.route('/delete_user/<int:id>')
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('users'))

@app.route('/attendance')
def attendance():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM attendance")
    data = cur.fetchall()
    return render_template('attendance.html', data=data)

@app.route('/add_attendance', methods=['POST'])
def add_attendance():
    name = request.form['name']
    status = request.form['status']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO attendance (name, status) VALUES (%s, %s)", (name, status))
    mysql.connection.commit()
    return redirect(url_for('attendance'))

@app.route('/chart')
def chart():
    cur = mysql.connection.cursor()
    cur.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status")
    result = cur.fetchall()
    labels = [row[0] for row in result]
    values = [row[1] for row in result]

    plt.clf()
    plt.bar(labels, values, color='skyblue')
    plt.title('Rekap Kehadiran')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return render_template('chart.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
