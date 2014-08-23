#!/usr/bin/python3
import subprocess
import threading
from threading import Thread
import math
import time
import tkinter
import urllib.request
import json
import time
import re
import csv
import io
import csv
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from jmath import *

words = {"quit": ["quit", "stop", "die", "done", "end"],
        "contrary" : ["don't", "not", "un"]}

class App:
    applist = list()
    place = 0
    history = [""]
    firstRun = True
    outText = {"calculus" : [False, None], "gnuplot" : [False, None], "duckduckgo" : [False, None], "concalc" : [False, None]}

    que = [False, None, None]
    
    concalcTsk = Thread()
    calculusTsk = Thread()
    gnuplotTsk = Thread()
    duckduckgoTsk = Thread()

    def updateProgramList(self):
        applist = subprocess.Popen(["ls", "/usr/share/applications"]).split(" ")
        print(applist)

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.defaultfont=('Helvetica', 36, '')	
        self.descFont=('Helvetica', 12, '')	
        self.Frame = frame

        #self.icon = BitmapImage(file="logo.xbm")
        master.title("Jarvis")
        #master.iconmask(self.icon)

        #import history
        self.loadhistory();

        #self.goButton = Button()
        self.goButton = Button(frame,width=0)
        
        self.angleStatus = StringVar()
        self.angleStatus.set("degrees"); 
        self.optionTitle = Label(frame, text="Angle Units", font=('Helvetica', 0, ''))
        self.optionTitle.pack(side=TOP)
        self.radioDeg = Radiobutton(self.optionTitle, takefocus=0, text="Degrees", value="degrees", variable=self.angleStatus)
        self.radioDeg.pack(side=LEFT)
        self.radioRad = Radiobutton(self.optionTitle, takefocus=0, text="Radians", value="radians", variable=self.angleStatus)
        self.radioRad.pack(side=LEFT)

        self.entry = Entry(frame, exportselection=0, font=self.defaultfont)
        self.entry.focus_force()
        self.entry.bind('<Up>', self.up)
        self.entry.bind('<Down>', self.down)
        self.entry.bind("<Button-4>", self.up)
        self.entry.bind("<Button-5>", self.down)
        self.entry.bind("<KeyRelease>", self.addNext)
        self.entry.pack(side=TOP)

        self.appImage = PhotoImage()

        self.prompt = Label(frame, text="", font=('Helvetica', 0, ''))
        #self.prompt.bind("<Button-2>", self.copy)
        #self.prompt.bind("<Button-1>", self.copy)
        master.bind_all("<Control-KeyPress-C>", self.copy)
        self.prompt.pack(side=TOP)
        pollTsk = Thread(target=self.pollData, args=(threading.current_thread(),))
        pollTsk.start()

    def addNext(self, event):
        with threading.RLock() as lock:
            q = self.entry.get()
            self.que = [True, q, event]
            outText = {"calculus" : [False, None], "gnuplot" : [False, None], "duckduckgo" : [False, None], "concalc" : [False, None]}

    def pollData(self, parentThread):
        evalTsk = Thread()
        while parentThread.is_alive():
            change = False
            with threading.RLock() as lock:
                if self.que[0]:
                    self.prompt["image"] = "" 
                    self.prompt["text"] = ""
                    change = True
                    if not evalTsk.is_alive():
                            evalTsk = Thread(target=self.evaluate, args=(self.que[1],self.que[2],))
                            self.que = [False, None, None]
                            evalTsk.start()

            for i in ["concalc", "calculus", "duckduckgo", "gnuplot"]:
                j = self.outText[i]
                if j[0] and not self.que[0]:
                    if i == "gnuplot":
                        self.prompt["image"] = self.appImage
                    else:
                        self.prompt["text"] = j[1];
                        if i == "duckduckgo":
                            self.prompt["font"] = self.descFont
                        else:
                            self.prompt["font"] = self.defaultfont
                    change = True
                    break;
                elif self.prompt["text"] == "":
                    self.prompt["text"] = "Loading..."
            time.sleep(.1)
            self.prompt.pack()

    def evaluate(self, qry, event):
        q = qry
        self.goButton.destroy()
        returnKey = False
        self.prompt["image"] = ""

        if event.keycode == 36:
            self.prompt["text"] = ""
            self.entry.delete(0, END)
            self.addhistory(q)
            returnKey == True
            if q == "":
                self.quitProgram()
                return
            print("#")
            print("# of threads: " + str(len(threading.enumerate())))
            print("#")
            for i in threading.enumerate():
                if i != threading.current_thread():
                    i.join(timeout=4)



        if not self.concalcTsk.is_alive():
            #self.outText["concalc"] = [False, None]
            self.concalcTsk = Thread(target=self.concalc, args=(q,))
            self.concalcTsk.start()
            
        if not self.calculusTsk.is_alive():
            #self.outText["calculus"] = [False, None] 
            self.calculusTsk = Thread(target=self.calculus, args=(q,))
            self.calculusTsk.start()
            
        if not self.gnuplotTsk.is_alive():
            #self.outText["gnuplot"] = [False, None]
            self.gnuplotTsk = Thread(target=self.gnuplot, args=(q,))
            self.gnuplotTsk.start()

        if not self.duckduckgoTsk.is_alive():
            #self.outText["duckduckgo"] = [False, None]
            self.duckduckgoTsk = Thread(target=self.duckduckgo, args=(q,))
            self.duckduckgoTsk.start()

        change = False
        

    def gnuplot(self, query):
     #TODO sanitize input
        #setup variables
        success = True
        query = query.lower();
        plot = "plot"
        title = " title "
        quotes = "\'"
        polar = ""
        numbers = "0123456789y"
        termList = "xyztr"
        angleUnit = self.angleStatus.get()
        inFront = numbers + "c(x"
        behind = numbers + ")"
        likeTerms = {"x" : "t", "t" : "x", "y" : "r", "r" : "y", "z" : "x", "x" : "z"}
        terms = ["x"]

      #standard replacements
        for i in ["plot:", "graph:", "plot", "graph"]:
            query = query.replace(i, "")
        #override radian/degree setting
        if "rad" in query:
            angleUnit = "radians"
        if "deg" in query:
            angleUnit = "degrees"
        for i in ["degrees", "degree", "deg"]:
            query = query.replace(i, "")
        for i in ["radiant","radians", "radian", "rad"]:
            query = query.replace(i, "")
        self.angleStatus.set(angleUnit);
        formq = query.replace("^", "**")


        formq = formq.replace("f(x)", "y")
        formq = formq.replace("y=", "")
        formq = formq.replace("y =", "")
        #Changes to make it work with the title
        query = query.replace("(", "[")
        query = query.replace(")", "]")

        query = query.replace("sqrt", "SQRT")
        formq = formq.replace("sqrt", "SQRT")
      #Set the type of graph (2d, 3d, polar) and what variables to use
        if ("x" in query and "y" in query and "=" not in query) or "r3" in query or "z" in query:
            formq = formq.replace("r3","")
            query = query.replace("r3","")
            plot = "splot"
            terms = ["x", "y"]
        elif "polar" in query or "t" in query or "r" in query:
            polar = "set polar"
            formq = formq.replace("polar", "")
            query = query.replace("polar", "")
            terms = ["t"]

      #Fix title(s) if there is going to be more than one
        if "," in query:
            query = ""
            title = ""
            quotes = ""


      #Add multiplication symbols (*) where nessary
        tempList = list(formq)
        for i in range(len(tempList)):
            if i+1 < len(tempList):
                if tempList[i] in termList+"e)" and tempList[i+1] in inFront:
                    tempList[i+1:i+1] = "*"
                elif tempList[i] in behind and tempList[i+1] in termList + "ec(":
                    tempList[i+1:i+1] = "*"
        formq = "".join(tempList)

      #Replace math things
        formq = formq.replace("vector", "VCTR")
        formq = formq.replace("style", "STYL")
        formq = formq.replace("e", str(math.e))
        formq = formq.replace("ln", "log")
        formq = formq.replace("VCTR", "vector")
        formq = formq.replace("STYL", "style")

      #Try make the query in right terms
        print("The query (" + formq + ")  needs to be in terms of: " + str(terms));
        for i in termList:
            if i not in terms and i in formq:
                if likeTerms[i] in terms:
                    query = query.replace(i, likeTerms[i])
                    formq = formq.replace(i, likeTerms[i])
                elif len(terms) == 1:
                    query = query.replace(i, terms[0])
                    formq = formq.replace(i, terms[0])
        #Make final changes
        formq = formq.replace("SQRT", "sqrt")
        query = query.replace("SQRT", "sqrt")

        formq = "gnuplot -e \"set terminal gif rounded linewidth 2; set yzeroaxis; set xzeroaxis; set zzeroaxis; set output \'out.gif\'; set angles " + angleUnit + "; set autoscale; " + polar + "; " + plot + " " + formq + title + quotes + query + quotes+ "\""
        print(formq)
        #formq = " -e \"plot " + query + "; pause -1\""
        try:
            print(subprocess.check_output(formq, shell=True, universal_newlines=True))
            reply = PhotoImage(file="out.gif")
            self.appImage = reply
        except:
            success = False
        self.outText["gnuplot"] = [success, self.appImage]


    def concalc(self, query):
        angleUnit = self.angleStatus.get()[0:3]
        if "rad" in query:
            angleUnit = "rad"
            self.angleStatus.set("radians");
        if "deg" in query:
            angleUnit = "deg"
            self.angleStatus.set("degrees");
        for i in ["degress", "degree", "deg"]:
            query = query.replace(i, "")
        for i in ["radiant","radians", "radian", "rad"]:
            query = query.replace(i, "")

        try:
            success = True
            query=query.replace("integ", "INTGRL")
            query=query.replace("e", str(math.e))
            query=query.replace("INTGRL", "integ")

            #reply = subprocess.check_output("concalc -a " + angleUnit + "\'" + query + "\'", shell=True, universal_newlines=True)
            reply = subprocess.check_output("concalc -a " + angleUnit + " '" + query + "'", shell=True, universal_newlines=True)
            if reply in ["nan\n", "Nan\n", "nannani\n", "none\n"]:
                success = False
            else:
                try:
                    rounded = float(reply.replace("\n", ""))
                    places = str(rounded).index(".");
                    decimals = len(str(rounded))-str(rounded).index(".")
                    if decimals > 14:
                        rounded = round(rounded, len(str(rounded).replace(".",""))-3)
                        reply = str(rounded)
                        decimals = len(str(rounded))-str(rounded).index(".")
                    if decimals > 4 and "e" not in reply:
                        reply = str(float(rounded)*float(10**(decimals-1))) + "e-" + str(decimals-1)
                    if places > 4 and "e" not in reply:
                        reply = str(float(rounded)/float(10**(places-1))) + "e" + str(places-1)

                except:
                    print("Error")
                    print(list(reply.replace("\n", "")))
        except:
            success= False
            reply = "Error in using concalc"
        self.outText["concalc"] = [success, reply]
        return

    def duckduckgo(self, query):
        success = True
        query = query.replace("def:", "")
        try:
            page = urllib.request.urlopen("http://176.34.135.166/?q=%22" + query.replace(" ", "%20") + "%22&format=json&no_redirect=1", timeout=1.5)
            jdata = json.loads(page.read().decode('utf-8'))
        except:
            reply = "Failed to connect"
            success = False
        else:
            for i in ["Answer", "AbstractText", "Definition", "Abstract", "Heading"]:
                reply = str(jdata[i])
                print(reply)
                if len(reply) > 0:
                    break
            reply = re.sub("(.{64})", "\\1\n", reply, re.DOTALL)	

        try:
            queryURL = "http://176.34.135.166/?q=!+" + query.replace(" ", "+") + "&format=json&no_redirect=1"
            print(queryURL)
            urlpage = urllib.request.urlopen(queryURL, timeout=1)
            urldata = json.loads(urlpage.read().decode('utf-8'))
            self.Site = urldata["Redirect"]
        except:
            print("Page didn't load")
        else:
            self.goButton = Button(self.Frame, text="Go to site", command=self.gotosite)
            self.goButton.pack(side=BOTTOM)
            self.goButton.bind("<Return>", self.gotosite)
            #self.goButton.focus_force()
        if reply == "":
            success = False
        self.outText["duckduckgo"] = [success, reply]

    def calculus(self, query):
        success = True;
        derive = ["derive", "derivative"]
        integrate = ["integrate", "integral"]
        calc = derive + integrate
        operators = "-+"
        operation = ""
        opList = list()
        returnString = "Error"

        for i in calc:
            if i in query:
                success=True;
                break;
            else:
                success=False;

        if success==True:
            for i in calc:
                if i in query:
                    operation = i
                    query = query.replace(i, "")
            query = query.replace(" " , "")
            query = query.replace("of" , "")
            listQuery = list(query)
            for i in listQuery:
                if i in operators:
                    opList.append(i)
                    listQuery[listQuery.index(i)] = "&"
            indivQuerys = "".join(listQuery).split("&")
            for i in range(len(indivQuerys)):
                if operation in integrate:
                    reply = integral(indivQuerys[i])
                if operation in derive:
                    reply = derivative(indivQuerys[i])
                if reply[0]:
                    indivQuerys[i] = reply[1]
                else:
                    success = False
                    break
                
            returnString = ""
            for i in indivQuerys:
                returnString += i
                if len(opList) > 0:
                    returnString += " " + opList.pop() + " "
        self.outText["calculus"] = [success, returnString]


    def gethistory(self, num=1):
        if len(self.history) > self.place+num and self.place+num >= 0:
            rval = self.history[self.place+num-1];
            self.place+=num
            self.entry.delete(0, END)
            self.entry.insert(0, rval)
        return

    def addhistory(self, query=""):
        self.history[:0] = [query]
        self.place=0
        return

    def up (self, event):
        if self.place == 0 and self.entry.get() != "":
            self.addhistory(self.entry.get())
        self.gethistory(num=1)
        return

    def down (self, event):
        self.gethistory(num=-1)
        return

    def copy(self, event):
        for i in range(10):
            print(copy)
        if self.prompt["image"] == "":
            query = "echo -n \"" + self.prompt["text"] + "\" | xsel -ib"
            if self.firstRun:
                subprocess.check_output("xsel -k", shell=True, universal_newlines=True)
                self.firstRun = False;
            subprocess.check_output(query.replace("\n", ""), shell=True, universal_newlines=True)
        return
    def gotosite(self, event=None):
        subprocess.Popen(["/etc/alternatives/x-www-browser", self.Site])
        self.entry.focus_force()
        return
    def loadhistory(self):
        with open("history.csv", newline="") as csvfile:
            hist = csv.reader(csvfile, delimiter=';', quotechar="\"");
            for i in hist:
                for j in i:
                    self.addhistory(j);
        return
    def writehistory(self):
        with open("history.csv", 'w', newline="") as csvfile:
            histwrite = csv.writer(csvfile, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            for i in reversed(self.history):
                if i != "":
                    histwrite.writerow([i])
        return
    
    def quitProgram(self):
        self.writehistory()
        with threading.RLock() as lock:
            for i in threading.enumerate():
                if i != threading.current_thread():
                    i.join(timeout=.5)
        self.prompt.quit()

root = Tk()
app = App(root)
root.iconbitmap("@logo.xbm")
root.mainloop()
