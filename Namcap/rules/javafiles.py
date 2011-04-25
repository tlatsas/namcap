# -*- coding: utf-8 -*-
#
# namcap rules - javafiles
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

import os
from Namcap.ruleclass import *

class JavaFiles(TarballRule):
	name = "javafiles"
	description = "Check for existence of Java classes or JARs"
	def analyze(self, pkginfo, tar):
		has_java_classes = False
		javas = []
		for entry in tar:
			# is it a regular file ?
			if not entry.isfile():
				continue
			# is it a JAR file ?
			if entry.name.endswith('.jar'):
				javas.append(entry.name)
				#self.infos.append( ('jar-file-found %s', entry.name) )
				continue
			# is it a CLASS file ?
			f = tar.extractfile(entry)
			if f.read(4) == b"\xCA\xFE\xBA\xBE":
				javas.append(entry.name)
				#self.infos.append( ('java-class-file-found %s', entry.name) )
			f.close()
		if len(javas) > 0:
			reasons = pkginfo.detected_deps.setdefault('java-environment', [])
			reasons.append( ('java-environment-needed %s', ', '.join(javas)) )

# vim: set ts=4 sw=4 noet:
