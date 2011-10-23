#
# namcap rules - elffiles
# Copyright (C) 2009 Hugo Doria <hugo@archlinux.org>
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
import tempfile
import subprocess

from Namcap.util import is_elf, clean_filename
from Namcap.ruleclass import *

# Valid directories for ELF files
valid_dirs = ['bin/', 'sbin/', 'usr/bin/', 'usr/sbin/', 'lib/',
		'usr/lib/', 'usr/lib32/']

class ELFPaths(TarballRule):
	name = "elfpaths"
	description = "Check about ELF files outside some standard paths."
	def analyze(self, pkginfo, tar):
		invalid_elffiles = []

		for entry in tar:
			# is it a regular file ?
			if not entry.isfile():
				continue
			# is it outside standard binary dirs ?
			is_outside_std_dirs = True
			for d in valid_dirs:
				if entry.name.startswith(d):
					is_outside_std_dirs = False
					break
			if not is_outside_std_dirs:
				continue
			# is it an ELF file ?
			f = tar.extractfile(entry)
			if f.read(4) == b"\x7fELF":
				invalid_elffiles.append(entry.name)

		self.errors = [("elffile-not-in-allowed-dirs %s", i)
				for i in invalid_elffiles]

class ELFTextRelocationRule(TarballRule):
	"""
	Check for text relocations in ELF files.

	Introduced by FS#26434. Text relocations are detected by the
	eu-findtextrel utility from elfutils. eu-findtextrel returns 0
	whenever the input file has a text relocation section.
	"""

	name = "elftextrel"
	description = "Check for text relocations in ELF files."

	def analyze(self, pkginfo, tar):
		files_with_textrel = []

		for entry in tar:
			if not entry.isfile():
				continue
			f = tar.extractfile(entry)
			magic = f.read(4)
			if magic != b"\x7fELF":
				continue

			# read the rest of file
			tmp = tempfile.NamedTemporaryFile(delete=False)
			tmp.write(magic + f.read())
			tmp.close()

			try:
				ret = subprocess.call(["eu-findtextrel", tmp.name],
					stdout=open(os.devnull, 'w'),
					stderr=open(os.devnull, 'w'))
				if ret == 0:
					files_with_textrel.append(entry.name)
			finally:
				os.unlink(tmp.name)

		if files_with_textrel:
			self.warnings = [("elffile-with-textrel %s", i)
					for i in files_with_textrel]

# vim: set ts=4 sw=4 noet:
