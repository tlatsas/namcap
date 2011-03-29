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

import re, os, os.path
import subprocess
import tempfile
from Namcap.util import is_elf, script_type
from Namcap.ruleclass import *
import Namcap.tags
from Namcap import package

def getcovered(dependlist, covereddepend = None):
	"""
	Fills covereddepend with the full dependency tree
	of dependlist (iterable of package names)
	"""
	if covereddepend is None:
		covereddepend = set()

	for i in dependlist:
		pac = package.load_from_db(i)
		if pac != None and "depends" in pac:
			newdeps = [j for j in pac["depends"]
					if j != None and j not in covereddepend]
			covereddepend.update(newdeps)
			getcovered(newdeps, covereddepend)

	return covereddepend

def getprovides(depends, provides):
	for i in depends:
		pac = package.load_from_db(i)

		if pac != None and "provides" in pac and pac["provides"] != None and len(pac["provides"]) > 0:
			provides[i] = pac["provides"]
		else:
			provides[i] = []

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
	getprovides(smartdepend, smartprovides)

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
		# if the dependency is pulled as a provider for some explicit dep
		if len(set(smartprovides[i]) & pkgbuild_depend) > 0:
			continue
		# compute dependency reason
		reasons = pkginfo.detected_deps[i]
		reason_strings = [Namcap.tags.format_message(reason) for reason in reasons]
		reason = ', '.join(reason_strings)
		# still not found, maybe it is specified as optional
		if i in optdepend:
			warnings.append(("dependency-detected-but-optional %s (%s)", (i, reason)))
			continue
		# maybe, it is pulled as a provider for an optdepend
		if len(set(smartprovides[i]) & optdepend) > 0:
			warnings.append(("dependency-detected-but-optional %s (%s)", (i, reason)))
			continue
		# now i'm pretty sure i didn't find it.
		errors.append(("dependency-detected-not-included %s (%s)", (i, reason)))

	for i in pkginfo["depends"]:
		# a needed dependency is superfluous it is implicitly satisfied
		if i in implicitdepend and (i in smartdepend or i in indirectdependlist):
			warnings.append(("dependency-already-satisfied %s", i))
		# a dependency is unneeded if:
		#   it is not in the depends as we see them
		#   it does not pull some needed dependency which provides it
		elif i not in needed_depend and i not in allprovides:
			warnings.append(("dependency-not-needed %s", i))
	infos.append(("depends-by-namcap-sight depends=(%s)", ' '.join(smartdepend) ))

	return errors, warnings, infos

# vim: set ts=4 sw=4 noet:
