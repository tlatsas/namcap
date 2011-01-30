import os
import unittest
import tempfile
import shutil

import pacman
import valid_pkgbuilds

import Namcap.carch as module

EMPTY_RESULT = [ [] , [] , [] ]

class NamcapSpecialArchTest(unittest.TestCase):
	pkgbuild1 = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
options=('!libtool')
source=(ftp://ftp.example.com/pub/mypackage-0.1.tar.gz)
md5sums=('abcdefabcdef12345678901234567890')

build() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  [[ $CARCH == x86_64 ]] && CFLAGS+="-m32"
  ./configure --prefix=/usr
  make
}

package() {
  cd "${srcdir}"/${pkgname}-${pkgver}
  ./configure --prefix=/usr
  make DESTDIR="${pkgdir}" install
}
"""
	def setUp(self):
		self.rule = module.package()
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
		self.assertEqual(ret[1], ("specific-host-type-used %s", "i686"))
		self.assertEqual(ret[2], [])

# vim: set ts=4 sw=4 noet:
