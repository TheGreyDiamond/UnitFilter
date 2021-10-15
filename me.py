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
        
    return 'nothing here yet'

@userpages.route("/me/timetable")
def timetable():
    ## check if user is not already logged in and redirect to timetable if that is the case
    if 'username' not in session:
        return redirect("/login")
    
    ## check for course selection and redirect, if no courses are selected
    cur = sqlite3.connect(databaseName).cursor()
    cur.execute(f'SELECT class_code FROM userdata WHERE e_mail={session["username"]}')
    if cur.fetchall()[0][0] == None:
        return redirect("/updateCourseSelection")

    return "The Timetable"