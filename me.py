from flask import Blueprint, redirect, render_template, request, session
import sqlite3
import config
import webuntis


databaseName = config.databaseName

userpages = Blueprint('me', __name__, template_folder='templates/me')


@userpages.route('/me/updateCourseSelection')
def updateCourseSelection():
    ## check if user is not already logged in and redirect to timetable if that is the case
    if 'username' not in session:
        return redirect("/login")

    return render_template("updateCourseSelection.html")

@userpages.route("/me/timetable")
def timetable():
    ## check if user is not already logged in and redirect to timetable if that is the case
    if 'username' not in session:
        return redirect("/login")
    
    ## init database
    database = sqlite3.connect(databaseName)
    cur = database.cursor()

    ## check for course selection and redirect, if no courses are selected
    cur.execute(f'SELECT subjects FROM userdata WHERE e_mail={session["username"]}')
    userSubjects = cur.fetchall()[0][0]
    if userSubjects == None:
        return redirect("/me/updateCourseSelection")
    else:
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

    return render_template("timetable.html", timetable=filteredTimetable)