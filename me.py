from flask import Blueprint, redirect, render_template, request, session
import sqlite3
import config
import webuntis


databaseName = config.databaseName

userpages = Blueprint('me', __name__, template_folder='templates/me')


@userpages.route('/me')
def me():
    return redirect('/me/timetable')

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

    return render_template("timetable.html")