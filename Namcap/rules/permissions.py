# 
# namcap rules - permissions
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

import stat
from Namcap.ruleclass import *

class package(TarballRule):
	name = "permissions"
	description = "Checks file permissions."
	def analyze(self, pkginfo, tar):
		for i in tar.getmembers():
			if not i.mode & stat.S_IROTH and not (i.issym() or i.islnk()):
				self.warnings.append(("file-not-world-readable %s", i.name))
			if i.mode & stat.S_IWOTH and not (i.issym() or i.islnk()):
				self.warnings.append(("file-world-writable %s", i.name))
			if not i.mode & stat.S_IXOTH and i.isdir():
				self.warnings.append(("directory-not-world-executable %s", i.name))
			if str(i.name).endswith('.a') and not (i.issym() or i.islnk()):
				if i.mode != 0o644 and i.mode != 0o444:
					self.warnings.append(("incorrect-library-permissions %s", i.name))
			if i.mode & (stat.S_ISUID | stat.S_ISGID):
				self.warnings.append(("file-setugid %s", i.name))

# vim: set ts=4 sw=4 noet:
