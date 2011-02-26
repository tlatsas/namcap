# 
# namcap rules - lotsofdocs
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

from Namcap.ruleclass import *

class package(TarballRule):
	name = "lots-of-docs"
	description = "See if a package is carrying more documentation than it should"
	def analyze(self, pkginfo, tar):
		if ('name' in pkginfo and
				(pkginfo["name"].endswith('-doc') or
				 pkginfo["name"].endswith('-docs'))):
			# Don't do anything if the package is called "*-doc"
			return
		docdir = 'usr/share/doc'
		size = 0
		docsize = 0

		for i in tar.getmembers():
			if i.name.startswith(docdir):
				docsize += i.size
			size += i.size

		if size > 0:
			ratio = docsize / float(size)
			if ratio > 0.50:
				self.warnings.append(("lots-of-docs %f", ratio * 100))

# vim: set ts=4 sw=4 noet:
