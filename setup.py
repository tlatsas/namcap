#!/usr/bin/env python
from setuptools import setup, find_packages

DATAFILES = [('/usr/share/man/man1', ['namcap.1']),
		('/usr/share/namcap', ['namcap-tags', 'parsepkgbuild.sh']),
		('/usr/share/doc/namcap',['README','AUTHORS','TODO'])]

setup(name="namcap",
	version="3.2.2",

	description="Pacman package analyzer",
	author="Arch Dev Team",
	author_email="pacman-dev@archlinux.org",
	url="http://www.archlinux.org/",

	py_modules=["namcap"],
	packages = find_packages(),
	scripts=["namcap", 'parsepkgbuild'],
	test_suite = "Namcap.tests",
	data_files=DATAFILES)

# vim: set ts=4 sw=4 noet:
