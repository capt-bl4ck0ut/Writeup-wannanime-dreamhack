from flask import Flask, render_template, request, url_for, redirect, session
import secrets
import pymysql.cursors
import math
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(20)

def get_conn():
    return pymysql.connect(
        host='localhost',
        user=os.getenv('DB_USER', 'winky'),
        password=os.getenv('DB_PASSWORD', 'fake_db_password'),
        database=os.getenv('DB_NAME', 'wannanime'),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.get('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if not username or not password:
            return render_template('error.html', error_message='Username and password are required')
        if len(username) > 100 or len(password) > 100:
            return render_template('error.html', error_message='Username and password are too long')
        conn = None
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username=%s', (username,))
            if cursor.fetchone():
                return render_template('error.html', error_message='Username already exists')
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)',(username, password))
            conn.commit()
        except Exception as e:
            print(f"Registration error: {e}")
            return render_template('error.html', error_message='Registration error')
        finally:
            if conn is not None:
                conn.close()
                
        return render_template('success.html', success_message='Registration successful')
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if not username or not password:
            return render_template('error.html', error_message='Username and password are required')
        conn = None
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute('SELECT username, password, role FROM users WHERE username=%s', (username,))
            user = cursor.fetchone()
            if not user:
                return render_template('error.html', error_message='Username does not exist')
            if user['password'] != password:
                return render_template('error.html', error_message='Incorrect username or password')
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('error.html', error_message='Login error')
        finally:
            if conn is not None:
                conn.close()
    return render_template('login.html')

@app.get('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    try:
        page = int(request.args.get('page', 0))
    except Exception:
        page = 0
    try:
        keyword = request.args.get('keyword', '').strip().lower()
    except Exception:
        keyword = ''
    conn = None
    count = 0
    try:
        conn = get_conn()
        cursor = conn.cursor()
        if page < 0:
            page = 0
        size = 10
        offset = page * size
        if ("'" in keyword):
            return render_template('not_found.html') 
        if (keyword == ''):
            count = math.ceil(cursor.execute("SELECT * FROM anime") / size)
        else:
            count = math.ceil(cursor.execute(f"SELECT * FROM anime WHERE LOWER(title) REGEXP '{keyword}' or LOWER(description) REGEXP '{keyword}'") / size)
        cursor.scroll(offset, mode='absolute')
        result = cursor.fetchmany(size)
    except Exception:
        return render_template('not_found.html')
    return render_template('dashboard.html', result=result, page=page, count=count, keyword=keyword)

@app.get('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.get('/admin')
def admin():
    if ('username' not in session or session['username'] != 'admin'):
        return 'You are not admin'
    filename = request.args.get('filename', None)

    if filename is None:
        return 'No filename provided', 400

    while '../' in filename:
        filename = filename.replace('../', '')

    return open(os.path.join('files/', filename),'rb').read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)