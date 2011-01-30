import os
import unittest
import tempfile
import shutil

import pacman

pkgbuild = """
# Maintainer: Arch Linux <archlinux@example.com>
# Contributor: Arch Linux <archlinux@example.com>

pkgname=mypackage
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc' 'foobar')
optdepends=('libabc: provides the abc feature')
provides=('yourpackage>=0.9')
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

class PkgbuildLoaderTests(unittest.TestCase):
	def runTest(self):
		tmpdir = tempfile.mkdtemp()
		tmpname = os.path.join(tmpdir, "PKGBUILD")
		with open(tmpname, 'w') as f:
			f.write(pkgbuild)
		pkginfo = pacman.load(tmpname)

		self.assertEqual(pkginfo.name, "mypackage")
		self.assertEqual(pkginfo.version, "1.0-1")
		self.assertEqual(pkginfo.desc, "A package")
		self.assertEqual(pkginfo.url, "http://www.example.com/")

		self.assertEqual(pkginfo.depends, ["glibc", "foobar"])
		self.assertEqual(pkginfo.optdepends, ["libabc"])
		self.assertEqual(pkginfo.provides, ["yourpackage"])

		shutil.rmtree(tmpdir)

# vim: set ts=4 sw=4 noet:
