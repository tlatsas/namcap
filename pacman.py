# 
# namcap rules - pacman package interface
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

import tarfile, os, os.path, re, subprocess

pacmandb = '/var/lib/pacman/local/'

for i in open('/etc/pacman.conf'):
	m = re.match('\s*DBPath\s*=\s*([\S^#]+)', i)
	if m != None:
		pacmandb = os.path.join(m.group(1), 'local/')
		break

class PacmanPackage(object):
	strings = ['name', 'version', 'desc', 'url', 'builddate', 'packager', 'install', 'filename', 'csize', 'isize', ]
	equiv_vars = [
			('name', 'pkgname'),
			('md5sums', 'md5sum'),
			('sha1sums', 'sha1sum'),
			('depends', 'depend'),
			('desc', 'pkgdesc'),
			('isize', 'size'),
			('optdepends', 'optdepend'),
	]

	def __init__(self, **data):
		self.__dict__.update(data)

	def process_strings(self):
		"""
		Turn all the instance properties listed in self.strings into strings instead of lists
		"""
		for i in self.strings:
			value = getattr(self, i, None)
			if type(value) == list:
				setattr(self, i, value[0])

	def fix_equiv(self):
		"""
		Go through self.equiv_vars ( (new, old) ) and set all the old vars to new vars
		"""
		for new, old in self.equiv_vars:
			if hasattr(self, old):
				setattr(self, new, getattr(self, old))
				del self.__dict__[old]

	def clean_depends(self):
		"""
		Go through the special depends instance property and strip all the depend version info off ('neon>=0.25.5-4' => 'neon').
		Also clean our optdepends and remove any trailing description.
		The original arrays are copied to orig_depends and orig_optdepends respectively.
		"""
		def strip_depend_info(l):
			for item, value in enumerate(l):
				l[item] = value.split(':')[0].split('>')[0].split('<')[0].split('=')[0]

		if hasattr(self, 'depends'):
			self.orig_depends = self.depends[:]
			strip_depend_info(self.depends)
		if hasattr(self, 'makedepends'):
			self.orig_makedepends = self.makedepends[:]
			strip_depend_info(self.makedepends)
		if hasattr(self, 'optdepends'):
			self.orig_optdepends = self.optdepends[:]
			strip_depend_info(self.optdepends)
		if hasattr(self, 'provides'):
			self.orig_provides = self.provides[:]
			strip_depend_info(self.provides)

	def process(self):
		"""
		After all the text processing happens, call this to sanitize the PacmanPackage object a bit
		"""
		self.fix_equiv()
		self.process_strings()
		self.clean_depends()

def load(package, root=None):
	if root == None:
		root = pacmandb
	# We know it's a local package
	if os.path.isfile(package) and tarfile.is_tarfile(package):
		pkgtar = tarfile.open(package, "r")
		if not pkgtar:
			return None
		if not '.PKGINFO' in pkgtar.getnames():
			return None
		pkginfo = pkgtar.extractfile('.PKGINFO')
		ret = PacmanPackage()
		for i in pkginfo:
			m = re.match('(.*) = (.*)', i)
			if m != None:
				lhs = m.group(1)
				rhs = m.group(2)
				if rhs != '':
					ret.__dict__.setdefault(lhs, []).append(rhs)

		pkgtar.close()
		ret.process()
		return ret

	# Ooooo, it's a PKGBUILD
	elif package.endswith('PKGBUILD'):
		# Load all the data like we normally would
		workingdir = os.path.dirname(package)
		if workingdir == '':
			workingdir = None
		filename = os.path.basename(package)
		process = subprocess.Popen(['parsepkgbuild',filename], stdout=subprocess.PIPE, cwd=workingdir)
		data = process.communicate()
		# this means parsepkgbuild returned an error, so we are not valid
		if process.returncode > 0:
			return None
		ret = loaddb(None, data[0])

		# Add a nice little .pkgbuild surprise
		pkgbuild = open(package)
		ret.pkgbuild = pkgbuild.readlines()
		pkgbuild.close()

		ret.process()

		return ret

	else:
		searchstr = re.compile('(.*)-([^-]*)-([^-]*)')
		for i in os.listdir(root):
			n = searchstr.match(i)
			if n == None:
				continue
			if n.group(1) == package:
				# We found the package!
				return loadfromdir(os.path.join(root, i))

		# Maybe it's a provides then...
		for i in os.listdir(root):
			prov = loadfromdir(os.path.join(root, i))

			if prov != None and hasattr(prov, 'provides') and package in prov.provides:
				return prov

		return None

def loadfromdir(directory):
	"""Read package information from a directory in the database"""
	if not os.path.isdir(directory):
		return None
	ret = PacmanPackage()

	for info in ('desc', 'depends', 'files'):
		path = os.path.join(directory, info)
		if os.path.isfile(path):
			dbfile = open(path)
			loaddb(ret, dbfile.read())
			dbfile.close()

	ret.process()
	return ret

def loaddb(package, data):
	"""Read information from file data"""
	if package is None:
		package = PacmanPackage()

	attrname = None
	for line in data.split('\n'):
		if line.startswith('%'):
			attrname = line.strip('%').lower()
		elif line.strip() == '':
			attrname = None
		elif attrname != None:
			package.__dict__.setdefault(attrname, []).append(line)

	return package

def getprovides(provides):
	packagelist = []

	searchstr = re.compile('(.*)-([^-]*)-([^-]*)')
	for i in os.listdir(pacmandb):
		pac = loadfromdir(os.path.join(pacmandb, i))
		if hasattr(pac, 'provides') and provides in pac.provides:
			packagelist.append(pac.name)

	return packagelist
# vim: set ts=4 sw=4 noet:
