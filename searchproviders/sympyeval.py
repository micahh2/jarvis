from .searchprovider import SearchProvider
from sympy import *
import re

class SymPySearchProvider(SearchProvider):

    def sanitize_input(self, query):
        badwords = ["import", "lambda", "system", r"\<__\>"]
        while sum([re.match(i, query) != None for i in badwords]) > 0:
            for i in badwords:
                query = re.sub().replace(i, "", query)
        return query

    def routine(self, query):
        """Check if there is a simple mathimatical solution."""

        query = self.sanitize_input(query)
        try:
            expression = sympify(query)
            self.callback({"success": True, "ans": str(expression)})
        except (SympifyError) as e:
            self.callback({"success": False, "ans":"Poor formed expression"})
