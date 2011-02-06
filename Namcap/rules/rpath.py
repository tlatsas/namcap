#
# namcap rules - rpath
# Copyright (C) 2009 Abhishek Dasgupta <abhidg@gmail.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os, subprocess, re
from Namcap.util import is_elf, clean_filename
from Namcap.ruleclass import *

allowed = ['/usr/lib', '/usr/lib32', '/lib', '$ORIGIN', '${ORIGIN}']
allowed_toplevels = [s + '/' for s in allowed]
warn = ['/usr/local/lib']
libpath = re.compile('Library rpath: \[(.*)\]')

def checkrpath(filename, ret):
	"Checks if secure RPATH."

	if not is_elf(filename):
		return

	var = subprocess.Popen('readelf -d ' + filename,
			shell=True, env={'LANG': 'C'},
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE).communicate()

	for j in var[0].decode('ascii').splitlines():
		n = libpath.search(j)
		# Is this a Library rpath: line?
		if n != None:
			if ":" in n.group(1):
				rpaths = n.group(1).split(':')
			else:
				rpaths = [n.group(1)]
			for path in rpaths:
				path_ok = path in allowed
				for allowed_toplevel in allowed_toplevels:
					if path.startswith(allowed_toplevel):
						path_ok = True
				fname = clean_filename(filename)
				if not path_ok:
					ret[0].append(("insecure-rpath %s %s", (path, fname)))
					break
				if path in warn and fname not in insecure_rpaths:
					ret[1].append(("insecure-rpath %s %s", (path, fname)))

class package(TarballRule):
	name = "rpath"
	description = "Verifies correct and secure RPATH for files."
	def prereq(self):
		return "extract"
	def analyze(self, pkginfo, data):
		ret = [[], [], []]
		insecure_rpaths = [[], []]

		for dirpath, subdirs, files in os.walk(data):
			for i in files:
				checkrpath(os.path.join(dirpath, i), ret)

		return ret

# vim: set ts=4 sw=4 noet:
