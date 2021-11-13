from flask import Blueprint, redirect, render_template, request, session, jsonify
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
    return jsonify(cur.fetchall())

@api.route("/api/getAllUsers")
def getAllUsers():
    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    cur.execute("SELECT * FROM userdata")
    userdata = cur.fetchall()

    return jsonify(userdata)

@api.route("/api/removeUser")
def removeUser():
    if request.args:
        id = request.args.get('id')
    else: return "No param given"

    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    cur.execute(f"DELETE FROM userdata WHERE id='{id}'")
    database.commit()
    cur.close()

    return "Deletion Successful"

@api.route('/api/getAvailableSubjects')
def getAvailableSubjects():
    ## check if user is logged in
    if 'username' not in session:
        return

    ## init database
    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    ## gain school and class code for given user
    cur.execute(f"SELECT school,class_code FROM userdata WHERE e_mail='{session['username']}'")
    data = cur.fetchall()
    school = data[0][0]
    classname = data[0][1]

    ## get server and password of the given school
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

@api.route("/api/getTimegridUnits")
def getTimegridUnits():
    ## check if user is logged in
    if 'username' not in session:
        return

    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    ## check for course selection and redirect, if no courses are selected
    cur.execute(f'SELECT subjects FROM userdata WHERE e_mail={session["username"]}')
    userSubjects = cur.fetchall()[0][0]
    if userSubjects != None:
        userSubjects = userSubjects.split(",")


    ## gain school and class code for given user
    cur.execute(f"SELECT school,class_code FROM userdata WHERE e_mail='{session['username']}'")
    data = cur.fetchall()
    school = data[0][0]
    classname = data[0][1]

    ## get server and password of the given school
    cur.execute(f"SELECT server,password FROM schooldata WHERE school='{school}' AND class='{classname}'")
    data = cur.fetchall()
    server = data[0][0]
    password = data[0][1]

    untisSession = webuntis.Session(
        server=f'{server}.webuntis.com',
        school=school,
        username=classname,
        password=password,
        useragent=config.untisAgentName
    )

    with untisSession.login():
        timegrid = untisSession.timegrid_units()

    return str(timegrid)

@api.route("/api/getFilteredTimetable")
def getFilteredTimetable(): 
    ## check if user is logged in
    if 'username' not in session:
        return

    ## init database
    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    ## check for course selection and redirect, if no courses are selected
    cur.execute(f'SELECT subjects FROM userdata WHERE e_mail={session["username"]}')
    userSubjects = cur.fetchall()[0][0]
    if userSubjects != None:
        userSubjects = userSubjects.split(",")


    ## gain school and class code for given user
    cur.execute(f"SELECT school,class_code FROM userdata WHERE e_mail='{session['username']}'")
    data = cur.fetchall()
    school = data[0][0]
    classname = data[0][1]

    ## get server and password of the given school
    cur.execute(f"SELECT server,password FROM schooldata WHERE school='{school}' AND class='{classname}'")
    data = cur.fetchall()
    server = data[0][0]
    password = data[0][1]

    untisSession = webuntis.Session(
        server=f'{server}.webuntis.com',
        school=school,
        username=classname,
        password=password,
        useragent=config.untisAgentName
    )

    filteredTimetable = []

    with untisSession.login():
        klasse=untisSession.klassen().filter(name=classname)[0]
        timetable = untisSession.timetable(klasse=klasse, start=20211008, end=20211016)

        for lesson in timetable:
            if len(lesson.subjects):
                if lesson.subjects[0].name in userSubjects:
                    filteredTimetable.append(lesson)
    

        jsonTimetable = []

        for lesson in filteredTimetable:
            subject = lesson.subjects[0]
            print(lesson)
            lessonDict = {
                'code':lesson.code,
                'start':str(lesson.start),
                'end':str(lesson.end),
                'subject':{'id':subject.id,'name':subject.name,'longName':subject.long_name},
                'original_rooms':lesson.original_rooms,
                'original_teachers':lesson.original_teachers,
                'rooms':[{'id':x.id,
                        'name':x.name,
                        'longName':x.long_name} for x in lesson.rooms],
                #'teachers':lesson.teachers if (lesson.code != "cancelled") else None,
                'type':lesson.type
            }
            jsonTimetable.append(lessonDict)
    
    return str(jsonTimetable)

    