# -*- coding: utf-8 -*-
#
# namcap tests - carch
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

import unittest
from Namcap.tests.pkgbuild_test import PkgbuildTest
import Namcap.rules.carch as module

class NamcapSpecialArchTest(PkgbuildTest):
	pkgbuild1 = """
pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  [[ $CARCH == x86_64 ]] && CFLAGS+="-m64"
  [ '$CARCH' = 'i686' ] && CFLAGS+="-m32"
  ./configure --prefix=/usr
  make
}
"""

	pkgbuild2 = """
pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  [[ $CARCH == x86_64 ]] && CFLAGS+="-m64"
  [ '$CARCH' = 'i686' ] && CFLAGS+="-m32"
  ./configure --prefix=/usr
  make
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install
  cp foobar /usr/lib/i686/pkg/
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = module.package

	def test_example1(self):
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

	def test_example2(self):
		r = self.run_on_pkg(self.pkgbuild2)
		self.assertEqual(r.errors, [])
		self.assertEqual(r.warnings, [("specific-host-type-used %s", "i686")])
		self.assertEqual(r.infos, [])


# vim: set ts=4 sw=4 noet:
