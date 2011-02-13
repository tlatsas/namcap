# -*- coding: utf-8 -*-
#
# namcap tests - arrays
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

import pacman
import valid_pkgbuilds

import Namcap.extravars

EMPTY_RESULT = [ [] , [] , [] ]

class ExtravarsTest(unittest.TestCase):
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
	def setUp(self):
		self.rule = Namcap.extravars.package()
		self.tmpdir = tempfile.mkdtemp()
		self.tmpname = os.path.join(self.tmpdir, "PKGBUILD")

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def run_on_pkg(self, p):
		with open(self.tmpname, 'w') as f:
			f.write(p)
		pkginfo = pacman.load(self.tmpname)
		return self.rule.analyze(pkginfo, self.tmpname)

	def test_valid(self):
		# Valid PKGBUILDS
		for p in valid_pkgbuilds.all_pkgbuilds:
			ret = self.run_on_pkg(p)
			self.assertEqual(ret, EMPTY_RESULT)

	def test_example1(self):
		# Example 1
		ret = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(ret[0], [])
		self.assertEqual(set(ret[1]), set([
			("extra-var-begins-without-underscore %s", "mycustomvar"),
			("extra-var-begins-without-underscore %s", "hello")
		]))
		self.assertEqual(ret[2], [])


# vim: set ts=4 sw=4 noet:
