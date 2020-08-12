import webuntis, os, tornado.web, tornado.ioloop, logging, datetime, time

kursDict = {"soeren": ["CH2", "EK1", "IF2", "E52", "GE2", "KU1", "ER1", "C01", "D2", "M2", "PH1", "SP1"],
            "joshua": ["CH2", "PA2", "IF2", "E53", "L61", "MU1", "ER1", "C01", "D3", "M3", "GE3", "SP1"]}
kurse = kursDict["soeren"] ## Defaults to soeren
selected = "soeren"


se = webuntis.Session(
    username='JgstEF',
    password='Doruwiwilu1',
    server='tritone.webuntis.com',
    school='gym_remscheid',
    useragent='Soeren spielt mit der API'
)

logging.basicConfig(level=logging.WARN)

def parseTimegrid(se):
    tiObj = {}
    tiObj['startTime'] = ["".join(list(i.start.isoformat())[0:-3]) for i in se.timegrid_units()[0].time_units]
    tiObj['endTime'] = ["".join(list(i.end.isoformat())[0:-3]) for i in se.timegrid_units()[0].time_units]
    return(tiObj)

outify = []
weekdayL = ""
outF = []
outFState = []

today = datetime.date.today()
monday = today - datetime.timedelta(days=today.weekday()) + datetime.timedelta(days=7)
friday = monday + datetime.timedelta(days=4) + datetime.timedelta(days=7)


### Settings
wantedDay = monday
rowRam = ""


class updateCallback(tornado.web.RequestHandler):
    def get(self):
        global kurse, finalData, outify, weekdayL, outF, outFState, selected
        self.write("<script> window.close(); </script>")
        kurse = kursDict[self.get_argument("kurs")]
        selected = self.get_argument("kurs")
        print(kurse)
        outify = []
        weekdayL = ""
        outF = []
        outFState = []
        finalData, strout = webU(wantedDay)
        

def webU(wantedDay = today):
    print("Updating table...", end = "")
    global outify, weekdayL, outF, outFState, rowRam
    with se.login() as s:
        timeGr = parseTimegrid(s)

        
        klasse = s.klassen().filter(name='EF')[0]

         
        table = s.timetable(klasse=klasse, start=wantedDay, end=wantedDay).to_table()
        weekdayL = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][wantedDay.weekday()]
        out = ""
        strout = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][wantedDay.weekday()]
        times = []
        i = 0
        while i < len(timeGr["startTime"]):
            outify.append(timeGr["startTime"][i] + " - " + timeGr["endTime"][i])
            i-=-1
        rowcount = 0
        for time, row in table:
            print(rowcount)
            if rowcount >= 5:
                print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIFFFFFFFFFFFFFFFFF")
                row = rowRam
            rowcount -=-1
            strout += '----[{}]----\n'.format(time.strftime('%H:%M'))
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
                            
                                strout += proc
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
                                    strout += (" "*(11-len(proc)) + "\n"+period.code + "\n")
                                else:
                                    out += proc + " "
                                    out += str(period.rooms[0])
                                    to += proc + " " + str(period.rooms[0])
                                    state = False
                                    strout += (" " * (11 - len(proc)) + str(period.rooms[0]) + "\n")
            elif rowcount >= 5:
                to += "-Mittagspause-"
            outF.append(to) 
            outFState.append(state)
            rowRam = row
    print("[DONE]")                           
    return(out, strout)
    

finalData = ""
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
    finalData, strout = webU(wantedDay)
    print("Starting server")
    tornado.ioloop.IOLoop.current().start()