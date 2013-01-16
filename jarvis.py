#!/usr/bin/python3.2
import subprocess
import math
import tkinter
import urllib.request
import json
import time
import re
import csv
import io
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

words = {"quit": ["quit", "stop", "die", "done", "end"],
        "contrary" : ["don't", "not", "un"]}


class App:
    applist = list()
    place = 0
    history = [""]
    firstRun = True;

    def updateProgramList(self):
        applist = subprocess.Popen(["ls", "/usr/share/applications"]).split(" ")
        print(applist)

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        print(str(type(frame)))

        self.defaultfont=('Helvetica', 36, '')	
        self.descFont=('Helvetica', 12, '')	
        self.Frame = frame

        #self.icon = BitmapImage(file="logo.xbm")
        master.title("Jarvis")
        #master.iconmask(self.icon)

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
        self.entry.bind("<Return>", self.evaluate)
        self.entry.pack(side=TOP)

        self.appImage = PhotoImage()

        self.prompt = Label(frame, text="", font=('Helvetica', 0, ''))
        self.prompt.bind("<Button-2>", self.copy)
        self.prompt.bind("<Button-1>", self.copy)
        self.prompt.pack(side=TOP)

    def evaluate(self, event):
        self.prompt["text"] = ""
        self.prompt["image"] = ""
        self.prompt["font"] = self.defaultfont
        q = self.entry.get()
        self.entry.delete(0, END)
        self.goButton.destroy()

        self.addhistory(q)

        if q == "":
            self.prompt.quit()
            return

        reply = self.concalc(q)
        if reply[0]:
            outText = reply[1]
        else:
            reply = self.calculus(q)
            if reply[0]:
                outText = reply[1]
            else:
                reply = self.gnuplot(q)
                if reply[0]:
                    self.prompt["image"] = self.appImage
                    outText = "Done"
                else:
                    reply = self.duckduckgo(q)
                    self.prompt["font"] = self.descFont
                    if reply[0]:
                        outText = reply[1]
                    else:
                        outText = "I'm sorry, I don't know how to answer that."

        self.prompt["text"] = outText

        self.prompt.pack()

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
            print(formq)
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
        return [success, self.appImage]

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
                    reply = self.integral(indivQuerys[i])
                if operation in derive:
                    reply = self.derivative(indivQuerys[i])
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
        return [success, returnString]
            
    def integral(self, query):
        success = True
        integrals = {"1":"x", "1/x" : "ln(x)", "e^x":"e^x", "sin(x)":"-cos(x)", "cos(x)":"sin(x)",
                     "sec^2(x)" : "tan(x)", "tan(x)" : "ln(sec^2(x))",
                     "cot(x)": "ln(sin(x))", "sec(x)": "ln(sec(x)+tan(x))"}
        returnString = "Err/integrate"
        if query in integrals:
            returnString = integrals[query]
        else:
            success = False
        return [success, returnString]
    def derivative(self, query):
        success = True
        derivatives = {"x":"1", "ln(x)" : "1/x", "e^x":"e^x", "sin(x)":"cos(x)", "cos(x)":"-sin(x)",
                       "tan(x)" : "sec^2(x)", "cot(x)":"-csc^2(x)", 
                       "sec(x)":"sec(x)tan(x)", "csc(x)" : "-csc(x)cot(x)"}
        returnString = "Err/derive"
        print(query)
        if query in derivatives:
            returnString = derivatives[query]
        else:
            success = False
        return [success, returnString]

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

            print(angleUnit)
            #reply = subprocess.check_output("concalc -a " + angleUnit + "\'" + query + "\'", shell=True, universal_newlines=True)
            reply = subprocess.check_output("concalc -a " + angleUnit + " '" + query + "'", shell=True, universal_newlines=True)
            if reply in ["nan\n", "Nan\n", "nannani\n", "none\n"]:
                success = False
            else:
                try:
                    rounded = float(reply.replace("\n", ""))
                    decimals = len(str(rounded))-str(rounded).index(".")
                    if decimals > 14:
                        rounded = round(rounded, len(str(rounded).replace(".",""))-3)
                        reply = str(rounded)
                except:
                    print("Error")
                    print(list(reply.replace("\n", "")))
        except:
            success= False
            reply = "Error in using concalc"
        return [success, reply]

    def duckduckgo(self, query):
        success = True
        query = query.replace("def:", "")
        print(query)
        try:
            page = urllib.request.urlopen("http://176.34.135.166/?q=%22" + query.replace(" ", "%20") + "%22&format=json&no_redirect=1", timeout=1)
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
            print("Fudge nuggets!")
        else:
            self.goButton = Button(self.Frame, text="Go to site", command=self.gotosite)
            self.goButton.pack(side=BOTTOM)
            self.goButton.bind("<Return>", self.gotosite)
            self.goButton.focus_force()
        if reply == "":
            success = False
        return [success, reply]


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
        self.gethistory(num=1)
        return
    def down (self, event):
        self.gethistory(num=-1)
        return
    def copy(self, event):
        if self.prompt["image"] == "" and self.prompt["text"] != "I'm sorry, I don't know how to answer that.":
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
        0/0
        self.tree.parse("history.xml")
        return
    def writehistory(self):
        self.tree.write("history.xml")
        0/0
        return

root = Tk()
app = App(root)
root.iconbitmap("@logo.xbm")
root.mainloop()
