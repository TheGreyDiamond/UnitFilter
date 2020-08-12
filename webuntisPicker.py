import webuntis, os, tornado.web, tornado.ioloop, logging, datetime, time

se = webuntis.Session(
    username='JgstEF',
    password='Doruwiwilu1',
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
temp = ""
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

def parseTimegrid(se):
    tiObj = {}
    tiObj['startTime'] = ["".join(list(i.start.isoformat())[0:-3]) for i in se.timegrid_units()[0].time_units]
    tiObj['endTime'] = ["".join(list(i.end.isoformat())[0:-3]) for i in se.timegrid_units()[0].time_units]
    return(tiObj)

def work(row2, out):
    global rowcount, rowRam, temp
    print(rowcount)
    if rowcount >= 5:
        row = rowRam
    else:
        row = row2
    rowcount -=-1
    to = ""
    state = None
    print(rowcount)
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
    rowRam = temp

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
        self.render("index.html", data = outify, datum = weekdayL, roomData = outF, roomStates = outFState, sel = selected)

def make_app():
    settings = dict(
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        template_path=os.path.join(os.path.dirname(__file__), "templates")
    )
    data = "Test"
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/update_kurse", updateCallback),
    ], static_path=os.path.join(os.path.dirname(__file__), "static"),template_path=os.path.join(os.path.dirname(__file__), "templates"))

if __name__ == "__main__":
    io_loop = tornado.ioloop.IOLoop.current()
    app = make_app()
    app.listen(8888)
    finalData = webU(wantedDay)
    print("Starting server")
    tornado.ioloop.IOLoop.current().start()