from flask import Flask, redirect
import logging
import sqlite3
import webuntis

app = Flask("UnitFilter")
databaseName = 'database.db'
database = 0

@app.route("/")
def root():
    return redirect("/login")

@app.route("/login")
def login():
    return "login page"

@app.route("/register")
def register():
    return "Register page"

@app.route("/timetable")
def timetable():
    return "The Timetable"


def initDB():
    logging.info("Initializing database...")

    connection = sqlite3.connect(databaseName)
    createTableCode = '''CREATE TABLE IF NOT EXISTS userdata (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
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
    initDB()
    database = sqlite3.connect(databaseName)
    app.run(port=8888)