import os
import unittest

def getTestSuite():
	loader = unittest.TestLoader()
	return loader.discover(start_dir = os.path.dirname(__file__))

if __name__ == "__main__":
	runner = unittest.TextTestRunner()
	runner.run(getTestSuite())

# vim: set ts=4 sw=4 noet:
