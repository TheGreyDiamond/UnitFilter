from flask import Blueprint, redirect, render_template, request, session
import sqlite3
import config

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