# -*- coding: utf-8 -*-
#
# namcap tests - invalidstartdir
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
import Namcap.rules.invalidstartdir as module

class NamcapInvalidStartdirTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="This program does foobar"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "$startdir/src/${pkgname}-${pkgver}"
  patch -p1 ${startdir}/patch
  ./configure --prefix=/usr
  make
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="$startdir/pkg" install
}
"""

	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = module.package

	def test_example1(self):
		# Example 1
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(set(r.errors), set([
			("file-referred-in-startdir", ()),
			("use-pkgdir", ()),
			("use-srcdir", ())
		]))
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

# vim: set ts=4 sw=4 noet:

