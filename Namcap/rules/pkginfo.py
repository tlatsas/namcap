# 
# namcap rules - package variables
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

"These rules checks basic sanity of package metadata"

import re
from Namcap.ruleclass import PkgInfoRule

class CapsPkgnameRule(PkgInfoRule):
	name = "capsnamespkg"
	description = "Verifies package name in package does not include upper case letters"
	def analyze(self, pkginfo, tar):
		if re.search('[A-Z]', pkginfo["name"]) != None:
			self.errors.append(("package-name-in-uppercase", ()))

class UrlRule(PkgInfoRule):
	name = "urlpkg"
	description = "Verifies url is included in a package file"
	def analyze(self, pkginfo, tar):
		if "url" not in pkginfo:
			self.errors.append(("missing-url", ()))

class LicenseRule(PkgInfoRule):
	name = "license"
	description = "Verifies license is included in a PKGBUILD"
	def analyze(self, pkginfo, tar):
		if "license" not in pkginfo or len(pkginfo["license"]) == 0:
			self.errors.append(("missing-license", ()))

# vim: set ts=4 sw=4 noet:
