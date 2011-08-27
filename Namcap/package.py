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

import os
import subprocess
import re
import collections

import pyalpm
_pyalpm_version_tuple = tuple(int(n) for n in pyalpm.version().split('.'))
if _pyalpm_version_tuple < (0, 5):
	raise DeprecationWarning("pyalpm versions <0.5 are no longer supported")

import pycman.config
pyalpm_handle = pycman.config.init_with_config('/etc/pacman.conf')

DEPENDS_RE = re.compile("([^<>=:]+)([<>]?=.*)?(: .*)?")

def strip_depend_info(value):
	"""
	Strip all the depend version info off ('neon>=0.25.5-4' => 'neon').
	Also remove any trailing description (for optdepends)
	"""
	m = DEPENDS_RE.match(value)
	if m is None:
		raise ValueError("Invalid dependency specification")
	return m.group(1)

class PacmanPackage(collections.MutableMapping):
	strings = ['base', 'name', 'version', 'desc', 'url', 'builddate',
			'packager', 'install', 'filename', 'csize', 'isize',
			'pkgfunction']
	equiv_vars = {
		'pkgname': 'name',
		'md5sum': 'md5sums',
		'sha1sum': 'sha1sums',
		'depend': 'depends',
		'pkgdesc': 'desc',
		'size': 'isize',
		'optdepend': 'optdepends',
		'license': 'licenses'
		}

	@classmethod
	def canonical_varname(cls, varname):
		try:
			return cls.equiv_vars[varname]
		except KeyError:
			return varname

	def __init__(self, data = None, pkginfo = None, db = None):
		"""
		A PacmanPackage object can be ininitialised from:
		* a dictionary (then its contents are updated accordingly)
		* the contents of a .PKGINFO file
		* the contents of a database entry or the output of parsepkgbuild
		"""

		# Usual attributes
		self.is_split = False
		# a dictionary { package => [reasons why it is needed] }
		self.detected_deps = {}
		self._data = {}

		# Init from a dictionary
		if isinstance(data, dict):
			for k, v in data.items():
				self[k] = v

		# Parsing of .PKGINFO files from tarballs
		if isinstance(pkginfo, str):
			for i in pkginfo.splitlines():
				m = re.match('(.*) = (.*)', i)
				if m != None:
					lhs = m.group(1)
					rhs = m.group(2)
					if rhs != '':
						self.setdefault(lhs, []).append(rhs)
		elif pkginfo is not None:
			raise TypeError("argument 'pkginfo' must be a string")

		# Parsing of database entries or parsepkgbuild output
		if isinstance(db, str):
			attrname = None
			if '\0' in db:
				self.is_split = True
				parts = db.split("\0")
				self.subpackages = [PacmanPackage(db = s) for s in parts[1:]]
				db = parts[0]
			for line in db.split('\n'):
				if line.startswith('%'):
					attrname = line.strip('%').lower()
				elif line.strip() != '':
					self.setdefault(attrname, []).append(line)
		elif db is not None:
			raise TypeError("argument 'pkginfo' must be a string")

		# Cleanup
		self.process()

	def __iter__(self):
		return iter(self._data)

	def __len__(self):
		return len(self._data)

	def __getitem__(self, key):
		return self._data[self.canonical_varname(key)]

	def __setitem__(self, key, value):
		k = self.canonical_varname(key)
		self._data[k] = value

	def __contains__(self, key):
		return self.canonical_varname(key) in self._data

	def __delitem__(self, key):
		del self._data[self.canonical_varname(key)]

	def process_strings(self):
		"""
		Turn all the instance properties listed in self.strings into strings instead of lists
		"""
		for i in self.strings:
			if i in self:
				if isinstance(self[i], list):
					self[i] = self[i][0]

	def clean_depends(self):
		"""
		Strip all the depend version info off ('neon>=0.25.5-4' => 'neon').
		Also clean our optdepends and remove any trailing description.
		The original arrays are copied to orig_depends and orig_optdepends respectively.
		"""

		if 'depends' in self._data:
			self["orig_depends"] = self["depends"]
			self["depends"] = [strip_depend_info(d) for d in self['orig_depends']]
		if 'makedepends' in self._data:
			self["orig_makedepends"] = self["makedepends"]
			self["makedepends"] = [strip_depend_info(d) for d in self['orig_makedepends']]
		if 'optdepends' in self._data:
			self["orig_optdepends"] = self["optdepends"]
			self["optdepends"] = [strip_depend_info(d) for d in self['orig_optdepends']]
		if 'provides' in self._data:
			self["orig_provides"] = self["provides"]
			self["provides"] = [strip_depend_info(d) for d in self['orig_provides']]

	def process(self):
		"""
		After all the text processing happens, call this to sanitize the PacmanPackage object a bit
		"""
		self.process_strings()
		self.clean_depends()

	def __repr__(self):
		if not self.is_split:
			return "PacmanPackage(%s)" % repr(self._data)
		else:
			children = ','.join(repr(p) for p in self.subpackages)
			return ("PacmanPackage(%s,[%s])" %
					(repr(self._data), children))

def load_from_pkgbuild(path):
	# Load all the data like we normally would
	workingdir = os.path.dirname(path)
	if workingdir == '':
		workingdir = None
	filename = os.path.basename(path)
	process = subprocess.Popen(['parsepkgbuild', filename],
			stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=workingdir)
	out, err = process.communicate()
	out = out.decode('utf-8', 'ignore')
	err = err.decode('utf-8', 'ignore')
	# this means parsepkgbuild returned an error, so we are not valid
	if process.returncode > 0:
		if out:
			print("Error:", out)
		if err:
			print("Error:", err, file=sys.stdout)
		return None
	ret = PacmanPackage(db = out)

	# Add a nice little .pkgbuild surprise
	pkgbuild = open(path, errors="ignore")
	ret.pkgbuild = pkgbuild.read().replace("\\\n", " ").splitlines()
	pkgbuild.close()

	return ret

def load_from_alpm(pmpkg):
	variables = ['name', 'version', 'conflicts', 'url',
			'depends', 'desc', 'files', 'groups',
			'has_scriptlet', 'size', 'licenses',
			'optdepends', 'packager', 'provides', 'replaces']
	values = dict((v, getattr(pmpkg, v)) for v in variables)

	# arch is a list for PKGBUILDs, we do the same for tarball packages
	values['arch'] = [pmpkg.arch]
	# also drop md5sums for backed up files
	values['backup'] = [name for (name, md5) in pmpkg.backup]

	return PacmanPackage(data = values)

def load_from_tarball(path):
	try:
		p = pyalpm_handle.load_pkg(path)
	except pyalpm.error:
		return None

	return load_from_alpm(p)

def load_from_db(pkgname, dbname = None):
	if dbname is None:
		# default is loading local database
		db = pyalpm_handle.get_localdb()
	else:
		db = pyalpm_handle.register_syncdb(dbname, 0)
	p = db.get_pkg(pkgname)

	if p is None:
		p = lookup_provider(pkgname, db)
	if p is not None:
		p = load_from_alpm(p)
	return p

def get_installed_packages():
	return pyalpm_handle.get_localdb().pkgcache

def lookup_provider(pkgname, db):
	for pkg in db.pkgcache:
		if pkgname in pkg.provides:
			return pkg

# vim: set ts=4 sw=4 noet:
