def calculus(query):
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
    return [success, returnString]
        
def integral(query):
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
def derivative(query):
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
