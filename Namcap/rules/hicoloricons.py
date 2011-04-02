#
# namcap rules - hicoloricons
# Copyright (C) 2009 Abhishek Dasgupta <abhidg@gmail.com>
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
	name = "hicoloricons"
	description = "Checks whether the hicolor icon cache is updated."
	def analyze(self, pkginfo, tar):
		if "usr/share/icons/hicolor" in tar.getnames():
			reasons = pkginfo.detected_deps.setdefault("hicolor-icon-theme", [])
			reasons.append( ('hicolor-icon-theme-needed-for-hicolor-dir',()) )

			if ".INSTALL" not in tar.getnames():
				self.errors.append(("hicolor-icon-cache-not-updated", ()))
			else:
				f = tar.extractfile(".INSTALL")
				install_script = f.read().decode("utf-8", "ignore")
				if ("gtk-update-icon-cache" not in install_script) and ("xdg-icon-resource" not in install_script):
					self.errors.append(("hicolor-icon-cache-not-updated", ()))

# vim: set ts=4 sw=4 noet:
