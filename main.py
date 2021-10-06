from flask import Flask, redirect, render_template, request, session
import logging
import sqlite3
import hashlib
import webuntis

app = Flask("UnitFilter")
app.secret_key = b'~p\xbc\xd9\x1b\x84\xdd\xe9-w\xd4ma\xe8GZK\xe3\x18foP\x9d\xe0C\x87\xb3\x06&\x1a\xad+'

databaseName = 'database.db'
database = 0
cur = 0

@app.route("/")
def root():
    ## check if user is already logged in and redirect to timetable if that is the case
    if 'username' in session:
        return redirect("/timetable")
    return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    ## check if user is already logged in and redirect to timetable if that is the case
    if 'username' in session:
        return redirect("/timetable")

    error = None

    if request.method == 'POST':
        database = sqlite3.connect(databaseName)
        cur = database.cursor()

        email = request.form['email']
        password = request.form['password']

        cur.execute('SELECT e_mail FROM userdata;')
        if any(email in i for i in cur.fetchall()):
            ## correct username

            # compare password hash
            hasher = hashlib.md5()
            hasher.update(password.encode('utf-8'))

            cur.execute(f'SELECT password_hash FROM userdata WHERE e_mail="{email}";')
            if hasher.hexdigest() in cur.fetchall()[0]:
                ## correct password/credentials
                cur.execute(f'SELECT id FROM userdata WHERE e_mail="{email}";')
                session['userID'] = cur.fetchall()[0][0]
                session['username'] = email

                return redirect("/timetable")
            else:
                ## wrong password
                error = 'Invalid Password. Please try again.'
        else:
            ## incorrect email
            error = 'Invalid Email-Address. Please try again.'

    return render_template('login.html', error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
def register():
    ## check if user is already logged in and redirect to timetable if that is the case
    if 'username' in session:
        return redirect("/timetable")

    error = ''

    if request.method == 'POST':
        database = sqlite3.connect(databaseName)
        cur = database.cursor()

        email = request.form['email']
        password = request.form['password']
        password2 = request.form['repeat_password']
        school = request.form['school']
        classCode = request.form['class']
        classPass = request.form['class_password']

        cur.execute('SELECT e_mail FROM userdata;')
        if email in cur.fetchall():
            error += 'Email-Adress already used\n'
        
        cur.execute('SELECT school FROM schooldata;')
        if school not in cur.fetchall()[0]:
            error += 'School not found\n'
        
        if password != password2:
            error += 'Passwords don\'t match\n'

        cur.execute(f'SELECT class FROM schooldata WHERE school="{school}";')
        if not any(classCode in i for i in cur.fetchall()):
            error += 'Class not found or not supported\n'
        else:
            cur.execute(f'SELECT password FROM schooldata WHERE school="{school}" AND class="{classCode}";')
            if classPass not in cur.fetchall()[0]:
                error += 'Invalid Class Password\n'

        # check for password security
        if len(password) < 6:
            error += 'Your password needs to be at least 6 characters long'

        # toastbrot mit annanas drauf
        # if no errors, save user and redirect to subject selection
        if error == '':
            hasher = hashlib.md5()
            hasher.update(password.encode('utf-8'))
            passwordhash = hasher.hexdigest()
            cur.execute(f'''INSERT INTO userdata (e_mail, password_hash, school, class_code, class_password)
                        VALUES ("{email}", "{passwordhash}", "{school}", "{classCode}", "{classPass}");''')
            database.commit()
            cur.close()
            print(f'Created new user with email-address "{email}"')

            return redirect('/updateCourseSelection')

    return render_template('register.html', error=error)

@app.route('/updateCourseSelection')
def updateCourseSelection():
    return 'nothing here yet'


@app.route("/timetable")
def timetable():
    ## check if user is not already logged in and redirect to timetable if that is the case
    if 'username' not in session:
        return redirect("/login")

    return "The Timetable"


def initDB():
    logging.info("Initializing database...")

    connection = sqlite3.connect(databaseName)
    createUserdataTableCode = '''CREATE TABLE IF NOT EXISTS userdata (
        id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        e_mail          VARCHAR (255) UNIQUE,
        password_hash   VARCHAR (255),
        subjects        VARCHAR (255),
        school          VARCHAR (255),
        class_code      VARCHAR (255),
        class_password  VARCHAR (255));'''
    
    createSchoolsTableCode = '''CREATE TABLE IF NOT EXISTS schooldata (
        id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        server          VARCHAR (255),
        school          VARCHAR (255),
        class           VARCHAR (255),
        password        VARCHAR (255));'''

    cursor = connection.cursor()
    cursor.execute(createUserdataTableCode)
    cursor.execute(createSchoolsTableCode)
    connection.commit()
    cursor.close()


if __name__ == '__main__':
    initDB()

    database = sqlite3.connect(databaseName)
    cur = database.cursor()
    cur.execute('select * from schooldata')
    print(cur.fetchall())
    cur.execute('select * from userdata')
    print(cur.fetchall())

    app.run(port=8888)