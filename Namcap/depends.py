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
	global pkgcache
	if name not in pkgcache:
		pkgcache[name] = pacman.load(name)
	return pkgcache[name]

def getcovered(dependlist, covereddepend = None):
	"""
	Fills covereddepend with the full dependency tree
	of dependlist (iterable of package names)
	"""
	if covereddepend is None:
		covereddepend = set()

	for i in dependlist:
		pac = load(i)
		if pac != None and "depends" in pac:
			newdeps = [j for j in pac["depends"]
					if j != None and j not in covereddepend]
			covereddepend.update(newdeps)
			getcovered(newdeps, covereddepend)

	return covereddepend

def getprovides(depends, provides):
	for i in depends:
		pac = load(i)

		if pac != None and "provides" in pac and pac["provides"] != None:
			provides[i] = pac["provides"]

def analyze_depends(pkginfo):
	errors, warnings, infos = [], [], []

	# compute needed dependencies + recursive
	dependlist = pkginfo.detected_deps
	covereddepend = getcovered(dependlist)
	for i in covereddepend:
		infos.append(("dependency-covered-by-link-dependence %s", i))

	# Find all the covered dependencies from the PKGBUILD
	pkginfo.setdefault("depends", [])
	pkgdepend = set(pkginfo["depends"])
	# Include the optdepends from the PKGBUILD
	pkginfo.setdefault("optdepends", [])
	pkgdepend |= set(pkginfo["optdepends"])

	pkgcovered = getcovered(pkgdepend)

	# Our detected dependencies not covered by PKGBUILD
	smartdepend = set(dependlist) - covereddepend

	# Get the provides so we can reference them later
	smartprovides = {}
	getprovides(dependlist, smartprovides)

	# The set of all provides for detected dependencies
	allprovides = set()
	for plist in smartprovides.values():
		allprovides |= set(plist)

	# Do the actual message outputting stuff
	for i in smartdepend:
		# If (i is not in the PKGBUILD's dependencies
		# and i isn't the package name
		# and (if (there are provides for i) then
		#      (those provides aren't included in the package's dependencies))
		# )
		all_dependencies = pkginfo['depends'] + pkginfo['optdepends'] + list(pkgcovered)
		if (i not in all_dependencies and i != pkginfo["name"]
				and ((i not in smartprovides)
					or len([c for c in smartprovides[i] if c in pkgcovered]) == 0)):
			errors.append(("dependency-detected-not-included %s", i))

	for i in pkginfo["depends"]:
		if i in covereddepend and i in dependlist:
			warnings.append(("dependency-already-satisfied %s", i))
		# if i is not in the depends as we see them
		# and it's not in any of the provides from said depends
		elif i not in smartdepend and i not in allprovides:
			warnings.append(("dependency-not-needed %s", i))
	infos.append(("depends-by-namcap-sight depends=(%s)", ' '.join(smartdepend) ))

	return errors, warnings, infos

# vim: set ts=4 sw=4 noet:
