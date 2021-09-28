from flask import Flask, redirect, render_template, request
import logging
import sqlite3
import webuntis

app = Flask("UnitFilter")
databaseName = 'database.db'
database, cur = 0

@app.route("/")
def root():
    return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
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
            ## incorrect username
            error = 'Invalid Username. Please try again.'

    return render_template('login.html', error=error)

@app.route("/register", methods=['GET', 'POST'])
def register():
    return "Register page"

@app.route("/timetable")
def timetable():
    return "The Timetable"


def initDB():
    logging.info("Initializing database...")

    connection = sqlite3.connect(databaseName)
    createTableCode = '''CREATE TABLE IF NOT EXISTS userdata (
        id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        e_mail          VARCHAR (255) UNIQUE,
        password_hash   VARCHAR (255),
        subjects        VARCHAR (255),
        class_code      VARCHAR (255),
        class_password  VARCHAR (255));'''

    cursor = connection.cursor()
    cursor.execute(createTableCode)
    connection.commit()
    cursor.close()


if __name__ == '__main__':
    global database, cur
    initDB()
    database = sqlite3.connect(databaseName)
    cur = database.cursor()
    app.run(port=8888)