# 
# namcap rules - __init__
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
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

from types import ModuleType
import Namcap.ruleclass

# Tarball rules
from . import (
  anyelf,
  depends,
  directoryname,
  elffiles,
  emptydir,
  fhsmanpages,
  fhsinfopages,
  filenames,
  fileownership,
  gnomemime,
  hardlinks,
  hicoloricons,
  infodirectory,
  kdeprograms,
  libtool,
  licensepkg,
  lotsofdocs,
  mimefiles,
  missingbackups,
  perllocal,
  permissions,
  rpath,
  scrollkeeper,
  symlink
)

# Package rules
from . import (
  arrays,
  badbackups,
  carch,
  invalidstartdir,
  missingvars,
  pkginfo,
  pkgnameindesc,
  sfurl
)

all_rules = {}
for name,value in dict(locals()).iteritems():
	if not isinstance(value, ModuleType):
		continue
	if name == "Namcap.ruleclass":
		continue
	for n, v in value.__dict__.iteritems():
		if (type(v) == type
			and issubclass(v, Namcap.ruleclass.AbstractRule)
			and hasattr(v, "name")):
			all_rules[v.name] = v

# vim: set ts=4 sw=4 noet:
