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

__tarball__ = """
  anyelf
  capsnamespkg
  depends
  directoryname
  elffiles
  emptydir
  fhsmanpages
  fhsinfopages
  filenames
  fileownership
  gnomemime
  hardlinks
  hicoloricons
  infodirectory
  kdeprograms
  libtool
  licensepkg
  lotsofdocs
  mimefiles
  missingbackups
  perllocal
  permissions
  rpath
  scrollkeeper
  symlink
  urlpkg

""".split()

__pkgbuild__ = """
  arrays
  badbackups
  carch
  checksums
  invalidstartdir
  license
  pkgname
  pkgnameindesc
  sfurl
  tags
  url

""".split()

tarball_rules = {}
for __rulename__ in __tarball__:
	tarball_rules[__rulename__] = \
		__import__("Namcap." + __rulename__, fromlist = "Namcap").package

pkgbuild_rules = {}
for __rulename__ in __pkgbuild__:
	pkgbuild_rules[__rulename__] = \
		__import__("Namcap." + __rulename__, fromlist = "Namcap").package

all_rules = {}
all_rules.update(tarball_rules)
all_rules.update(pkgbuild_rules)

# vim: set ts=4 sw=4 noet:
