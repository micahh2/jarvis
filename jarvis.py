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
from searchproviders.duckduckgo import *
from searchproviders.sympyeval import *

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
        self.loadhistory()

        #self.goButton = Button()
        self.goButton = Button(frame,width=0)

        self.angleStatus = StringVar()
        self.angleStatus.set("degrees")
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
        self.entry.bind("<KeyRelease>", self.evaluate)
        self.entry.pack(side=TOP)

        self.appImage = PhotoImage()

        self.prompt = Label(frame, text="", font=('Helvetica', 0, ''))
        #self.prompt.bind("<Button-2>", self.copy)
        #self.prompt.bind("<Button-1>", self.copy)
        master.bind_all("<Control-KeyPress-C>", self.copy)
        self.prompt.pack(side=TOP)
        self.write_lock = threading.RLock()

        self.ddg = DuckDuckGoSearchProvider(self.output_provider_data)
        self.sp = SymPySearchProvider(self.output_provider_data)
        self.active_providers=0

    def output_provider_data(self, data):
        """Wrapper to handle closing active providers."""
        self.output_data(data)
        self.active_providers-=1

    def output_data(self, data):
        """The callback data then does something about it."""
        with self.write_lock:
            if data["success"]:
                self.prompt["text"] = data["ans"]
            elif self.active_providers == 1 and self.prompt["text"] == "Loading...":
                self.prompt["text"] = "No results found."

    def evaluate(self, event):
        q = self.entry.get()
        self.goButton.destroy()
        returnKey = False
        self.prompt["image"] = ""

        if event.keycode == 36:
            self.output_data({"success":True, "ans":"Loading..."})
            self.entry.delete(0, END)
            self.addhistory(q)
            returnKey = True

            if q == "":
                self.quitProgram()
                return

            print("# of threads: " + str(len(threading.enumerate())))

            #The two queries we'll do.
            self.ddg.query(q)
            self.sp.query(q)
            self.active_providers=2

    def gnuplot(self, query):
     #TODO sanitize input
        #setup variables
        success = True
        query = query.lower()
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
        self.angleStatus.set(angleUnit)
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
        print("The query (" + formq + ")  needs to be in terms of: " + str(terms))
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
            self.angleStatus.set("radians")
        if "deg" in query:
            angleUnit = "deg"
            self.angleStatus.set("degrees")
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
                    places = str(rounded).index(".")
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

    def calculus(self, query):
        success = True
        derive = ["derive", "derivative"]
        integrate = ["integrate", "integral"]
        calc = derive + integrate
        operators = "-+"
        operation = ""
        opList = list()
        returnString = "Error"

        for i in calc:
            if i in query:
                success=True
                break
            else:
                success=False

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
            rval = self.history[self.place+num-1]
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
                self.firstRun = False
            subprocess.check_output(query.replace("\n", ""), shell=True, universal_newlines=True)
        return

    def gotosite(self, event=None):
        """Open the webbrowser with the site?"""
        subprocess.Popen(["/etc/alternatives/x-www-browser", self.Site])
        self.entry.focus_force()
        return

    def loadhistory(self):
        with open("history.csv", newline="") as csvfile:
            hist = csv.reader(csvfile, delimiter=';', quotechar="\"")
            for i in hist:
                for j in i:
                    self.addhistory(j)
        return

    def writehistory(self):
        with open("history.csv", 'w', newline="") as csvfile:
            histwrite = csv.writer(csvfile, delimiter=';', quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            for i in reversed(self.history):
                if i != "":
                    histwrite.writerow([i])
        return

    def quitProgram(self):
        """Quit the program closing any threads"""
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
