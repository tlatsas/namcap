# -*- coding: utf-8 -*-
#
# namcap - Class hierarchy for rules
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
# 

"""
This module defines the base classes from which Namcap rules are derived
and how they are meant to be used.
"""

# python 3 does not need classes to derive from object
class AbstractRule(object):
	"The parent class of all rules"
	def __init__(self):
		self.errors = []
		self.warnings = []
		self.infos = []

class PkgInfoRule(AbstractRule):
	"The parent class of rules that process package metadata"
	pass

class PkgbuildRule(AbstractRule):
	"The parent class of rules that process PKGBUILDs"
	pass

class TarballRule(AbstractRule):
	"The parent class of rules that process tarballs"
	pass

# vim: set ts=4 sw=4 noet:
