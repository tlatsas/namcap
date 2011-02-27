# 
# namcap rules - split package checks
# Copyright (C) 2011 Rémy Oudompheng <remy@archlinux.org>
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

"This module contains rules that check coherence of split PKGBUILDs."

from Namcap.ruleclass import PkgbuildRule
import Namcap.depends

class PackageFunctionsRule(PkgbuildRule):
	"""
	This rule checks for existence of package_* functions
	in split PKGBUILDs. It relies on the output of parsepkgbuild
	which gives the type of the package_xxx object in the PKGBUILD.
	"""
	name = "splitpkgfunctions"
	description = "Checks that all package_* functions exist."

	def analyze(self, pkginfo, pkgbuild):
		if not pkginfo.is_split:
			return
		# All subpackages should have a valid package function
		for subpkg in pkginfo.subpackages:
			if subpkg["pkgfunction"] != "function":
				self.errors.append(
						("missing-pkgfunction %s", subpkg["name"])
						)

class SplitPkgMakedepsRule(PkgbuildRule):
	"""
	This rule checks that the global makedepends of a split
	PKGBUILD cover all needed depends of individual children
	packages.
	"""
	name = "splitpkgmakedeps"
	description = "Checks that a split PKGBUILD has enough makedeps."

	def analyze(self, pkginfo, pkgbuild):
		if not pkginfo.is_split:
			return
		# Find dependencies specified in makedepends
		global_deps = set()
		global_deps.update(pkginfo["names"])
		if "depends" in pkginfo:
			global_deps.update(pkginfo["depends"])
		if "makedepends" in pkginfo:
			global_deps.update(pkginfo["makedepends"])

		global_deps |= Namcap.depends.getcovered(global_deps)

		# Read dependencies specified in subpackages
		local_deps = set()
		for s in pkginfo.subpackages:
			if "depends" in s:
				local_deps.update(s["depends"])
			if "makedepends" in s:
				local_deps.update(s["makedepends"])

		if not local_deps.issubset(global_deps):
			missing = list(local_deps - global_deps)
			self.errors.append(("missing-makedeps %s", str(missing)))

# vim: set ts=4 sw=4 noet:
