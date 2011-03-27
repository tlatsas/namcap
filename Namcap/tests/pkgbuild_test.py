# -*- coding: utf-8 -*-
#
# namcap tests - pkgbuild rule testing template
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
import unittest
import tempfile
import shutil

import Namcap.package
import Namcap.ruleclass

class PkgbuildTest(unittest.TestCase):
	"""
	This class is the template for unit tests concerning PKGBUILD rules.
	The setUp()	method should set self.rule to a class derived from
	PkgbuildRule.

	The usual way to do that is by defining

	def preSetUp(self):
		self.rule = myRuleClass
		# Add standard valid PKGBUILDs to tests
		self.test_valid = PkgbuildTest.valid_tests
	"""

	def preSetUp(self):
		pass

	def setUp(self):
		self.preSetUp()
		self.tmpdir = tempfile.mkdtemp()
		self.tmpname = os.path.join(self.tmpdir, "PKGBUILD")

	def run_on_pkg(self, p):
		with open(self.tmpname, 'w', encoding = 'utf-8') as f:
			f.write(p)
		pkginfo = Namcap.package.load_from_pkgbuild(self.tmpname)
		r = self.rule()
		if isinstance(r, Namcap.ruleclass.PkgInfoRule):
			if pkginfo.is_split:
				for p in pkginfo.subpackages:
					r.analyze(p, self.tmpname)
			else:
				r.analyze(pkginfo, self.tmpname)
		if isinstance(r, Namcap.ruleclass.PkgbuildRule):
			r.analyze(pkginfo, self.tmpname)
		return r

	def valid_tests(self):
		"Valid PKGBUILDS"
		for p in valid_pkgbuilds:
			r = self.run_on_pkg(p)
			self.assertEqual(r.errors, [])
			self.assertEqual(r.warnings, [])
			self.assertEqual(r.errors, [])

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

_basic = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
epoch=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc' 'pacman')
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
  make DESTDIR="${pkgdir}" install
}
"""

_split = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgbase=mysplitpackage
pkgname=('mypackage1' 'mypackage2' 'mypackage3')
pkgver=1.0
pkgrel=1
epoch=2
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
makedepends=('make' 'gtk2')
checkdepends=('perl')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgbase}-${pkgver}
  ./configure --prefix=/usr
  make
}

check() {
  cd "${srcdir}"/${pkgbase}-${pkgver}
  make check
}

package_mypackage1() {
  pkgdesc="Package 1"
  depends=("gtk2")
  cd "${srcdir}"/${pkgbase}-${pkgver}
  make DESTDIR="${pkgdir}" install1
}

package_mypackage2() {
  pkgdesc="Package 2"
  depends=("glib2" "mypackage1")
  cd "${srcdir}"/${pkgbase}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install2
}

package_mypackage3() {
  pkgdesc="Package 3"
  depends=("glib2")
  optdepends=("mypackage1: for foobar functionality")
  install=somescript.install
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install3
}
"""

valid_pkgbuilds = [_basic, _split]

# vim: set ts=4 sw=4 noet:
