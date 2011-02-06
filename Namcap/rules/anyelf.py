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
	name = "anyelf"
	description = "Check for ELF files to see if a package should be 'any' architecture"
	def prereq(self):
		return "tar"
	def analyze(self, pkginfo, tar):
		ret = [[], [], []]
		found_elffiles = []

		for entry in tar.getmembers():
			if not entry.isfile():
				continue
			f = tar.extractfile(entry)
			if f.read(4) == b"\x7fELF":
				found_elffiles.append(entry.name)

		if pkginfo.arch and pkginfo.arch[0] == 'any':
			ret[0] = [("elffile-in-any-package %s", i)
					for i in found_elffiles]
		else:
			if len(found_elffiles) == 0:
				ret[1].append(("no-elffiles-not-any-package", ()))
		return ret

# vim: set ts=4 sw=4 noet:
