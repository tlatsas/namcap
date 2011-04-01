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
	dependlist = set(pkginfo.detected_deps.keys())
	indirectdependlist = getcovered(dependlist)
	for i in indirectdependlist:
		infos.append(("dependency-covered-by-link-dependence %s", i))
	needed_depend = dependlist | indirectdependlist
	# the minimal set of needed dependencies
	smartdepend = set(dependlist) - indirectdependlist

	# Find all the covered dependencies from the PKGBUILD
	pkginfo.setdefault("depends", [])
	explicitdepend = set(pkginfo["depends"])
	implicitdepend = getcovered(explicitdepend)
	pkgbuild_depend = explicitdepend | implicitdepend

	# Include the optdepends from the PKGBUILD
	pkginfo.setdefault("optdepends", [])
	optdepend = set(pkginfo["optdepends"])
	optdepend |= getcovered(optdepend)

	# Get the provides so we can reference them later
	# smartprovides : depend => (packages provided by depend)
	smartprovides = {}
	getprovides(explicitdepend, smartprovides)
	getprovides(implicitdepend, smartprovides)
	getprovides(optdepend, smartprovides)

	# The set of all provides for detected dependencies
	allprovides = set()
	for plist in smartprovides.values():
		allprovides |= set(plist)

	# Do the actual message outputting stuff
	for i in smartdepend:
		# if the needed package is itself:
		if i == pkginfo["name"]:
			continue
		# if the dependency is satisfied
		if i in pkgbuild_depend:
			continue
		# if the dependency is actually provided
		found = False
		for depend, provides in smartprovides.items():
			if i in provides and depend in pkgbuild_depend:
				found = True
				continue
		if found:
			continue
		# still not found, maybe it is specified as optional
		if i in optdepend:
			warnings.append(("dependency-detected-but-optional %s", i))
			continue
		# maybe, worse, it is provided by an optdepend
		for depend, provides in smartprovides.items():
			if i in provides and depend in optdepend:
				found = True
		if found:
			warnings.append(("dependency-detected-but-optional %s", i))
			continue
		# now i'm pretty sure i didn't find it.
		errors.append(("dependency-detected-not-included %s", i))

	for i in pkginfo["depends"]:
		# a needed dependency is superfluous it is implicitly satisfied
		if i in implicitdepend and (i in smartdepend or i in indirectdependlist):
			warnings.append(("dependency-already-satisfied %s", i))
		# a dependency is unneeded if:
		#   it is not in the depends as we see them
		#   it's not a provider for some needed dependency
		elif i not in needed_depend:
			needed_provides = set(smartprovides.get(i, [])) & needed_depend
			if len(needed_provides) == 0:
				warnings.append(("dependency-not-needed %s", i))
	infos.append(("depends-by-namcap-sight depends=(%s)", ' '.join(smartdepend) ))

	return errors, warnings, infos

# vim: set ts=4 sw=4 noet:
