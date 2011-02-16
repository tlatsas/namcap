# -*- coding: utf-8 -*-
#
# namcap tests - permissions
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
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
#   USA
# 

import os
from Namcap.tests.makepkg import MakepkgTest
import Namcap.rules.permissions

class permissionsTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_permissions
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
source=()
build() {
  true
}
package() {
  mkdir -p ${pkgdir}/usr/bin
  touch ${pkgdir}/usr/bin/program
  chmod 777 ${pkgdir}/usr/bin/program
}
"""
	def test_nonrootowner(self):
		pkgfile = "__namcap_test_permissions-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.permissions.package
				)
		self.assertEqual(ret[0], [])
		self.assertEqual(ret[1], [("file-world-writable %s",
			"usr/bin/program")])
		self.assertEqual(ret[2], [])

# vim: set ts=4 sw=4 noet:

