import webuntis, os, tornado.web, tornado.ioloop, logging, datetime, time

kursDict = {"soeren": ["CH2","EK1","IF2","E52","GE2","KU1","ER1","C01","D2","M2","PH1","SP1"],
            "joshua": ["CH2", "PA2", "IF2", "E53", "L61", "MU1", "ER1", "C01", "D3", "M3", "GE3", "SP1"]}
kurse = kursDict["soeren"]


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

class updateCallback(tornado.web.RequestHandler):
    def get(self):
        global kurse, finalData, outify, outF, outFState, weekdayL
        self.write("<script> window.close(); </script>")
        kurse = kursDict[self.get_argument("kurs")]
        print(kurse)
        outify = []
        weekdayL = ""
        outF = []
        outFState = []
        finalData, strout = webU()
        

def webU():
    global outify, weekdayL, outF, outFState
    with se.login() as s:
        timeGr = parseTimegrid(s)

        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        friday = monday + datetime.timedelta(days=4)
        klasse = s.klassen().filter(name='EF')[0]

        wantedDay = today

        table = s.timetable(klasse=klasse, start=wantedDay, end=wantedDay).to_table()
        weekdayL = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][wantedDay.weekday()]
        out = ""
        strout = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][wantedDay.weekday()]
        times = []
        #print(timeGr)
        i = 0
        while i < len(timeGr["startTime"]):
            outify.append(timeGr["startTime"][i] + " - " + timeGr["endTime"][i])
            i-=-1
        #print(outify)
           
        for time, row in table:
            #out += '----[{}]----\n'.format(time.strftime('%H:%M'))
            strout += '----[{}]----\n'.format(time.strftime('%H:%M'))
            to = ""
            state = None
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
                                    to += proc +  " " + period.code
                                strout += (" "*(11-len(proc)) + "\n"+period.code + "\n")
                            else:
                                out += proc + " "
                                out += str(period.rooms[0])
                                to += proc + " " + str(period.rooms[0])
                                state = False
                                strout += (" "*(11-len(proc)) + str(period.rooms[0]) + "\n")
            outF.append(to) 
            outFState.append(state)                           
    return(out, strout)
    

finalData = ""
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        global finalData, outify, weekdayL, outF, outFState
        htmlDataPre = '''<html>
        <head>
        <style>
        html, body {
            font-family: Verdana, Geneva, sans-serif;
            background-color: white;
        }
        table {
            border: 1px solid black;
        }
        </style>
        </head>
        <body>'''
        htmlDataAfter = "</body></html>"
        self.render("index.html", data = outify, datum = weekdayL, roomData = outF, roomStates = outFState)
        #self.write(htmlDataPre + finalData + htmlDataAfter)

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
    finalData, strout = webU()
    #print(finalData)
    print("start")
    tornado.ioloop.IOLoop.current().start()