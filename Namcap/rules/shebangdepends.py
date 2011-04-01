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

import re, os, pacman
import tempfile
import subprocess
from Namcap.util import is_elf, script_type
from Namcap.ruleclass import *

pkgcache = {}

def load(name, path=None):
	if name not in pkgcache:
		pkgcache[name] = pacman.load(name)
	return pkgcache[name]

def scanshebangs(fileobj, filename, scripts):
	"""
	Scan a file for shebang and stores the interpreter name.
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
			scripts.setdefault(cmd, {})[filename] = 1
	finally:
		os.unlink(tmp.name)

def findowners(scriptlist):
	pkglist = set()
	scriptfound = set()

	for s in scriptlist:
		p = subprocess.Popen(["which", s],
				stdout = subprocess.PIPE)
		out, _ = p.communicate()
		if p.returncode != 0:
			continue

		# strip leading slash
		scriptpath = out.strip()[1:]

		pacmandb = '/var/lib/pacman/local'
		for i in os.listdir(pacmandb):
			iname = i.split("-")[0]
			if os.path.isfile(pacmandb+'/'+i+'/files'):
				file = open(pacmandb+'/'+i+'/files', 'rb')
				for j in file:
					if scriptpath == j.strip():
						pkglist.add(iname)
						scriptfound.add(s)
				file.close()

	orphans = list(set(scriptlist) - scriptfound)
	return pkglist, orphans

def getprovides(depends, provides):
	for i in depends.keys():
		pac = load(i)

		if pac != None and 'provides' in pac and pac["provides"] != None:
			provides[i] = pac["provides"]

class ShebangDependsRule(TarballRule):
	name = "depends"
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
		for dep in pkglist:
			pkginfo.detected_deps.setdefault(dep, [])

		# Do the script handling stuff
		for i, v in scriptlist.items():
			files = list(v.keys())
			self.infos.append(("script-link-detected %s in %s", (i, str(files))))

		# Handle "no package associated" errors
		self.warnings.extend([("library-no-package-associated %s", i)
			for i in orphans])

		# Check for packages in testing
		if os.path.isdir('/var/lib/pacman/sync/testing'):
			for i in scriptlist:
				p = pacman.load(i, '/var/lib/pacman/sync/testing/')
				q = pacman.load(i)
				if p != None and q != None and p["version"] == q["version"]:
					self.warnings.append(("dependency-is-testing-release %s", i))

# vim: set ts=4 sw=4 noet:
