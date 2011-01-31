# 
# namcap rules - depends
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
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

import re, os, os.path, pacman, subprocess
from Namcap.util import is_elf, script_type
from Namcap.ruleclass import *

pkgcache = {}

def load(name, path=None):
	if name not in pkgcache:
		pkgcache[name] = pacman.load(name)
	return pkgcache[name]

libcache = {'i686': {}, 'x86-64': {}}

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

def scanlibs(filename, liblist):
	"""
	Run "readelf -d" on a file
	If it depends on a library, store that library's path.
	"""
	sharedlibs, scripts = liblist
	shared = re.compile('Shared library: \[(.*)\]')

	if is_elf(filename):
		var = subprocess.Popen('readelf -d ' + filename,
				shell=True,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE).communicate()
		for j in var[0].splitlines():
			n = shared.search(j)
			# Is this a Shared library: line?
			if n != None:
				# Find out its architecture
				architecture = figurebitsize(j)
				try:
					libpath = os.path.abspath(
							libcache[architecture][n.group(1)])[1:]
					sharedlibs.setdefault(libpath, {})[filename] = 1
				except KeyError:
					# We didn't know about the library, so add it for fail later
					sharedlibs.setdefault(n.group(1), {})[filename] = 1
	# Maybe it is a script file
	else:
		cmd = script_type(filename)
		if cmd != None:
			scripts.setdefault(cmd, {})[filename] = 1

def finddepends(liblist):
	dependlist = {}
	foundlist = []

	somatches = {}
	actualpath = {}

	knownlibs = liblist.keys()

	for j in knownlibs:
		actualpath[j] = os.path.realpath('/'+j)[1:]

	# Sometimes packages don't include all so .so, .so.1, .so.1.13, .so.1.13.19 files
	# They rely on ldconfig to create all the symlinks
	# So we will strip off the matching part of the files and use this regexp to match the rest
	so_end = re.compile('(\.\d+)*')
	# Whether we should even look at a particular file
	is_so = re.compile('\.so')

	pacmandb = '/var/lib/pacman/local'
	for i in os.listdir(pacmandb):
		if os.path.isfile(pacmandb+'/'+i+'/files'):
			file = open(pacmandb+'/'+i+'/files')
			for j in file:
				if not is_so.search(j):
					continue

				for k in knownlibs:
					# File must be an exact match or have the right .so ending numbers
					# i.e. gpm includes libgpm.so and libgpm.so.1.19.0, but everything links to libgpm.so.1
					# We compare find libgpm.so.1.19.0 startswith libgpm.so.1 and .19.0 matches the regexp
					if j == actualpath[k] or (j.startswith(actualpath[k]) and so_end.match(j[len(actualpath[k]):])):
						n = re.match('(.*)-([^-]*)-([^-]*)', i)
						if n.group(1) not in dependlist:
							dependlist[n.group(1)] = {}
						for x in liblist[k]:
							dependlist[n.group(1)][x] = 1
						knownlibs.remove(k)
						foundlist.append(k)
			file.close()

	ret = []
	# knownlibs only contains what hasn't been found at this point
	for i in knownlibs:
		ret.append(("library-no-package-associated %s", i))
	return dependlist, ret

def getprovides(depends, provides):
	for i in depends.keys():
		pac = load(i)

		if pac != None and hasattr(pac, 'provides') and pac.provides != None:
			provides[i] = pac.provides

def filllibcache():
	var = subprocess.Popen('ldconfig -p', 
			shell=True,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE).communicate()
	libline = re.compile('\s*(.*) \((.*)\) => (.*)')
	for j in var[0].splitlines():
		g = libline.match(j)
		if g != None:
			if g.group(2).startswith('libc6,x86-64'):
				libcache['x86-64'][g.group(1)] = g.group(3)
			else:
				libcache['i686'][g.group(1)] = g.group(3)


class package(TarballRule):
	def short_name(self):
		return "depends"
	def long_name(self):
		return "Checks dependencies semi-smartly."
	def prereq(self):
		return "extract"
	def analyze(self, pkginfo, data):
		liblist = [{}, {}]
		dependlist = {}
		smartdepend = {}
		smartprovides = {}
		covereddepend = {}
		pkgcovered = {}
		ret = [[], [], []]
		filllibcache()
		os.environ['LC_ALL'] = 'C'

		for dirpath, subdirs, files in os.walk(data):
			for i in files:
				scanlibs(os.path.join(dirpath, i), liblist)

		# Ldd all the files and find all the link and script dependencies
		dependlist, tmpret = finddepends(liblist[0])

		# Handle "no package associated" errors
		for i in tmpret:
			ret[1].append(i)

		# Remove the package name from that list, we can't depend on ourselves.
		if pkginfo.name in dependlist:
			del dependlist[pkginfo.name]

		# Print link-level deps
		for i, v in dependlist.iteritems():
			if type(v) == dict:
				files = [x[len(data)+1:] for x in v.keys()]
				ret[2].append(("link-level-dependence %s in %s", (i, str(files))))

		# Do the script handling stuff
		for i, v in liblist[1].iteritems():
			if i not in dependlist:
				dependlist[i] = {}
			for j in v.keys():
				dependlist[i][j] = 1
			files = [x[len(data)+1:] for x in v.keys()]
			ret[2].append(("script-link-detected %s in %s", (i, str(files))))

		# Check for packages in testing
		if os.path.isdir('/var/lib/pacman/sync/testing'):
			for i in dependlist.keys():
				p = pacman.load(i, '/var/lib/pacman/sync/testing/')
				q = load(i)
				if p != None and q != None and p.version == q.version:
					ret[1].append(("dependency-is-testing-release %s", i))

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
			ret[2].append(("dependency-covered-by-link-dependence %s", i))

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
			all_dependencies = getattr(pkginfo, 'depends', []) + getattr(pkginfo, 'optdepends', []) + pkgcovered.keys()
			if (i not in all_dependencies and i != pkginfo.name
					and ((i not in smartprovides)
						or len([c for c in smartprovides[i] if c in pkgcovered]) == 0)):
					if type(dependlist[i]) == dict:
						ret[0].append(("dependency-detected-not-included %s from files %s", (i, str([x[len(data)+1:] for x in dependlist[i].keys()])) ))
					else:
						ret[0].append(("dependency-detected-not-included %s", i))
		if hasattr(pkginfo, 'depends'):
			for i in pkginfo.depends:
				if i in covereddepend and i in dependlist:
					ret[1].append(("dependency-already-satisfied %s", i))
				# if i is not in the depends as we see them and it's not in any of the provides from said depends
				elif i not in smartdepend and i not in [y for x in smartprovides.values() for y in x]:
					ret[1].append(("dependency-not-needed %s", i))
		ret[2].append(("depends-by-namcap-sight depends=(%s)", ' '.join(smartdepend.keys()) ))
		return ret

# vim: set ts=4 sw=4 noet:
