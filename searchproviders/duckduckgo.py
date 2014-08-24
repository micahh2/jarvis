import urllib.request
import json
import re
from .searchprovider import SearchProvider

class DuckDuckGoSearchProvider(SearchProvider):

    def routine(self, query):
        """Overiding the parents routine to search the using the duckduckgo search engine."""

        success = True
        #Replace words
        query = query.replace("def:", "")
        query = query.replace(" ", "%20")

        try:
            page = urllib.request.urlopen("http://176.34.135.166/?q=%22" + query + "%22&format=json&no_redirect=1", timeout=1.5)
            jdata = json.loads(page.read().decode('utf-8'))

            for i in ["Answer", "AbstractText", "Definition", "Abstract", "Heading"]:
                reply = str(jdata[i])
                if len(reply) > 0:
                    break
            reply = re.sub("(.{64})", "\\1\n", reply, re.DOTALL)

        except Exception as e:
            reply = "Failed to connect: " + str(e)
            success = False

        if reply == "":
            success = False

        self.callback({"success": success, "ans":reply})
