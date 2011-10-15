# -*- coding: utf-8 -*-
# 
# namcap rules - glibfiles
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

import os
from Namcap.ruleclass import *

class GlibSchemasRule(TarballRule):
	name = "glibschemas"
	description = "Check that dconf schemas are compiled"
	def analyze(self, pkginfo, tar):
		flag = False
		ok = False
		for entry in tar:
			if ('usr/share/glib-2.0/schemas' in entry.name
					and os.path.basename(entry.name).endswith(".gschema.xml")
					and not flag):
				flag = True
				reasons = pkginfo.detected_deps.setdefault("dconf", [])
				reasons.append( ('dconf-needed-for-glib-schemas',()) )
			if ".INSTALL" in entry.name:
				f = tar.extractfile(".INSTALL")
				if b"glib-compile-schemas" in f.read():
					ok = True
				f.close()
		if flag and not ok:
			self.warnings.append(("dconf-schemas-not-compiled", ()))

class GioModulesRule(TarballRule):
	name = "giomodules"
	description = "Check that GIO modules are registered"
	def analyze(self, pkginfo, tar):
		flag = False
		ok = False
		for entry in tar:
			if ('usr/lib/gio/modules' in entry.name
					and os.path.basename(entry.name) not in ('', 'modules')
					and not flag):
				flag = True
				reasons = pkginfo.detected_deps.setdefault("glib2", [])
				reasons.append( ('glib2-needed-for-gio-modules',()) )
			if ".INSTALL" in entry.name:
				f = tar.extractfile(".INSTALL")
				if b"gio-querymodules" in f.read():
					ok = True
				f.close()
		if flag and not ok:
			self.warnings.append(("gio-modules-not-registered", ()))

# vim: set ts=4 sw=4 noet:
