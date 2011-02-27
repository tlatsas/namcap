# -*- coding: utf-8 -*-
#
# namcap tests - sfurl
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

from Namcap.tests.pkgbuild_test import PkgbuildTest
import Namcap.rules.splitpkgbuild as module

class NamcapSplitPkgbuildTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgbase=mypackage
pkgname=('prog1' 'prog2')
pkgver=1.0
pkgrel=1
pkgdesc="A package"
url="http://mypackage.sf.net/"
arch=('i686' 'x86_64')
depends=('glibc')
license=('GPL')
options=('!libtool')
source=(ftp://heanet.dl.sourceforge.net/pub/m/mypackage/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make
}

package_prog1() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install1
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = module.PackageFunctionsRule

	def test_example1(self):
		"Example 1 : missing package_* function"
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [("missing-pkgfunction %s", "prog2")])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

class NamcapSplitMakedepsTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgbase=mypackage
pkgname=('prog1' 'prog2')
pkgver=1.0
pkgrel=1
pkgdesc="A package"
url="http://mypackage.sf.net/"
arch=('i686' 'x86_64')
makedepends=('gtk2')
license=('GPL')
options=('!libtool')
source=(ftp://heanet.dl.sourceforge.net/pub/m/mypackage/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make
}

package_prog1() {
  depends=("gtk2")
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install1
}

package_prog2() {
  depends=("qt" "glibc")
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install1
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = module.SplitPkgMakedepsRule

	def test_example1(self):
		"Example 1 : missing makedepend"
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [("missing-makedeps %s",
			str(["qt"]))])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])


# vim: set ts=4 sw=4 noet:
