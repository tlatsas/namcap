# 
# namcap rules - libtool
# Copyright (C) 2005-2009 Simo Leone <simo@archlinux.org>
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

class package(TarballRule):
	name = "libtool"
	description = "Checks for libtool (*.la) files."
	def analyze(self, pkginfo, tar):
		for i in tar.getnames():
			if re.search('\.la$', i) != None:
				self.warnings.append(("libtool-file-present %s", i))

# vim: set ts=4 sw=4 noet:
