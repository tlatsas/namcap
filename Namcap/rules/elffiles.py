#
# namcap rules - elffiles
# Copyright (C) 2009 Hugo Doria <hugo@archlinux.org>
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
from Namcap.util import is_elf, clean_filename
from Namcap.ruleclass import *

# Valid directories for ELF files
valid_dirs = ['bin/', 'sbin/', 'usr/bin/', 'usr/sbin/', 'lib/',
		'usr/lib/', 'usr/lib32/']

class package(TarballRule):
	name = "elffiles"
	description = "Check about ELF files outside some standard paths."
	def prereq(self):
		return "extract"
	def analyze(self, pkginfo, data):
		ret = [[], [], []]

		for dirpath, subdirs, files in os.walk(data):
			for i in files:
				file_path = os.path.join(dirpath, i)
				if not is_elf(file_path):
					# Not an ELF file, nothing to check
					continue
				clean_file_path = clean_filename(file_path)
				in_valid_dir = False
				for valid in valid_dirs:
					if clean_file_path.startswith(valid):
						# Found a valid path prefix
						in_valid_dir = True
						break
				if not in_valid_dir:
					ret[0].append(("elffile-not-in-allowed-dirs %s", clean_file_path))

		return ret

# vim: set ts=4 sw=4 noet:
