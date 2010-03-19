#
# namcap rules - utility functions
# Copyright (C) 2009 Dan McGee <dan@archlinux.org>
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
import re

def is_elf(path):
	"""
	Given a file path, ensure it exists and peek at the first few bytes
	to determine if it is an ELF file.
	"""
	if not os.path.isfile(path):
		return False
	fd = open(path)
	bytes = fd.read(4)
	fd.close()
	# magic elf header, present in binaries and libraries
	if bytes == "\x7FELF":
		return True
	else:
		return False

clean_filename = lambda s: re.search(r"/tmp/namcap\.[0-9]*/(.*)", s).group(1)

# vim: set ts=4 sw=4 noet:
