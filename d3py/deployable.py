from abc import ABCMeta
from exceptions import NotImplementedError

import logging
import os

class deployable():
    """
    Given a d3py.figure, deployable stores it persistently. Concrete classes
    may simply save the files to the file system or be used to deploy them 
    in the cloud. 
    """
    
    __metaclass__ = ABCMeta

    def save(self, fig):
        raise NotImplementedError

class FileSystem(deployable):
    """
    Concrete class which simply saves the files to the file system
    """
    def __init__(self, fig, dest_dir, host="localhost", port=8000, logging=False):
        self.fig = fig
        self.host = host
        self.port = port
        self.dest_dir = dest_dir

    def save(self):
        """
        Save the figure to dest_dir
        """
        self.fig.update()
        self.fig.save()
        self.fig.renderHtml(self.host, self.port)

        if self.dest_dir is None:
            raise Exception("Destination directory not defined")
        if not os.path.exists(self.dest_dir):
            raise IOError("Destination directory, {d} , does not exist.".format(d=self.dest_dir))
        os.chdir(self.dest_dir)
        static_dir = self.dest_dir + os.sep + "static"
        if not os.path.exists(static_dir): 
            os.mkdir(static_dir)
        for k_filename in self.fig.filemap:
            f = self.dest_dir + os.sep + k_filename
            with open(f, 'w',0644) as fd_out:
                fd_in = self.fig.filemap[k_filename]["fd"]
                fd_in.seek(0)
                # import pdb; pdb.set_trace()
                for line in fd_in.readlines():
                    fd_out.write(line)
                fd_out.close()
