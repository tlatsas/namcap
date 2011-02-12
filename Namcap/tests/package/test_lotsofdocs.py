# -*- coding: utf-8 -*-
#
# namcap tests - lotsofdocs
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
import Namcap.lotsofdocs

class LotsOfDocsTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_lotsofdocs
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
source=()
options=(!purge !zipman)
build() {
  true
}
package() {
  mkdir -p "${pkgdir}/usr/share/doc"
  dd if=/dev/zero of="${pkgdir}/usr/share/doc/somefile" bs=1k count=500
}
"""
	def test_lotsofdocs(self):
		pkgfile = "__namcap_test_lotsofdocs-1.0-1-i686.pkg.tar"
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.lotsofdocs.package
				)
		self.assertEqual(ret[0], [])
		tag, value = ret[1][0]
		self.assertEqual(tag, "lots-of-docs %f")
		self.assertGreater(value, 99.9)
		self.assertEqual(ret[2], [])

# vim: set ts=4 sw=4 noet:

