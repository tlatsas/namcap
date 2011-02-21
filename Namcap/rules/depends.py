# -*- coding: utf-8 -*-
# 
# namcap rules - depends
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

"""Checks dependencies semi-smartly."""

import re, os, os.path, pacman
import subprocess
import tempfile
from Namcap.util import is_elf, script_type
from Namcap.ruleclass import *

pkgcache = {}

def load(name, path=None):
	if name not in pkgcache:
		pkgcache[name] = pacman.load(name)
	return pkgcache[name]

def getcovered(current, dependlist, covereddepend):
	if current == None:
		for i in dependlist:
			pac = load(i)
			if pac != None and hasattr(pac, 'depends'):
				for j in pac.depends:
					if j != None and not j in covereddepend:
						covereddepend[j] = 1
						getcovered(j, dependlist, covereddepend)
	else:
		pac = load(current)
		if pac != None and hasattr(pac, 'depends'):
			for i in pac.depends:
				if i != None and not i in covereddepend:
					covereddepend[i] = 1
					getcovered(i, dependlist, covereddepend)

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

def getprovides(depends, provides):
	for i in depends.keys():
		pac = load(i)

		if pac != None and hasattr(pac, 'provides') and pac.provides != None:
			provides[i] = pac.provides

class package(TarballRule):
	name = "depends"
	description = "Checks dependencies semi-smartly."
	def analyze(self, pkginfo, tar):
		scriptlist = {}
		dependlist = {}
		smartdepend = {}
		smartprovides = {}
		covereddepend = {}
		pkgcovered = {}

		for entry in tar:
			if not entry.isfile():
				continue
			f = tar.extractfile(entry)
			scanshebangs(f, entry.name, scriptlist)
			f.close()

		# TODO: find packages owning interpreters

		# Do the script handling stuff
		for i, v in scriptlist.items():
			if i not in dependlist:
				dependlist[i] = {}
			for j in v.keys():
				dependlist[i][j] = 1
			files = list(v.keys())
			self.infos.append(("script-link-detected %s in %s", (i, str(files))))

		# Check for packages in testing
		if os.path.isdir('/var/lib/pacman/sync/testing'):
			for i in dependlist.keys():
				p = pacman.load(i, '/var/lib/pacman/sync/testing/')
				q = load(i)
				if p != None and q != None and p.version == q.version:
					self.warnings.append(("dependency-is-testing-release %s", i))

		# Find all the covered dependencies from the PKGBUILD
		pkgdepend = {}
		if hasattr(pkginfo, 'depends'):
			for i in pkginfo.depends:
				pkgdepend[i] = 1

		# Include the optdepends from the PKGBUILD
		if hasattr(pkginfo, 'optdepends'):
			for i in pkginfo.optdepends:
				pkgdepend[i] = 1

		getcovered(None, pkgdepend, pkgcovered)

		# Do tree walking to find all the non-leaves (branches?)
		getcovered(None, dependlist, covereddepend)
		for i in covereddepend.keys():
			self.infos.append(("dependency-covered-by-link-dependence %s", i))

		# Set difference them to find the leaves
		for i in dependlist.keys():
			if not i in covereddepend:
				smartdepend[i] = 1

		# Get the provides so we can reference them later
		getprovides(dependlist, smartprovides)

		# Do the actual message outputting stuff
		for i in smartdepend.keys():
			# If (i is not in the PKGBUILD's dependencies
			# and i isn't the package name
			# and (if (there are provides for i) then
			#      (those provides aren't included in the package's dependencies))
			# )
			all_dependencies = getattr(pkginfo, 'depends', []) + getattr(pkginfo, 'optdepends', []) + list(pkgcovered.keys())
			if (i not in all_dependencies and i != pkginfo.name
					and ((i not in smartprovides)
						or len([c for c in smartprovides[i] if c in pkgcovered]) == 0)):
					if type(dependlist[i]) == dict:
						self.errors.append(("dependency-detected-not-included %s from files %s",
							(i, str(list(dependlist[i]))) ))
					else:
						self.errors.append(("dependency-detected-not-included %s", i))
		if hasattr(pkginfo, 'depends'):
			for i in pkginfo.depends:
				if i in covereddepend and i in dependlist:
					self.warnings.append(("dependency-already-satisfied %s", i))
				# if i is not in the depends as we see them and it's not in any of the provides from said depends
				elif i not in smartdepend and i not in [y for x in smartprovides.values() for y in x]:
					self.warnings.append(("dependency-not-needed %s", i))
		self.infos.append(("depends-by-namcap-sight depends=(%s)", ' '.join(smartdepend.keys()) ))

# vim: set ts=4 sw=4 noet:
