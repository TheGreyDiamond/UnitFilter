from flask import Blueprint, redirect, render_template, request, session
import sqlite3
import config
import webuntis

databaseName = config.databaseName

api = Blueprint('api', __name__, template_folder='templates/api')


@api.route("/api/getAllClasses")
def getAllClasses():
    database = sqlite3.connect(databaseName)
    cur = database.cursor()
    cur.execute("SELECT * FROM schooldata")
    return str(cur.fetchall())

@api.route("/api/getAllUsers")
def getAllUsers():
    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    cur.execute("SELECT * FROM userdata")
    userdata = cur.fetchall()

    return str(userdata)

@api.route('/api/getAvailableSubjects')
def getAvailableSubjects():
    ## check if user is logged in
    if 'username' not in session:
        return

    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    cur.execute(f"SELECT school,class_code FROM userdata WHERE e_mail='{session['username']}'")
    data = cur.fetchall()
    school = data[0][0]
    classname = data[0][1]

    cur.execute(f"SELECT server,password FROM schooldata WHERE school='{school}' AND class='{classname}'")
    data = cur.fetchall()
    server = data[0][0]
    password = data[0][1]

    subjects = []

    untisSession = webuntis.Session(
        server=f'{server}.webuntis.com',
        school=school,
        username=classname,
        password=password,
        useragent=config.untisAgentName
    )

    with untisSession.login():
        klasse=untisSession.klassen().filter(name=classname)[0]
        timetable = untisSession.timetable(klasse=klasse, start=20211008, end=20211016)

        for k in timetable:
            if len(k.subjects):
                subjects.append(k.subjects[0].name)

    return str(set(subjects))