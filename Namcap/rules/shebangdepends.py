# -*- coding: utf-8 -*-
# 
# namcap rules - shebangdepends
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
# Copyright (C) 2011 Rémy Oudompheng <remy@archlinux.org>
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

"""Checks dependencies on programs specified in shebangs."""

import re
import os
import tempfile
import subprocess
import pyalpm
import Namcap.package
from Namcap.util import script_type
from Namcap.ruleclass import *

def scanshebangs(fileobj, filename, scripts):
	"""
	Scan a file for shebang and stores the interpreter name.

	Stores
	  scripts -- a dictionary { program => set(scripts) }
	"""

	# test magic bytes
	magic = fileobj.read(2)
	if magic != b"#!":
		return
	# read the rest of file
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmp.write(magic + fileobj.read())
	tmp.close()

	try:
		cmd = script_type(tmp.name)
		if cmd != None:
			assert(isinstance(cmd, str))
			scripts.setdefault(cmd, set()).add(filename)
	finally:
		os.unlink(tmp.name)

def findowners(scriptlist):
	"""
	Find owners for executables.

	Returns:
	  pkglist -- a dictionary { package => set(programs) }
	  orphans -- a set of scripts not found
	"""

	pkglist = {}
	scriptfound = set()

	for s in scriptlist:
		p = subprocess.Popen(["which", s],
				stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		out, _ = p.communicate()
		if p.returncode != 0:
			continue

		# strip leading slash
		scriptpath = out.strip()[1:].decode('utf-8', 'surrogateescape')
		for pkg in Namcap.package.get_installed_packages():
			pkg_files = [fname for fname, fsize, fmode in pkg.files]
			if scriptpath in pkg_files:
				pkglist.setdefault(pkg.name, set()).add(s)
				scriptfound.add(s)

	orphans = list(set(scriptlist) - scriptfound)
	return pkglist, orphans

def getprovides(depends, provides):
	for i in depends.keys():
		pac = load(i)

		if pac != None and 'provides' in pac and pac["provides"] != None:
			provides[i] = pac["provides"]

class ShebangDependsRule(TarballRule):
	name = "shebangdepends"
	description = "Checks dependencies semi-smartly."
	def analyze(self, pkginfo, tar):
		scriptlist = {}

		for entry in tar:
			if not entry.isfile():
				continue
			f = tar.extractfile(entry)
			scanshebangs(f, entry.name, scriptlist)
			f.close()

		# find packages owning interpreters
		pkglist, orphans = findowners(scriptlist)
		for dep, progs in pkglist.items():
			if not isinstance(progs, set):
				continue
			needing = set().union(*[scriptlist[prog] for prog in progs])
			reasons = pkginfo.detected_deps.setdefault(dep, [])
			reasons.append((
				'programs-needed %s %s',
				(str(list(progs)), str(list(needing)))
				))

		# Do the script handling stuff
		for i, v in scriptlist.items():
			files = list(v)
			self.infos.append(("script-link-detected %s in %s", (i, str(files))))

		# Handle "no package associated" errors
		self.warnings.extend([("library-no-package-associated %s", i)
			for i in orphans])

		# Check for packages in testing
		for i in scriptlist:
			p = Namcap.package.load_from_db(i, 'testing')
			q = Namcap.package.load_from_db(i)
			if p != None and q != None and p["version"] == q["version"]:
				self.warnings.append(("dependency-is-testing-release %s", i))

# vim: set ts=4 sw=4 noet:
