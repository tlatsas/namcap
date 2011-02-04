# -*- coding: utf-8 -*-
#
# namcap tests - non ascii filenames
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
import Namcap.directoryname

class FHSTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_nonfhs
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
  mkdir -p ${pkgdir}/weird/directory
  touch ${pkgdir}/weird/directory/file
}
"""
	def test_nonfhs(self):
		pkgfile = "__namcap_test_nonfhs-1.0-1-i686.pkg.tar"
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.directoryname.package
				)
		self.assertEqual(ret[0], [])
		self.assertEqual(set(ret[1]), set([
			("file-in-non-standard-dir %s", "weird"),
			("file-in-non-standard-dir %s", "weird/directory"),
			("file-in-non-standard-dir %s", "weird/directory/file")
			]))
		self.assertEqual(ret[2], [])

	pkgbuild_man = """
pkgname=__namcap_test_nonfhs
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
  mkdir -p ${pkgdir}/usr/man
  touch ${pkgdir}/usr/man/something.1
}
"""
	def test_nonfhsman(self):
		pkgfile = "__namcap_test_nonfhs-1.0-1-i686.pkg.tar"
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_man)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.fhsmanpages.package
				)
		self.assertEqual(ret[0],
				[("non-fhs-man-page %s", "usr/man/something.1.gz")])
		self.assertEqual(ret[1], [])
		self.assertEqual(ret[2], [])

	pkgbuild_info = """
pkgname=__namcap_test_nonfhs
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
  mkdir -p ${pkgdir}/usr/info
  touch ${pkgdir}/usr/info/something
}
"""
	def test_nonfhsinfo(self):
		pkgfile = "__namcap_test_nonfhs-1.0-1-i686.pkg.tar"
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_info)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.fhsinfopages.package
				)
		self.assertEqual(ret[0],
				[("non-fhs-info-page %s", "usr/info/something.gz")])
		self.assertEqual(ret[1], [])
		self.assertEqual(ret[2], [])



# vim: set ts=4 sw=4 noet:

