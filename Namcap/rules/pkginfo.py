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
	def short_name(self):
		return "capsnamespkg"
	def long_name(self):
		return "Verifies package name in package does not include upper case letters"
	def prereq(self):
		return "pkg"
	def analyze(self, pkginfo, tar):
		ret = [[], [], []]
		if re.search('[A-Z]', pkginfo.name) != None:
			ret[0].append(("package-name-in-uppercase", ()))
		return ret
	def type(self):
		return "tarball"

class UrlRule(PkgInfoRule):
	def short_name(self):
		return "urlpkg"
	def long_name(self):
		return "Verifies url is included in a package file"
	def prereq(self):
		return "pkg"
	def analyze(self, pkginfo, tar):
		ret = [[], [], []]
		if not hasattr(pkginfo, 'url'):
			ret[0].append(("missing-url", ()))
		return ret
	def type(self):
		return "tarball"

class LicenseRule(object):
	def short_name(self):
		return "license"
	def long_name(self):
		return "Verifies license is included in a PKGBUILD"
	def prereq(self):
		return ""
	def analyze(self, pkginfo, tar):
		ret = [[], [], []]
		if not hasattr(pkginfo, 'license') or len(pkginfo.license) == 0:
			ret[0].append(("missing-license", ()))
		return ret
	def type(self):
		return "pkgbuild"

# vim: set ts=4 sw=4 noet:
