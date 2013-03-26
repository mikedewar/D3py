import datetime
import os
import sys
import tempfile

from d3py.displayable import SimplyServer
from d3py.deployable import FileSystem

def display(fig):
    with SimplyServer(fig) as server:
       server.show()

def deploy(fig):
    test_dir = tempfile.gettempdir() 
    if test_dir is not None:
        test_dir += (os.sep 
            + "d3py_test" + os.sep 
            + os.path.splitext(os.path.basename(sys.argv[0]))[0]
            + "_"
            + datetime.date.today().strftime("%j")) # %j is day of year
        print("creating test dir, {0}.".format(test_dir))
        os.makedirs(test_dir)
        fs = FileSystem(fig, test_dir) 
        fs.save()

