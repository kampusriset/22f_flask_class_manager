from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'super_secret_key_123'  # Pastikan ini lebih kompleks!
app.permanent_session_lifetime = timedelta(days=1)  # Menjaga sesi tetap aktif selama 1 hari

# Konfigurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'passwordbaru'
app.config['MYSQL_DB'] = 'python-flask-mysql-crud-app-main'

mysql = MySQL(app)

# Route untuk halaman utama
@app.route('/')
def index():
    print("Session:", session)  # Cek isi session
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        data = cur.fetchall()
        cur.close()
        print("Data dari database:", data)  # Debugging apakah data terbaca
        return render_template('index.html', students=data)
    return redirect(url_for('login'))

# Route untuk register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        if user:
            flash('Username already exists!', 'danger')
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            flash('Registration successful! Please log in.', 'success')
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Route untuk login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[2], password):
            session['loggedin'] = True
            session['username'] = user[1]
            session.permanent = True  # Supaya session tidak hilang
            print("Session setelah login:", session)  # Debugging session
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')


# Route untuk logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# CRUD Operations
@app.route('/insert', methods=['POST'])
def insert():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
        mysql.connection.commit()
        cur.close()

        flash("Student Added Successfully")
        return redirect(url_for('index'))

@app.route('/delete/<string:id_data>', methods=['GET'])
def delete(id_data):
    if 'loggedin' in session:
        flash("Record Has Been Deleted Successfully")
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM students WHERE id=%s", (id_data,))
        mysql.connection.commit()
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route('/update', methods=['POST'])
def update():
    if request.method == "POST":
        id = request.form.get('id')
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')

        if not id or not name or not email or not phone:
            flash("All fields are required!", "danger")
            return redirect(url_for('index'))

        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                UPDATE students
                SET name=%s, email=%s, phone=%s
                WHERE id=%s
            """, (name, email, phone, id))
            mysql.connection.commit()
            flash("Student Updated Successfully", "success")
        except Exception as e:
            flash(f"Error updating student: {str(e)}", "danger")
        finally:
            cur.close()

        return redirect(url_for('index'))  # ✅ Tambahkan return ini

    flash("Invalid request method", "danger")
    return redirect(url_for('index'))  # ✅ Handle jika bukan POST



if __name__ == "__main__":
    app.run(debug=True)
