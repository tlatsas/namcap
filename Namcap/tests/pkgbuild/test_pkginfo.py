# -*- coding: utf-8 -*-
#
# namcap tests - pkginfo
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
from Namcap.rules.pkginfo import *

class NamcapInvalidPkgNameTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=MyPackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = CapsPkgnameRule

	def test_example1(self):
		# Example 1
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [("package-name-in-uppercase", ())])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

class NamcapLicenseTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
depends=('glibc')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install
}
"""
	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = LicenseRule

	def test_example1(self):
		# Example 1
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [("missing-license", ())] )
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

class NamcapUrlTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
depends=('glibc')
license=('GPL')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = UrlRule

	def test_example1(self):
		# Example 1
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [("missing-url", ())] )
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

# vim: set ts=4 sw=4 noet:
