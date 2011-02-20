# 
# namcap rules - hardlinks
# Copyright (C) 2011 Dan McGee <dan@archlinux.org>
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

from os.path import dirname
from Namcap.ruleclass import *

class package(TarballRule):
	name = "hardlinks"
	description = "Look for cross-directory/partition hard links"
	def analyze(self, pkginfo, tar):
		hardlinks = [i for i in tar.getmembers() if i.islnk() == True]
		for hardlink in hardlinks:
			if dirname(hardlink.name) != dirname(hardlink.linkname):
				self.errors.append(("cross-dir-hardlink %s %s",
					(hardlink.name, hardlink.linkname)))

# vim: set ts=4 sw=4 noet:
