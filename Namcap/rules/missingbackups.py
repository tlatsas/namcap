# 
# namcap rules - missingbackups
# Copyright (C) 2011 Dan McGee <dan@archlinux.org>
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
	name = "missingbackups"
	description = "Backup files listed in package should exist"
	def analyze(self, pkginfo, tar):
		if 'backup' not in pkginfo or len(pkginfo["backup"]) == 0:
			return
		known_backups = set(pkginfo["backup"])
		found_files = set(tar.getnames())
		missing_backups = known_backups - found_files
		for backup in missing_backups:
			self.errors.append(("missing-backup-file %s", backup))

# vim: set ts=4 sw=4 noet:
