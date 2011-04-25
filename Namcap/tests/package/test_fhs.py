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
from Namcap.rules import fhs

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
  mkdir -p ${pkgdir}/run
  touch ${pkgdir}/run/program.pid
}
"""
	def test_nonfhs(self):
		"Package with files in /weird"
		pkgfile = "__namcap_test_nonfhs-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				fhs.FHSRule
				)
		self.assertEqual(set(r.errors), set([
			("file-in-temporary-dir %s", 'run/program.pid')
			]))
		self.assertEqual(set(r.warnings), set([
			("file-in-non-standard-dir %s", "weird/"),
			("file-in-non-standard-dir %s", "weird/directory/"),
			("file-in-non-standard-dir %s", "weird/directory/file")
			]))
		self.assertEqual(r.infos, [])

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
		"Package with man pages in /usr/man"
		pkgfile = "__namcap_test_nonfhs-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_man)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				fhs.FHSManpagesRule
				)
		self.assertEqual(r.errors,
				[("non-fhs-man-page %s", "usr/man/something.1.gz")])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

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
		"Package with info pages in /usr/info"
		pkgfile = "__namcap_test_nonfhs-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild_info)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				fhs.FHSInfoPagesRule
				)
		self.assertEqual(r.errors,
				[("non-fhs-info-page %s", "usr/info/something.gz")])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])



# vim: set ts=4 sw=4 noet:

