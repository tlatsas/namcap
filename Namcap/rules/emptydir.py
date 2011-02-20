# 
# namcap rules - emptydir
# Copyright (C) 2004-2009 Jason Chu <jason@archlinux.org>
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
from Namcap.ruleclass import *

class package(TarballRule):
	name = "emptydir"
	description = "Warns about empty directories in a package"
	def analyze(self, pkginfo, tar):
		dirs = []
		entries = []
		for entry in tar:
			if entry.isdir():
				dirs.append(entry.name.rstrip("/"))
			entries.append(entry.name.rstrip("/"))
		nonemptydirs = [os.path.dirname(x) for x in entries]
		self.warnings = [("empty-directory %s", d)
				for d in (set(dirs) - set(nonemptydirs))]

# vim: set ts=4 sw=4 noet:
