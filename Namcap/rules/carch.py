# 
# namcap rules - carch
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

"""Verifies that no specific host type is used"""

import re
from Namcap.ruleclass import *

class package(PkgbuildRule):
	name = "carch"
	description = "Verifies that no specific host type is used"
	def analyze(self, pkginfo, tar):
		arches = ['arm', 'i586', 'i686', 'ppc', 'x86_64']
		archmatch = re.compile(r'\b(%s)\b' % '|'.join(arches))
		# Match an arch=(i686) line
		archline = re.compile(r'\w*arch=')
		for line in pkginfo.pkgbuild:
			# strip any comments
			line = line.split('#')[0]
			match = archmatch.search(line)
			if match and not archline.match(line) and not '$CARCH' in line:
				self.warnings.append(("specific-host-type-used %s", match.group(1)))

# vim: set ts=4 sw=4 noet:
