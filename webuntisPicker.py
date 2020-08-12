import webuntis, os, tornado.web, tornado.ioloop, logging, datetime, time

kurse = ["CH2","EK1","IF2","E52","GE2","KU1","ER1","C01","D2","M2","PH1","SP1"]

se = webuntis.Session(
    username='JgstEF',
    password='Doruwiwilu1',
    server='tritone.webuntis.com',
    school='gym_remscheid',
    useragent='Soeren spielt mit der API'
)

logging.basicConfig(level=logging.WARN)

def parseTimegrid(dayGrid):
    dayGrid = str(dayGrid)
    proce = dayGrid.split("[")[1]
    proce = proce.replace("]", "")
    proce = proce.split("}, {")
    
    fout = []
    for elm in proce:
        tiObj = {}
        tempy = elm.strip("{").strip("}").split(",")
        tiObj['startTime'] = ["".join(list(i.start.isoformat())[0:-3]) for i in s.timegrid_units()[0].time_units]
        tiObj['endTime'] = ["".join(list(i.end.isoformat())[0:-3]) for i in s.timegrid_units()[0].time_units]
        fout.append(tiObj)


    return(fout)

outify = []
weekdayL = ""
outF = []
outFState = []
def webU():
    global outify, weekdayL, outF, outFState
    with se.login() as s:
        timegrid2 = s.timegrid_units()[0]  
        timeGr = parseTimegrid(timegrid2)

        today = datetime.date.today()
        monday = today - datetime.timedelta(days=today.weekday())
        friday = monday + datetime.timedelta(days=4)
        klasse = s.klassen().filter(name='EF')[0]
        table = s.timetable(klasse=klasse, start=friday, end=friday).to_table()
        weekdayL = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][today.weekday()]
        out = ""
        strout = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"][today.weekday()]
        times = []

        for elm in timeGr:
            outify.append(str(elm["startTime"]) + " - " + str(elm["endTime"]))
           
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
        global finalData
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
    return tornado.web.Application([(r"/", MainHandler)], static_path=os.path.join(os.path.dirname(__file__), "static"),template_path=os.path.join(os.path.dirname(__file__), "templates"))

if __name__ == "__main__":
    io_loop = tornado.ioloop.IOLoop.current()
    app = make_app()
    app.listen(8888)
    finalData, strout = webU()
    #print(finalData)
    print("start")
    tornado.ioloop.IOLoop.current().start()