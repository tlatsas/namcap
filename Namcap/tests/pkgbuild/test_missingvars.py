# -*- coding: utf-8 -*-
#
# namcap tests - missingvars
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
from Namcap.rules.missingvars import *

class NamcapChecksumTest(PkgbuildTest):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('look-this-is-an-invalid-checksum')

build() {
  true
}

package() {
  true
}
"""
	pkgbuild2 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz
		nice-patch.diff)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  true
}

package() {
  true
}
"""

	# packages with no sources (FS#23258)
	pkgbuild_no_sources = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc' 'pacman')
options=('!libtool')
md5sums=('1234567890abcdef1234567890abcdef')

build() {
wget http://www.example.com/sources.tar.gz
cd "${srcdir}"/${pkgname}-${pkgver}
./configure --prefix=/usr
make
}

package() {
cd "${srcdir}"/${pkgname}-${pkgver}
make DESTDIR="${pkgdir}" install
}
"""


	test_valid = PkgbuildTest.valid_tests

	def preSetUp(self):
		self.rule = ChecksumsRule

	def test_example1(self):
		# Example 1
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [
			("improper-checksum %s %s", ("md5sums",
			 "look-this-is-an-invalid-checksum"))
		])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

	def test_example2(self):
		# Example 2
		r = self.run_on_pkg(self.pkgbuild2)
		self.assertEqual(r.errors, [
			("not-enough-checksums %s %i needed", ("md5sums", 2))
		])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

	def test_example_no_sources(self):
		# Example with no sources (FS #23259)
		r = self.run_on_pkg(self.pkgbuild_no_sources)
		self.assertEqual(r.errors, [
			("too-many-checksums %s %i needed", ("md5sums", 0))
		])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])


class NamcapMaintainerTagTest(PkgbuildTest):
	pkgbuild1 = """
pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="The foobar program"
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
		self.rule = TagsRule

	def test_example1(self):
		# Example 1
		r = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(r.errors, [])
		self.assertEqual(r.warnings, [("missing-maintainer", ())])
		self.assertEqual(r.infos, [("missing-contributor", ())] )

# vim: set ts=4 sw=4 noet:
