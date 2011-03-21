# 
# namcap rules - symlink
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
import os
from Namcap.ruleclass import *

class package(TarballRule):
	name = "symlink"
	description = "Checks that symlinks point to the right place"
	def analyze(self, pkginfo, tar):
		filenames = [s.name for s in tar]
		for i in tar:
			if i.issym():
				self.infos.append(("symlink-found %s points to %s", (i.name, i.linkname)))
				linktarget = i.linkname
				linklead = os.path.dirname(i.name)
				# os.path.join drops the 1st arg if the 2nd one is absolute
				linkdest = os.path.join(linklead, linktarget)
				linkdest = os.path.normpath(linkdest).lstrip('/')
				if linkdest not in filenames:
					self.errors.append(("dangling-symlink %s points to %s", (i.name, i.linkname)))
			if i.islnk():
				self.infos.append(("hardlink-found %s points to %s", (i.name, i.linkname)))
				if i.linkname not in filenames:
					self.errors.append(("dangling-hardlink %s points to %s", (i.name, i.linkname)))

# vim: set ts=4 sw=4 noet:
