import os

def datadir():
    """ Return the data/ directory."""
    fil = os.path.abspath(__file__)
    codedir = os.path.dirname(fil)
    datadir = os.path.join(codedir,'data')+'/'
    return datadir
