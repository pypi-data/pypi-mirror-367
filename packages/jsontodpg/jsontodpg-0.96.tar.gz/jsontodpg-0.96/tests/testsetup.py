import sys, os

def setup_pathing():
    testdir = os.path.dirname(__file__)
    srcdir = '../src'
    sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))