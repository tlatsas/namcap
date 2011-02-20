# -*- coding: utf-8 -*-
#
# namcap rules - filenames
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

"""Checks for invalid filenames."""

import string
from Namcap.ruleclass import *

VALID_CHARS = string.ascii_letters + string.digits \
		+ string.punctuation + ' '

class package(TarballRule):
	name = "filenames"
	description = "Checks for invalid filenames."
	def analyze(self, pkginfo, tar):
		for i in tar.getnames():
			for c in i:
				if c not in VALID_CHARS:
					self.warnings.append(("invalid-filename", i))
					break

# vim: set ts=4 sw=4 noet:
