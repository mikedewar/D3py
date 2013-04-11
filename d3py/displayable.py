from abc import ABCMeta
from exceptions import NotImplementedError

import logging

# in support of SimpleServer 
import threading
import webbrowser
from HTTPHandler import CustomHTTPRequestHandler, ThreadedHTTPServer

# requires IPython 0.11.0 or higher
import IPython.core.display

class displayable():
    """
    Given a d3py.figure, displayables present the graph to the user. 
    The first displayable is based on python's SimpleHTTPServer class.
    
    These classes should know nothing of html, css or javascript which
    live in the figure class. 
    """
    __metaclass__ = ABCMeta
    
    def show(self, fig):
        raise NotImplementedError
        
    @staticmethod
    def default_displayable(fig):
        return SimpleServer(fig)

class SimpleServer(displayable):
    """
    Use Python's SimpleHTTPServer class to present this resulting d3 output
    to the user. 
    """
    def __init__(self, fig, host="localhost", port=8000, 
        interactive=False, logging=False):

        self._fig = fig
        self._host = host
        self._port = port
        self._server_thread = None
        self._httpd = None
        # interactive is True by default as this is designed to be a command line tool
        # we do not want to block interaction after plotting.
        self._interactive = interactive

    @property
    def host(self):
        return self._host 
    
    @property
    def port(self):
        return self._port

    def ion(self):
        """
        Turns interactive mode on ala pylab
        """
        self._interactive = True
    
    def ioff(self):
        """
        Turns interactive mode off
        """
        self._interactive = False

    def show(self, interactive=None):
        if interactive is not None:
            blocking = not interactive
        else:
            blocking = not self._interactive

        if blocking:
            self._serve(blocking=True)
        else:
            # if not blocking, we serve the 
            self._serve(blocking=False)
            # fire up a browser
            webbrowser.open_new_tab("http://%s:%s/%s.html"%(self.host,self.port, self.name))

    def _serve(self, blocking=True):
        """
        start up a server to serve the files for this vis.
        """
        msgparams = (self.host, self.port, self._fig.name)
        url = "http://%s:%s/%s.html"%msgparams
        if self._server_thread is None or self._server_thread.active_count() == 0:
            Handler = CustomHTTPRequestHandler
            Handler.filemap = self._fig.filemap
            Handler.logging = self._fig.logging
            try:
                self._httpd = ThreadedHTTPServer(("", self.port), Handler)
            except Exception, e:
                print "Exception %s"%e
                return False
            if blocking:
                logging.info('serving forever on port: %s'%msgparams[1])
                msg = "You can find your chart at " + url
                print msg
                print "Ctrl-C to stop serving the chart and quit!"
                self._server_thread = None
                self._httpd.serve_forever()
            else:
                logging.info('serving asynchronously on port %s'%msgparams[1])
                self._server_thread = threading.Thread(
                    target=self._httpd.serve_forever
                )
                self._server_thread.daemon = True
                self._server_thread.start()
                msg = "You can find your chart at " + url
                print msg


    def __enter__(self):
        self._interactive = False
        return self

    def __exit__(self, ex_type, ex_value, ex_tb):
        if ex_tb is not None:
            if ex_value is None:
                print "Cleanup after exception: %s"%(ex_type)
            else:
                print "Cleanup after exception: %s: %s"%(ex_type, ex_value)
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        try:
            if self._httpd is not None:
                print "Shutting down httpd"
                self._httpd.shutdown()
                self._httpd.server_close()
        except Exception, e:
            print "Error in clean-up: %s"%e

class IPython(displayable):
    """
    IPython integration 
    """
    def __init__(self):
        pass
        
    def show(self, fig):
        html = "<iframe src=http://%s:%s/%s.html width=%s height=%s>" % (
            self.host, self.port, self.name, fig.width, fig.height)
        IPython.core.display.HTML(html)
