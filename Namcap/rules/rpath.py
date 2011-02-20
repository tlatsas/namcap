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
import tempfile
from Namcap.util import is_elf, clean_filename
from Namcap.ruleclass import *

allowed = ['/usr/lib', '/usr/lib32', '/lib', '$ORIGIN', '${ORIGIN}']
allowed_toplevels = [s + '/' for s in allowed]
warn = ['/usr/local/lib']
libpath = re.compile('Library rpath: \[(.*)\]')

def get_rpaths(filename):
	p = subprocess.Popen(["readelf", "-d", filename],
		env={'LANG': 'C'},
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	var = p.communicate()
	if p.returncode != 0:
		raise IOError("unable to read ELF file")

	for j in var[0].decode('ascii').splitlines():
		n = libpath.search(j)
		# Is this a Library rpath: line?
		if n is None:
			continue

		if ":" in n.group(1):
			rpaths = n.group(1).split(':')
		else:
			rpaths = [n.group(1)]
		for path in rpaths:
			yield path

class package(TarballRule):
	name = "rpath"
	description = "Verifies correct and secure RPATH for files."
	def analyze(self, pkginfo, tar):
		for entry in tar:
			if not entry.isfile():
				continue

			# is it an ELF file ?
			f = tar.extractfile(entry)
			elf = f.read()
			f.close()
			if elf[:4] != b"\x7fELF":
				continue # not an ELF file

			# write it to a temporary file
			f = tempfile.NamedTemporaryFile(delete = False)
			f.write(elf)
			f.close()

			for path in get_rpaths(f.name):
				path_ok = path in allowed
				for allowed_toplevel in allowed_toplevels:
					if path.startswith(allowed_toplevel):
						path_ok = True

				if not path_ok:
					self.errors.append(("insecure-rpath %s %s",
						(path, entry.name)))
					break
				if path in warn and entry.name not in insecure_rpaths:
					self.warnings.append(("insecure-rpath %s %s",
						(path, entry.name)))

			os.unlink(f.name)

# vim: set ts=4 sw=4 noet:
