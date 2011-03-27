# 
# namcap rules - array
# Copyright (C) 2003-2009 Jesse Young <jesseyoung@gmail.com>
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

"""Verifies that array variables are actually arrays"""

import re
from Namcap.ruleclass import *

class package(PkgbuildRule):
	name = "array"
	description = "Verifies that array variables are actually arrays"
	def analyze(self, pkginfo, tar):
		arrayvars = ['arch', 'license', 'depends', 'makedepends',
			 'optdepends', 'checkdepends', 'provides', 'conflicts' , 'replaces',
			 'backup', 'source', 'noextract', 'md5sums',
			 'sha1sums', 'sha256sums', 'sha384sums', 'sha512sums']
		for i in pkginfo.pkgbuild:
			m = re.match('\s*(.*)\s*=\s*(.*)$', i)
			for j in arrayvars:
				if m and m.group(1) == j:
					if not m.group(2).startswith('('):
						self.warnings.append(("variable-not-array %s", j))

# vim: set ts=4 sw=4 noet:
