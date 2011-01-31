#
# namcap rules - anyelf
# Copyright (C) 2010 Dan McGee <dan@archlinux.org>
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

"""
Check for ELF files to see if a package should be 'any' architecture
"""

import os
from Namcap.util import is_elf, clean_filename
from Namcap.ruleclass import *

class package(TarballRule):
	def short_name(self):
		return "anyelf"
	def long_name(self):
		return "Check for ELF files to see if a package should be 'any' architecture"
	def prereq(self):
		return "extract"
	def analyze(self, pkginfo, data):
		ret = [[], [], []]
		found_elffiles = []

		for dirpath, subdirs, files in os.walk(data):
			for i in files:
				file_path = os.path.join(dirpath, i)
				# Checking for ELF files
				if is_elf(file_path):
					found_elffiles.append(clean_filename(file_path))

		if pkginfo.arch and pkginfo.arch[0] == 'any':
			if len(found_elffiles) > 0:
				for i in found_elffiles:
					ret[0].append(("elffile-in-any-package %s", i))
		else:
			if len(found_elffiles) == 0:
				ret[1].append(("no-elffiles-not-any-package", ()))
		return ret

# vim: set ts=4 sw=4 noet:
