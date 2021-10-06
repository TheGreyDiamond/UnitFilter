from flask import Blueprint, redirect, render_template, request, session
import sqlite3
import config

databaseName = config.databaseName

adminpage = Blueprint('adminpage', __name__, template_folder='templates/admin')


@adminpage.route("/admin")
def adminIndex():
    return render_template('index.html')


@adminpage.route("/admin/users")
def users():
    return render_template('users.html')


@adminpage.route("/admin/classes")
def classes():
    return render_template('classes.html')


@adminpage.route("/admin/classes/addClass", methods=['GET', 'POST'])
def addClass():
    if request.method == 'POST':
        try:
            database = sqlite3.connect(databaseName)
            cur = database.cursor()

            server = request.form['email']
            school = request.form['password']
            classname = request.form['repeat_password']
            password = request.form['school']

            cur.execute(f'''INSERT INTO schooldata (server, school, school, class, password)
                        VALUES ("{server}", "{school}", "{classname}", "{password}");''')
            database.commit()
            cur.close()
            
            return render_template('addClass.html', message="Success")
        except Exception as e:
            return render_template('addClass.html', message=e)
    
    return render_template('addClass.html', message=None)

