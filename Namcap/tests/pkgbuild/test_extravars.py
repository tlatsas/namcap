# -*- coding: utf-8 -*-
#
# namcap tests - extravars
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
from Namcap.tests.pkgbuild_test import PkgbuildTest
import Namcap.rules.extravars

class ExtravarsTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license='GPL'
depends=('glibc')
depends+=('glib2')
optdepends=('gtk2')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

mycustomvar="something"
_legalvar="something else"

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr \\
	--libdir=something
  make
  hello=world make something
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  make DESTDIR="${pkgdir}" install
}
"""
	# now a more tricky example
	pkgbuild2 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A pac
kage=1 package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
depends+=('glib2'
glibc=2.12
)
optdepends=('gtk2')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr \\
	--libdir=something
  _variable=value make; mycustomvar="something"
  hello=world make something
  echo 's/a/b/
        b=c
        s/c=d/'
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  make DESTDIR="${pkgdir}" install
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = Namcap.rules.extravars.package

	def test_example1(self):
		"PKGBUILD with custom variables without underscore"
		os.putenv("environment_pollution", "yes")
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [])
		self.assertEqual(set(r.warnings), set([
			("extra-var-begins-without-underscore %s", "mycustomvar"),
		]))
		self.assertEqual(r.infos, [])

	def test_example2(self):
		"a tricky PKGBUILD with custom variables without underscore"
		r = self.run_on_pkg(self.pkgbuild2)
		self.assertEqual(r.errors, [])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])


# vim: set ts=4 sw=4 noet:
