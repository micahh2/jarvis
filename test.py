from searchproviders.duckduckgo import DuckDuckGoSearchProvider as DDG
from searchproviders.sympyeval import SymPySearchProvider as SPSP

#ddg = DDG(lambda x: print(x["ans"]))
#started = ddg.query("What does the fox say?")

sp = SPSP(lambda x: print(x["ans"]))
started = sp.query("1+123")
