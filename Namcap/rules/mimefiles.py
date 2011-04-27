# 
# namcap rules - mimefiles
# Copyright (C) 2009 Hugo Doria <hugo@archlinux.org>
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
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
# 

from Namcap.ruleclass import *

class MimeInfoRule(TarballRule):
	name = "mimefiles"
	description = "Check for files in /usr/share/mime"
	def analyze(self, pkginfo, tar):
		if 'usr/share/mime' in tar.getnames():
			reasons = pkginfo.detected_deps.setdefault("shared-mime-info", [])
			reasons.append( ('shared-mime-info-needed',()) )
			if ".INSTALL" not in tar.getnames():
				self.errors.append(("mime-cache-not-updated", ()))
			else:
				f = tar.extractfile(".INSTALL")
				if b"update-mime-database" not in f.read():
					self.errors.append(("mime-cache-not-updated", ()))

class MimeDesktopRule(TarballRule):
	name = "mimedesktop"
	description = "Check that MIME associations are updated"
	def analyze(self, pkginfo, tar):
		desktop_db_updated = False
		has_mime_desktop = False
		for entry in tar:
			if entry.issym():
				continue
			if (entry.name.startswith("usr/share/applications")
					and entry.name.endswith(".desktop")):
				f = tar.extractfile(entry)
				for l in f:
					if l.startswith(b"MimeType="):
						has_mime_desktop = True
						break
				f.close()
			if entry.name == ".INSTALL":
				f = tar.extractfile(entry)
				if b"update-desktop-database" in f.read():
					desktop_db_updated = True
				f.close()

		if has_mime_desktop:
			reasons = pkginfo.detected_deps.setdefault("desktop-file-utils", [])
			reasons.append( ('desktop-file-utils-needed',()) )
			if not desktop_db_updated:
				self.errors.append(("desktop-database-not-updated", ()))

# vim: set ts=4 sw=4 noet:
