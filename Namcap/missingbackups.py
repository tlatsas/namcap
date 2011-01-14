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

class package:
	def short_name(self):
		return "missingbackups"
	def long_name(self):
		return "Backup files listed in package should exist"
	def prereq(self):
		return "tar"
	def analyze(self, pkginfo, tar):
		ret = [[], [], []]
		if not hasattr(pkginfo, 'backup') or len(pkginfo.backup) == 0:
			return ret
		known_backups = set(pkginfo.backup)
		found_backups = [x for x in tar.getnames() if x in known_backups]
		missing_backups = known_backups - set(found_backups)
		for backup in missing_backups:
			ret[0].append(("missing-backup-file %s", backup))
		return ret
	def type(self):
		return "tarball"
# vim: set ts=4 sw=4 noet:
