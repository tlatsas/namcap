# -*- coding: utf-8 -*-
#
# namcap tests - anyelf rule
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
import Namcap.rules.anyelf

class AnyElfTest(MakepkgTest):
	pkgbuild_any = """
pkgname=__namcap_test_anyelf
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=(emptydirs)
source=()
build() {
  true
}
package() {
  mkdir -p ${pkgdir}/usr/share/directory
  touch ${pkgdir}/usr/share/directory_file
}
"""
	pkgbuild_elf = """
pkgname=__namcap_test_anyelf
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('any')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=(emptydirs)
source=()
build() {
  true
}
package() {
  install -m755 -D /bin/ls ${pkgdir}/usr/bin/ls
}
"""
	def test_not_any_no_elf(self):
		pkgfile = "__namcap_test_anyelf-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_any)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.anyelf.package
				)
		self.assertEqual(ret[0], [])
		self.assertEqual(ret[1], [('no-elffiles-not-any-package', ())])
		self.assertEqual(ret[2], [])

	def test_any_but_elf(self):
		pkgfile = "__namcap_test_anyelf-1.0-1-any.pkg.tar"
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_elf)
		self.run_makepkg()
		ret = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.anyelf.package
				)
		self.assertEqual(ret[0], 
				[("elffile-in-any-package %s", "usr/bin/ls")])
		self.assertEqual(ret[1], [])
		self.assertEqual(ret[2], [])


# vim: set ts=4 sw=4 noet:

