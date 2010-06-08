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

allowed = ['/usr/lib', '/lib', '$ORIGIN', '${ORIGIN}']
allowed_toplevels = map(lambda s: s + '/', allowed)
warn = ['/usr/local/lib']
libpath = re.compile('Library rpath: \[(.*)\]')

def checkrpath(insecure_rpaths, dirname, names):
	"Checks if secure RPATH."

	for i in names:
		mypath = dirname + '/' + i
		if is_elf(mypath):
			var = subprocess.Popen('readelf -d ' + mypath,
					shell=True,
					stdout=subprocess.PIPE,
					stderr=subprocess.PIPE).communicate()
			for j in var[0].split('\n'):
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
						fname = clean_filename(mypath)
						if not path_ok:
							insecure_rpaths[0].append((path, fname))
							break
						if path in warn and fname not in insecure_rpaths:
							insecure_rpaths[1].append((path, fname))

class package:
	def short_name(self):
		return "rpath"
	def long_name(self):
		return "Verifies correct and secure RPATH for files."
	def prereq(self):
		return "extract"
	def analyze(self, pkginfo, data):
		ret = [[], [], []]
		insecure_rpaths = [[], []]
		os.path.walk(data, checkrpath, insecure_rpaths)

		if len(insecure_rpaths) > 0:
			for j in (0, 1):
				for f in insecure_rpaths[j]:
					# f is already a tuple of (badrpath, badbinary)
					ret[j].append(("insecure-rpath %s %s", f))
		return ret
	def type(self):
		return "tarball"
# vim: set ts=4 sw=4 noet:
