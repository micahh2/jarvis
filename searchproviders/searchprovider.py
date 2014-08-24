import threading
from threading import Thread

#This is an abstract class for a simple Search Provider
class SearchProvider:

    def __init__(self, cb):
        self.callback = cb;
        self.thread = Thread() #Empty thread to give us a starting object

    def query(self, q):
        """Returns true if the query is started and false if it isn't"""
        if self.thread.is_alive() and self.join_thread(.1):
            return False

        self.thread = Thread(target=self.routine, args=(q,))
        self.thread.start()

        return True

    def join_thread(self, t_out=None):
        """Joins the curent thread"""
        self.thread.join(timeout=t_out)
        return self.thread.is_alive()

    def routine(self):
        """This is where the main logic goes for the search provider"""
        pass
