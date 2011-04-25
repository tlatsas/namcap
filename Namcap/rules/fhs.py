# 
# namcap rules - fhs
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

import os
import tarfile
from Namcap.ruleclass import *

class FHSRule(TarballRule):
	name = "directoryname"
	description = "Checks for standard directories."
	def analyze(self, pkginfo, tar):
		valid_paths = [
				'bin/', 'etc/', 'lib/', 'sbin/', 'opt/', 'srv/',
				'usr/bin/', 'usr/include/', 'usr/lib/', 'usr/lib32/',
				'usr/sbin/', 'usr/share/',
				'var/cache/', 'var/lib/', 'var/lock/', 'var/log/', 'var/opt/',
				'var/spool/', 'var/state/',
				'.PKGINFO', '.INSTALL', '.CHANGELOG',
		]
		forbidden_paths = [
				'tmp/', 'var/tmp/',
				'run/', 'var/run/',
				'var/lock/'
		]
		for entry in tar.getmembers():
			name = os.path.normpath(entry.name)
			if entry.isdir():
				name += '/'

			# check for files in wrong dirs, directory itself will be
			# catched by emptydirs rule
			if name in forbidden_paths:
				continue
			bad_dirs = [dirname for dirname in forbidden_paths
					if name.startswith(dirname)]
			if len(bad_dirs) > 0:
				self.errors.append(('file-in-temporary-dir %s',	name))
				continue

			# matches directory names or parent directories
			good_dirs = [dirname for dirname in valid_paths
				if name.startswith(dirname) or dirname.startswith(name)]
			if len(good_dirs) == 0:
				self.warnings.append(("file-in-non-standard-dir %s", name))

class FHSManpagesRule(TarballRule):
	name = "fhs-manpages"
	description = "Verifies correct installation of man pages"
	def analyze(self, pkginfo, tar):
		gooddir = 'usr/share/man'
		bad_dir = 'usr/man'
		for i in tar.getmembers():
			if not i.isfile():
				continue
			if i.name.startswith(bad_dir):
				self.errors.append(("non-fhs-man-page %s", i.name))
			elif not i.name.startswith(gooddir):
				#Check everything else to see if it has a 'man' path component
				for part in i.name.split(os.sep):
					if part == "man":
						self.warnings.append(("potential-non-fhs-man-page %s", i.name))

class FHSInfoPagesRule(TarballRule):
	name = "fhs-infopages"
	description = "Verifies correct installation of info pages"
	def analyze(self, pkginfo, tar):
		for i in tar.getmembers():
			if not i.isfile():
				continue
			if i.name.startswith('usr/info'):
				self.errors.append(("non-fhs-info-page %s", i.name))
			elif not i.name.startswith('usr/share/info'):
				for part in i.name.split(os.sep):
					if part == "info":
						self.warnings.append(("potential-non-fhs-info-page %s", i.name))

# vim: set ts=4 sw=4 noet:
