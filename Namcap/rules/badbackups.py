# 
# namcap rules - badbackups
# Copyright (C) 2004-2009 Ben Mazer <ben@benmazer.net>
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

"""Checks for bad backup entries"""

import re
from Namcap.ruleclass import *

class package(PkgbuildRule):
	name = "badbackups"
	description = "Checks for bad backup entries"
	def analyze(self, pkginfo, tar):
		if hasattr(pkginfo, 'backup'):
			for item in pkginfo.backup:
				if re.match('^/', item) != None:
					self.errors.append(("backups-preceding-slashes", ()))

# vim: set ts=4 sw=4 noet:
