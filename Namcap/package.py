# -*- coding: utf-8 -*-
# 
# namcap rules - package info structure
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

import re

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

	def __init__(self, data = None, pkginfo = None, db = None):
		"""
		A PacmanPackage object can be ininitialised from:
		* a dictionary (then its contents are updated accordingly)
		* the contents of a .PKGINFO file
		* the contents of a database entry or the output of parsepkgbuild
		"""

		# Usual attributes
		self.is_split = False
		self.detected_deps = []

		# Init from a dictionary
		if data is not None:
			self.__dict__.update(data)

		# Parsing of .PKGINFO files from tarballs
		if isinstance(pkginfo, str):
			for i in pkginfo.splitlines():
				m = re.match('(.*) = (.*)', i)
				if m != None:
					lhs = m.group(1)
					rhs = m.group(2)
					if rhs != '':
						self.__dict__.setdefault(lhs, []).append(rhs)
		elif pkginfo is not None:
			raise TypeError("argument 'pkginfo' must be a string")

		# Parsing of database entries or parsepkgbuild output
		if isinstance(db, str):
			attrname = None
			for line in db.split('\n'):
				if line.startswith('%'):
					attrname = line.strip('%').lower()
				elif line.strip() == '':
					attrname = None
				elif attrname != None:
					self.__dict__.setdefault(attrname, []).append(line)
		elif db is not None:
			raise TypeError("argument 'pkginfo' must be a string")

		# Cleanup
		self.process()

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

# vim: set ts=4 sw=4 noet:
