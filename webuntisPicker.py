import webuntis, os, tornado.web, tornado.ioloop, logging, datetime, time, sqlite3

untisPasswort = 'Doruwiwilu1'

se = webuntis.Session(
    username='JgstEF',
    password=untisPasswort,
    server='tritone.webuntis.com',
    school='gym_remscheid',
    useragent='Soeren spielt mit der API'
)

logging.basicConfig(level=logging.WARN)


outify = []
weekdayL = ""
outF = []
outFState = []
rowRam = ""
rowcount = 0
finalData = ""

# Time defintions
today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=7)
friday = monday + datetime.timedelta(days=4) + datetime.timedelta(days=7)


# Settings
wantedDay = monday
kursDict = {"soeren": ["CH2", "EK1", "IF2", "E52", "GE2", "KU1", "ER1", "C01", "D2", "M2", "PH1", "SP1"],
            "joshua": ["CH2", "PA2", "IF2", "E53", "L61", "MU1", "ER1", "C01", "D3", "M3", "GE3", "SP1"]}
kurse = kursDict["soeren"] ## Defaults to soeren
selected = "soeren"


def initDB():
    print("Starting DB init")
    f = open("ready.lock", "w+")
    li = f.readlines()
    done = None
    for el in li:
        if("setup done" in el):
            done = True
            break
        else:
            print("Init started")
            print(done)
            f.write("setup done")
            sqliteConnection = sqlite3.connect('SQL_LITE_userData.db')
            mysqlCreateCode = '''CREATE TABLE `userdata` (
	                        `id` INT NOT NULL AUTO_INCREMENT,
	                        `e_mail` VARCHAR(255),
	                        `password_hash` VARCHAR(255),
	                        `class_code` VARCHAR(255),
	                        PRIMARY KEY (`id`)
                            );'''
            cursor = sqliteConnection.cursor()
            cursor.execute(mysqlCreateCode)
            cursor.close()

    f.close()

def parseTimegrid(se):
    tiObj = {}
    tiObj['startTime'] = ["".join(list(i.start.isoformat())[0:-3]) for i in se.timegrid_units()[0].time_units]
    tiObj['endTime'] = ["".join(list(i.end.isoformat())[0:-3]) for i in se.timegrid_units()[0].time_units]
    return(tiObj)

def work(row2, out):
    global rowcount, rowRam
    if rowcount >= 5:
        row = rowRam
    else:
        row = row2
    rowcount -=-1
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
                                out +="<s>"
                                out += proc
                                try:
                                    to += proc + " " + str(period.rooms[0])
                                except:
                                    to += proc + " " + str(period.rooms)
                                state = True
                                out +="</s>" 
                            else:
                                out += proc
                                out += period.code + " "
                                to += proc +  " ?:" + period.code
                        else:
                            out += proc + " "
                            out += str(period.rooms[0])
                            to += proc + " " + str(period.rooms[0])
                            state = False
    elif rowcount >= 5:
        to += "-Mittagspause-"
    outF.append(to) 
    outFState.append(state)
    rowRam = row2

def webU(wantedDay = today):
    print("Updating table...", end = "")
    global outify, weekdayL, outF, outFState, rowRam
    with se.login() as s:
        timeGr = parseTimegrid(s)
        klasse = s.klassen().filter(name='EF')[0]
        table = s.timetable(klasse=klasse, start=wantedDay, end=wantedDay).to_table()
        weekdayL = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][wantedDay.weekday()]
        out = ""
        times = []
        i = 0
        while i < len(timeGr["startTime"]):
            outify.append(timeGr["startTime"][i] + " - " + timeGr["endTime"][i])
            i-=-1
        for time, row in table:
            work(row, out)
        work(row, out)
    print("[DONE]")                           
    return(out)

# Webserver
class updateCallback(tornado.web.RequestHandler):
    def get(self):
        global kurse, finalData, outify, weekdayL, outF, outFState, selected, rowRam, rowcount, temp
        self.write("<script> window.close(); </script>")
        kurse = kursDict[self.get_argument("kurs")]
        selected = self.get_argument("kurs")
        print("Changed selection", kurse)
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
        global finalData, outify, weekdayL, outF, outFState
        self.render("main.html", data = outify, datum = weekdayL, roomData = outF, roomStates = outFState, sel = selected)

class defaultHandler(tornado.web.RequestHandler):
    def __init__(self, arg2, arg3):
        print("Called default handler")
        self.arg2 = arg2
        self.arg3 = arg3

    def get(self):
        self.write("404 - my thing")
    def request(self):
        self.write("404 - my thing")

class LoginPage(tornado.web.RequestHandler):
    def get(self):
        global finalData, outify, weekdayL, outF, outFState
        self.render("index.html", data = outify, datum = weekdayL, roomData = outF, roomStates = outFState, sel = selected)

    def post(self):
        typeI = self.get_argument('type')
        if(typeI == "login"):
            email = self.get_argument('email')
            password = self.get_argument('pass')
            print("[AUTH] Type: LOGIN E-Mail:", email, "Password:", password)
        self.write("Okay")

class newAccountHandler(tornado.web.RequestHandler):
    def get(self):
        global finalData, outify, weekdayL, outF, outFState
        self.render("newAccount.html", data = outify, datum = weekdayL, roomData = outF, roomStates = outFState, sel = selected)

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
                else:
                    errCode.append("PASS_UNSAME")
            else:
                errCode.append("PASS_UNTISWRONG")
                untisOk = False
            authStringInfo  = "[AUTH] Type: REGISTER E-Mail: " + email + " Password: " + password + " Password2: " + password2 + " Units password: " + str(untisPasswortL) + " ErrorCodes: " + str(errCode)
            authStringInfo.encode("utf-8")
            print(authStringInfo)
        self.write(authStringInfo)

def make_app():
    data = "Test"
    return tornado.web.Application([
        (r"/main", MainHandler),
        (r"/update_kurse", updateCallback),
        (r"/", LoginPage),
        (r"/register", newAccountHandler),
    ], static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    default_handler_class=defaultHandler)

if __name__ == "__main__":
    initDB()
    io_loop = tornado.ioloop.IOLoop.current()
    app = make_app()
    app.listen(8888)
    finalData = webU(wantedDay)
    print("Starting server")
    tornado.ioloop.IOLoop.current().start()