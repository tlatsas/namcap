# 
# namcap rules - invalidstartdir
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

import re
from Namcap.ruleclass import *

class package(PkgbuildRule):
	name = "invalidstartdir"
	description = "Looks for references to $startdir"
	def analyze(self, pkginfo, tar):
		for i in pkginfo.pkgbuild:
			startdirs = re.split('\${?startdir}?"?', i)
			for j in startdirs[1:]:
				if j[:4] != '/pkg' and j[:4] != '/src':
					self.errors.append(("file-referred-in-startdir", ()))
				elif j[:4] == '/pkg':
					self.errors.append(("use-pkgdir", ()))
				elif j[:4] == '/src':
					self.errors.append(("use-srcdir", ()))

# vim: set ts=4 sw=4 noet:
