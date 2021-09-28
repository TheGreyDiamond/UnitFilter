from flask import Flask, redirect
import webuntis

app = Flask("UnitFilter")

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


if __name__ == '__main__':
    app.run(port=8888)