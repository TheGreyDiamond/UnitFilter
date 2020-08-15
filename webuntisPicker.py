import webuntis
import os
import tornado.web
import tornado.ioloop
import logging
import datetime
import time
import sqlite3
import hashlib
import re
import random
import string

version = "1.2.3"

untisPasswort = 'Doruwiwilu1'

se = webuntis.Session(
    username='JgstEF',
    password=untisPasswort,
    server='tritone.webuntis.com',
    school='gym_remscheid',
    useragent='Soeren spielt mit der API'
)

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s,%(msecs)d] %(name)s [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S',
                    filename="log.txt",
                    filemode='a')


outify = []
weekdayL = ""
outF = []
outFState = []
rowRam = ""
rowcount = 0
finalData = ""

# Time defintions
today = datetime.date.today()
monday = today - \
    datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=7)
friday = monday + datetime.timedelta(days=4) + datetime.timedelta(days=7)


# Settings
wantedDay = monday
kursDict = {"soeren": ["CH2", "EK1", "IF2", "E52", "GE2", "KU1", "ER1", "C01", "D2", "M2", "PH1", "SP1"],
            "joshua": ["CH2", "PA2", "IF2", "E53", "L61", "MU1", "ER1", "C01", "D3", "M3", "GE3", "SP1"]}
kurse = kursDict["soeren"]  # Defaults to soeren
selected = "soeren"


def get_random_alphanumeric_string():
    letters_count = 40
    digits_count = 10
    sample_str = ''.join((random.choice(string.ascii_letters)
                          for i in range(letters_count)))
    sample_str += ''.join((random.choice(string.digits)
                           for i in range(digits_count)))

    # Convert string to list and shuffle it to mix letters and digits
    sample_list = list(sample_str)
    random.shuffle(sample_list)
    final_string = ''.join(sample_list)
    return final_string


def initDB():
    logging.info("Started DB Init Function")
    try:
        f = open("ready.lock", "x")
    except FileExistsError:
        logging.info("No need for a new DB")
    else:
        logging.info("Creating DB")
        sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
        mysqlCreateCode = '''CREATE TABLE userdata (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            e_mail        VARCHAR (255) UNIQUE,
            password_hash VARCHAR (255),
            usr_code    VARCHAR (255) UNIQUE);'''

        mysqlCreateCode2 = '''CREATE TABLE fachKombi (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            usr_code        VARCHAR (255),
            kombi VARCHAR (255),
            class_code    VARCHAR (255));'''

        cursor = sqliteConnection.cursor()
        cursor.execute(mysqlCreateCode)
        cursor.execute(mysqlCreateCode2)
        cursor.close()


def createUser(e_mail, password):
    try:
        sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
        hasher = hashlib.md5()
        passwordEncode = password.encode("utf-8")
        hasher.update(passwordEncode)
        rand = get_random_alphanumeric_string()
        mysqlData = 'INSERT INTO userdata (e_mail, password_hash, usr_code) VALUES ("' + \
            e_mail + '", "' + hasher.hexdigest() + '", "' + rand + '");'
        cursor = sqliteConnection.cursor()
        ret = cursor.execute(mysqlData)
        sqliteConnection.commit()
        cursor.close()
        print("Created new user [DONE]")
        return(True)
    except Exception as ex:
        print("Creation failed!")
        logging.warn("Usercreation failed, error " + str(ex))
        return(False)


def setFachKombo(usrCode, fachs):
    try:
        sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
        mysqlData = 'INSERT INTO fachKombi (usr_code, kombi, class_code) VALUES ("' + \
            usrCode + '", "' + str(fachs) + '", "");'
        cursor = sqliteConnection.cursor()
        ret = cursor.execute(mysqlData)
        sqliteConnection.commit()
        cursor.close()
        print("Set new Fachkombo [DONE]")
        return(True)
    except Exception as ex:
        print("Creation failed!")
        logging.warn("setFachKombo failed, error " + str(ex))
        return(False)


def getFachKombo(usrCode):
    try:
        sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
        mysqlData = 'SELECT kombi FROM fachKombi WHERE usr_code="' + usrCode + '";'
        cursor = sqliteConnection.cursor()
        ret = cursor.execute(mysqlData)
        record = cursor.fetchall()
        cursor.close()
        #print(record[0][0])
        proc = record[0][0]
        proc = proc.strip("[").replace("]", "").replace(
            "'", "").replace(" ", "")
        proc = proc.split(",")
        #print(proc)
        return(proc)
    except Exception as ex:
        logging.warn("getFachKombo failed, error " + str(ex))
        return(False)


def resolve_e_mail(usr_code):
    try:
        sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
        mysqlData = 'SELECT e_mail FROM userdata WHERE usr_code="' + usr_code + '";'
        cursor = sqliteConnection.cursor()
        ret = cursor.execute(mysqlData)
        record = cursor.fetchall()
        cursor.close()
        proc = record[0][0]
        return(proc)
    except Exception as ex:
        logging.warn("resolve_e_mail failed, error " + str(ex))
        return(False)


def checkUser(e_mail, password):
    sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
    hasher = hashlib.md5()
    passwordEncode = password.encode("utf-8")
    hasher.update(passwordEncode)
    mysqlData = 'SELECT password_hash, usr_code FROM userdata WHERE e_mail="' + \
        e_mail.strip("<").strip("'").strip('"') + '";'
    cursor = sqliteConnection.cursor()

    ret = cursor.execute(mysqlData)
    record = cursor.fetchall()
    if(record[0][0] == hasher.hexdigest()):
        cursor.close()
        # usr_code
        return(record[0][1])
    else:
        cursor.close()
        return(False)
    # print(record[0][0])

    #    print("Usercheck failed!")
 #   return(False)


def parseTimegrid(se):
    tiObj = {}
    tiObj['startTime'] = ["".join(list(i.start.isoformat())[0:-3])
                          for i in se.timegrid_units()[0].time_units]
    tiObj['endTime'] = ["".join(list(i.end.isoformat())[0:-3])
                        for i in se.timegrid_units()[0].time_units]
    return(tiObj)


def work(row2, out):
    global rowcount, rowRam
    if rowcount >= 5:
        row = rowRam
    else:
        row = row2
    rowcount -= -1
    to = ""
    state = None
    if rowcount != 5:
        for date, cell in row:
            for period in cell:
                for su in period.subjects:
                    proc = str(su).split(" ")
                    if("VTF" not in proc[1]):
                        proc[0] = proc[0].upper()
                        proc[1] = proc[1].split("k")[1]
                        proc = proc[0] + proc[1]

                    if(proc in kurse):
                        if(period.code != None):
                            if(period.code == "cancelled"):
                                out += "<s>"
                                out += proc
                                try:
                                    to += proc + " " + str(period.rooms[0])
                                except:
                                    to += proc + " " + str(period.rooms)
                                state = True
                                out += "</s>"
                            else:
                                out += proc
                                out += period.code + " "
                                to += proc + " ?:" + period.code
                        else:
                            out += proc + " "
                            try:
                                out += str(period.rooms[0])
                                to += proc + " " + str(period.rooms[0])
                            except:
                                out += "???"
                                to += proc + " " + "???"
                            
                            state = False
    elif rowcount >= 5:
        to += "-Mittagspause-"
    outF.append(to)
    outFState.append(state)
    rowRam = row2


def webU(wantedDay=today):
    logging.info("Updating table")
    #print("Updating table...", end="")
    global outify, weekdayL, outF, outFState, rowRam
    with se.login() as s:
        timeGr = parseTimegrid(s)
        klasse = s.klassen().filter(name='EF')[0]
        table = s.timetable(klasse=klasse, start=wantedDay,
                            end=wantedDay).to_table()
        weekdayL = ["Montag", "Dienstag", "Mittwoch",
                    "Donnerstag", "Freitag"][wantedDay.weekday()]
        out = ""
        times = []
        i = 0
        while i < len(timeGr["startTime"]):
            outify.append(timeGr["startTime"][i] +
                          " - " + timeGr["endTime"][i])
            i -= -1
        for time, row in table:
            work(row, out)
        work(row, out)
    logging.info("Table [DONE]")
    return(out)



# Webserver

class updateCallback(tornado.web.RequestHandler):
    def get(self):
        global kurse, finalData, outify, weekdayL, outF, outFState, selected, rowRam, rowcount, temp
        self.write("<script> window.close(); </script>")
        kurse = kursDict[self.get_argument("kurs")]
        selected = self.get_argument("kurs")
        #print("Changed selection", kurse)
        outify = []
        weekdayL = ""
        outF = []
        outFState = []
        rowRam = ""
        rowcount = 0
        temp = ""
        finalData = webU(wantedDay)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global kurse, finalData, outify, weekdayL, outF, outFState, selected, rowRam, rowcount, temp
        if(self.get_cookie("user")):
            te = getFachKombo(self.get_cookie("user"))
            if(te == False):
                self.render("almostDone.html", errorMsg="")
            else:
                kurse = te
                outify = []
                weekdayL = ""
                outF = []
                outFState = []
                rowRam = ""
                rowcount = 0
                temp = ""
                selected = "custom"
                handOverData = []
                handOverData2 = []
                i = 0
                wantedDay = monday
                while(i <= 4):
                     outify = []
                     weekdayL = ""
                     outF = []
                     outFState = []
                     rowRam = ""
                     rowcount = 0
                     temp = ""
                     selected = "custom"
                     finalData = webU(wantedDay)
                     wantedDay =  wantedDay + datetime.timedelta(days=1)
                     handOverData2.append(outFState)
                     handOverData.append(outF)
                     i-=-1
                usrMail = str(resolve_e_mail(self.get_cookie("user")))
                usrMail = usrMail.encode("utf-8")
                #print(usrMail)
                result = hashlib.md5(usrMail)
                dig = str(result.digest())
                #result = hashlib.md5(resolve_e_mail(self.get_cookie("user").encode("utf-8"))) 
                self.render("main.html", data=outify, datum=today,
                            roomData=handOverData, roomStates=handOverData2, sel=selected, version = version, usrN = dig, mail=str(resolve_e_mail(self.get_cookie("user"))))
        else:
            self.render("index.html", errorMsg="")


class almostDone(tornado.web.RequestHandler):
    def get(self):
        self.render("almostDone.html", errorMsg="")

    def post(self):
        i = 1
        args = []
        try:
            while i <= 13:
                args.append(self.get_argument("a" + str(i)))
                i -= - 1

            # print(args)
            out = []
            for el in args:
                el2 = el.upper()
                # print(len(re.findall("(^E\d)", el2)))
                if(re.search("(^E\d)", el2)):
                    out.append(el2[0] + "5" + el2[1])
                elif(el2 == "0"):
                    pass
                else:
                    out.append(el2)
            usr = self.get_cookie("user")
            setFachKombo(usr, out)
        except Exception as ex:
            print("Missing args", ex)
            self.render("almostDone.html", errorMsg="notAllSet")
        else:
            self.render("redirect.html")


class defaultHandler(tornado.web.RequestHandler):
    def prepare(self):
        # Use prepare() to handle all the HTTP methods
        self.set_status(404)
        self.render("404.html")

class changelogHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("changelog.html")


class logoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.clear_cookie("user")
        self.render("logout.html")

class redirecter(tornado.web.RequestHandler):
    def get(self):
        self.render("redirect.html")

class legal(tornado.web.RequestHandler):
    def get(self):
        self.render("legal.html")

class LoginPage(tornado.web.RequestHandler):
    def get(self):
        global finalData, outify, weekdayL, outF, outFState
        self.render("index.html", errorMsg="")

    def post(self):
        typeI = self.get_argument('type')
        if(typeI == "login"):
            email = self.get_argument('email')
            password = self.get_argument('pass')
            #print("[AUTH] Type: LOGIN E-Mail:", email, "Password:", password)
            chkUser = checkUser(email, password)
            if(checkUser != False):

                self.set_cookie("user", chkUser)
                self.render("redirect.html")
            else:
                self.render("index.html", errorMsg="FAIL")

class newAccountHandler(tornado.web.RequestHandler):
    def get(self):
        global finalData, outify, weekdayL, outF, outFState
        self.render("newAccount.html", errorMsg="")

    def post(self):
        typeI = self.get_argument('type')
        if(typeI == "register"):
            email = self.get_argument('email')
            password = self.get_argument('pass')
            password2 = self.get_argument('pass2')
            untisPasswortL = self.get_argument('untisPass')
            errCode = []
            if(untisPasswortL == untisPasswort):
                untisOk = True
                if(password == password2):
                    passwordSame = True
                    ret = createUser(email, password)
                    if(ret == False):
                        self.render("newAccount.html",
                                    errorMsg="INTERNAL_FAIL")
                    else:
                        self.set_cookie("user", email)
                        self.render("redirect.html")
                else:
                    errCode.append("PASS_UNSAME")
                    self.render("newAccount.html", errorMsg="PASS_UNSAME")
            else:
                errCode.append("PASS_UNTISWRONG")
                self.render("newAccount.html", errorMsg="PASS_UNTISWRONG")
                untisOk = False
            authStringInfo = "[AUTH] Type: REGISTER E-Mail: " + email + " Password: " + password + \
                " Password2: " + password2 + " Units password: " + \
                str(untisPasswortL) + " ErrorCodes: " + str(errCode)
            authStringInfo.encode("utf-8")

def make_app():
    data = "Test"
    return tornado.web.Application([
        (r"/main", MainHandler),
        (r"/update_kurse", updateCallback),
        (r"/", LoginPage),
        (r"/register", newAccountHandler),
        (r"/redirect", redirecter),
        (r"/almost_done", almostDone),
        (r"/legal", legal),
        (r"/changelog", changelogHandler),
        (r"/logout", logoutHandler)
    ], static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        default_handler_class=defaultHandler)


if __name__ == "__main__":
    logging.info("Starting system.")
    initDB()
    io_loop = tornado.ioloop.IOLoop.current()
    app = make_app()
    app.listen(8888)
    finalData = webU(wantedDay)
    logging.info("Starting server")
    print("Starting server")
    tornado.ioloop.IOLoop.current().start()
