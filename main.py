from flask import Flask, redirect, render_template, request
import logging
import sqlite3
import webuntis

app = Flask("UnitFilter")
databaseName = 'database.db'
database = 0
cur = 0

@app.route("/")
def root():
    return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        database = sqlite3.connect(databaseName)
        cur = database.cursor()

        email = request.form['email']
        password = request.form['password']

        if email in cur.execute('SELECT e_mail FROM userdata'):
            ## correct username
            if password == cur.execute('SELECT password_has FROM userdata WHERE e_mail="{email}"'):
                ## correct password/credentials
                return redirect("/timetable")
            else:
                ## wrong password
                error = 'Invalid Password. Please try again.'
        else:
            ## incorrect email
            error = 'Invalid Email-Address. Please try again.'

    return render_template('login.html', error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
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

        if email in cur.execute('SELECT e_mail FROM userdata'):
            error += 'Email-Adress already used\n'
        
        if school not in cur.execute('SELECT school FROM schooldata'):
            error += 'School not found\n'
        
        if password != password2:
            error += 'Passwords don\'t match\n'

        if classCode not in cur.execute(f'SELECT class FROM schooldata WHERE school={school}'):
            error += 'Class not found or not supported\n'
        elif classPass not in cur.execute(f'SELECT password FROM schooldata WHERE school={school} AND class={classCode}'):
            error += 'Invalid Password\n'

        # check for password security
        if len(password) < 6:
            error += 'Your password needs to be at least 6 characters long'

    return render_template('register.html', error=error)

@app.route('/updateCourseSelection')
def updateCourseSelection():
    return 'nothing here yet'


@app.route("/timetable")
def timetable():
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
        school          VARCHAR (255),
        class   VARCHAR (255),
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

    app.run(port=8888)