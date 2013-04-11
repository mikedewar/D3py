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
    
    @staticmethod
    def default_deployable():
        return FileSystem(dest_dir=os.path.join(os.getcwd(), 'deploy'))

class FileSystem(deployable):
    """
    Concrete class which simply saves the files to the file system
    """
    def __init__(self, dest_dir=None, logging=False):
        self._fig = None
        self._dest_dir = dest_dir

    @property
    def fig(self):
        return self._fig

    @fig.setter
    def fig(self, fig):
        self._fig = fig
        
    @property
    def dest_dir(self):
        return self._dest_dir
        
    @dest_dir.setter
    def dest_dir(self, new_dir):
        self._dest_dir = new_dir

    def save(self, ephermeral_dir=None):
        """
        Save the figure to dest_dir.  If the user supplies a directory,
        via the ephermeral_dir argument, use it for this call. 
        """
        if ephermeral_dir is not None:
            self._dest_dir = ephermeral_dir
        if self._dest_dir is None:
            raise Exception("Destination directory not defined")
        static_dir = os.path.join(self._dest_dir, "static")
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        # NB: while this method makes sure we can write the static directory to the file system, figure controls the structure of the subdirectory. 
        os.chdir(self._dest_dir)
        for k_filename in self._fig.filemap:
            f = os.path.join(self._dest_dir, k_filename)
            with open(f, 'w',0644) as fd_out:
                fd_in = self._fig.filemap[k_filename]["fd"]
                fd_in.seek(0)
                # import pdb; pdb.set_trace()
                for line in fd_in.readlines():
                    fd_out.write(line)
