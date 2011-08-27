# -*- coding: utf-8 -*-
#
# namcap rules - sodepends
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

"""Checks dependencies resulting from linking of shared libraries."""

from collections import defaultdict
import re
import os
import subprocess
import tempfile
import Namcap.package
from Namcap.ruleclass import *

libcache = {'i686': {}, 'x86-64': {}}

def figurebitsize(line):
	"""
	Given a line of output from readelf (usually Shared library:) return
	'i686' or 'x86-64' if the binary is a 32bit or 64bit binary
	"""

	address = line.split()[0]
	if len(address) == 18: # + '0x' + 16 digits
		return 'x86-64'
	else:
		return 'i686'

def scanlibs(fileobj, filename, sharedlibs):
	"""
	Run "readelf -d" on a file-like object (e.g. a TarFile)

	If it depends on a library, store that library's path.

	sharedlibs: a dictionary { library => set(ELF files using that library) }
	"""
	shared = re.compile('Shared library: \[(.*)\]')

	# test magic bytes
	magic = fileobj.read(4)
	if magic[:4] != b"\x7fELF":
		return

	# read the rest of file
	tmp = tempfile.NamedTemporaryFile(delete=False)
	tmp.write(magic + fileobj.read())
	tmp.close()

	try:
		p = subprocess.Popen(["readelf", "-d", tmp.name],
				env = {"LANG": "C"},
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE)
		var = p.communicate()
		assert(p.returncode == 0)
		for j in var[0].decode('ascii').splitlines():
			n = shared.search(j)
			# Is this a Shared library: line?
			if n != None:
				# Find out its architecture
				architecture = figurebitsize(j)
				try:
					libpath = os.path.abspath(
							libcache[architecture][n.group(1)])[1:]
					sharedlibs.setdefault(libpath, set()).add(filename)
				except KeyError:
					# We didn't know about the library, so add it for fail later
					sharedlibs.setdefault(n.group(1), set()).add(filename)
	finally:
		os.unlink(tmp.name)

def finddepends(liblist):
	"""
	Find packages owning a list of libraries

	Returns:
	  dependlist -- a dictionary { package => set(libraries) }
	  orphans -- the list of libraries without owners
	"""
	dependlist = defaultdict(set)

	somatches = {}
	actualpath = {}

	knownlibs = set(liblist)
	foundlibs = set()

	actualpath = dict((j, os.path.realpath('/' + j)[1:]) for j in knownlibs)

	# Sometimes packages don't include all so .so, .so.1, .so.1.13, .so.1.13.19 files
	# They rely on ldconfig to create all the symlinks
	# So we will strip off the matching part of the files and use this regexp to match the rest
	so_end = re.compile('(\.\d+)*')
	# Whether we should even look at a particular file
	is_so = re.compile('\.so')

	for pkg in Namcap.package.get_installed_packages():
		for j, fsize, fmode in pkg.files:
			if not is_so.search(j):
				continue

			for k in knownlibs:
				# File must be an exact match or have the right .so ending numbers
				# i.e. gpm includes libgpm.so and libgpm.so.1.19.0, but everything links to libgpm.so.1
				# We compare find libgpm.so.1.19.0 startswith libgpm.so.1 and .19.0 matches the regexp
				if j == actualpath[k] or (j.startswith(actualpath[k]) and so_end.match(j[len(actualpath[k]):])):
					dependlist[pkg.name].add(k)
					foundlibs.add(k)

	orphans = list(knownlibs - foundlibs)
	return dependlist, orphans

def filllibcache():
	var = subprocess.Popen('ldconfig -p', 
			env = {"LANG": "C"},
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE).communicate()
	libline = re.compile('\s*(.*) \((.*)\) => (.*)')
	for j in var[0].decode('ascii').splitlines():
		g = libline.match(j)
		if g != None:
			if g.group(2).startswith('libc6,x86-64'):
				libcache['x86-64'][g.group(1)] = g.group(3)
			else:
				# TODO: This is bogus; what do non x86-architectures print?
				libcache['i686'][g.group(1)] = g.group(3)


class SharedLibsRule(TarballRule):
	name = "sodepends"
	description = "Checks dependencies caused by linked shared libraries"
	def analyze(self, pkginfo, tar):
		liblist = {}
		dependlist = {}
		filllibcache()
		os.environ['LC_ALL'] = 'C'

		for entry in tar:
			if not entry.isfile():
				continue
			f = tar.extractfile(entry)
			scanlibs(f, entry.name, liblist)
			f.close()

		# Ldd all the files and find all the link and script dependencies
		dependlist, orphans = finddepends(liblist)

		# Handle "no package associated" errors
		self.warnings.extend([("library-no-package-associated %s", i)
			for i in orphans])

		# Print link-level deps
		for pkg, libraries in dependlist.items():
			if isinstance(libraries, set):
				files = list(libraries)
				needing = set().union(*[liblist[lib] for lib in libraries])
				reasons = pkginfo.detected_deps.setdefault(pkg, [])
				reasons.append((
					"libraries-needed %s %s",
					(str(files), str(list(needing)))
					))
				self.infos.append(("link-level-dependence %s in %s", (pkg, str(files))))

		# Check for packages in testing
		for i in dependlist.keys():
			p = Namcap.package.load_from_db(i, 'testing')
			q = Namcap.package.load_from_db(i)
			if p != None and q != None and p["version"] == q["version"] :
				self.warnings.append(("dependency-is-testing-release %s", i))

# vim: set ts=4 sw=4 noet:
