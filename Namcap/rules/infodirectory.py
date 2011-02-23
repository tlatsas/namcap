#
# namcap rules - infodirectory
# Copyright (C) 2008-2009 Allan McRae <allan@archlinux.org>
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

class InfodirRule(TarballRule):
	name = "infodirectory"
	description = "Checks for info directory file."
	def analyze(self, pkginfo, tar):
		for i in tar.getnames():
			if i == "usr/share/info/dir":
				self.errors.append(("info-dir-file-present %s", i))

class InfoInstallRule(TarballRule):
	name = "infoinstall"
	description = "Checks that info files are correctly installed."
	def analyze(self, pkginfo, tar):
		info_installed = False
		info_present = False

		for i in tar:
			if i.name == ".INSTALL":
				install = tar.extractfile(i)
				if b"install-info" in install.read():
					info_installed = True
				install.close()

			if i.name.startswith("usr/share/info/"):
				info_present = True

		if info_present and not info_installed:
			self.errors.append(("info-dir-not-updated", ()))

# vim: set ts=4 sw=4 noet:
