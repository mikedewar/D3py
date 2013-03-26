from abc import ABCMeta
from exceptions import NotImplementedError

import logging

# in support of SimplyServer 
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

class SimplyServer(displayable):
    """
    Use Python's SimpleHTTPServer class to present this resulting d3 output
    to the user. 
    """
    def __init__(self, fig, host="localhost", port=8000, 
        interactive=False, logging=False):

        self.fig = fig
        self.host = host
        self.port = port
        self._server_thread = None
        self.httpd = None
        # interactive is True by default as this is designed to be a command line tool
        # we do not want to block interaction after plotting.
        self.interactive = interactive

    def ion(self):
        """
        Turns interactive mode on ala pylab
        """
        self.interactive = True
    
    def ioff(self):
        """
        Turns interactive mode off
        """
        self.interactive = False

    def show(self, interactive=None):
        self.fig.update()
        self.fig.save()
        self.fig.renderHtml(self.host, self.port)
        if interactive is not None:
            blocking = not interactive
        else:
            blocking = not self.interactive

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
        msgparams = (self.host, self.port, self.fig.name)
        url = "http://%s:%s/%s.html"%msgparams
        if self._server_thread is None or self._server_thread.active_count() == 0:
            Handler = CustomHTTPRequestHandler
            Handler.filemap = self.fig.filemap
            Handler.logging = self.fig.logging
            try:
                self.httpd = ThreadedHTTPServer(("", self.port), Handler)
            except Exception, e:
                print "Exception %s"%e
                return False
            if blocking:
                logging.info('serving forever on port: %s'%msgparams[1])
                msg = "You can find your chart at " + url
                print msg
                print "Ctrl-C to stop serving the chart and quit!"
                self._server_thread = None
                self.httpd.serve_forever()
            else:
                logging.info('serving asynchronously on port %s'%msgparams[1])
                self._server_thread = threading.Thread(
                    target=self.httpd.serve_forever
                )
                self._server_thread.daemon = True
                self._server_thread.start()
                msg = "You can find your chart at " + url
                print msg


    def __enter__(self):
        self.interactive = False
        return self

    def __exit__(self, ex_type, ex_value, ex_tb):
        if ex_tb is not None:
            print "Cleanup after exception: %s: %s"%(ex_type, ex_value)
        self._cleanup()

    def __del__(self):
        self._cleanup()

    def _cleanup(self):
        try:
            if self.httpd is not None:
                print "Shutting down httpd"
                self.httpd.shutdown()
                self.httpd.server_close()
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
