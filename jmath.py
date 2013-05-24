        
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
