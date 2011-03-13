# -*- coding: utf-8 -*-
#
# namcap rules - missingvars
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
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

"""Checks for missing variables in PKGBUILD"""

import re
from Namcap.ruleclass import *

RE_IS_HEXNUMBER = re.compile("[0-9a-f]+")

class ChecksumsRule(PkgbuildRule):
	name = "checksums"
	description = "Verifies checksums are included in a PKGBUILD"
	def analyze(self, pkginfo, tar):
		checksums=[('md5', 32), ('sha1', 40), ('sha256', 64), ('sha384', 96), ('sha512', 128)]

		if "source" in pkginfo:
			haschecksums = False
			for sumname, sumlen in checksums:
				if (sumname + 'sums') in pkginfo:
					haschecksums = True
			if not haschecksums:
				self.errors.append(("missing-checksums", ()))
		else:
			pkginfo["source"] = []

		for sumname, sumlen in checksums:
			sumname += 'sums'
			if sumname in pkginfo:
				if len(pkginfo["source"]) > len(pkginfo[sumname]):
					self.errors.append(("not-enough-checksums %s %i needed",
						          (sumname, len(pkginfo["source"]))))
				elif len(pkginfo["source"]) < len(pkginfo[sumname]):
					self.errors.append(("too-many-checksums %s %i needed",
						          (sumname, len(pkginfo["source"]))))
				for sum in pkginfo[sumname]:
					if len(sum) != sumlen or not RE_IS_HEXNUMBER.match(sum):
						self.errors.append(("improper-checksum %s %s", (sumname, sum)))

class TagsRule(PkgbuildRule):
	name = "tags"
	description = "Looks for Maintainer and Contributor comments"
	def analyze(self, pkginfo, tar):
		contributortag = 0
		maintainertag = 0
		idtag = 0
		for i in pkginfo.pkgbuild:
			if re.match("#\s*Contributor\s*:", i) != None:
				contributortag = 1
			if re.match("#\s*Maintainer\s*:", i) != None:
				maintainertag = 1

		if contributortag != 1:
			self.infos.append(("missing-contributor", ()))

		if maintainertag != 1:
			self.warnings.append(("missing-maintainer", ()))

# vim: set ts=4 sw=4 noet:
