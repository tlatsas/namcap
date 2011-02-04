import os
import unittest
import tempfile
import shutil

import pacman
import valid_pkgbuilds

import Namcap.tags as module

EMPTY_RESULT = [ [] , [] , [] ]

class NamcapMaintainerTagTest(unittest.TestCase):
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
	def run_on_pkg(self, p):
		with open(self.tmpname, 'w') as f:
			f.write(p)
		pkginfo = pacman.load(self.tmpname)
		return self.rule.analyze(pkginfo, self.tmpname)

	def runTest(self):
		self.rule = module.package()
		self.tmpdir = tempfile.mkdtemp()
		self.tmpname = os.path.join(self.tmpdir, "PKGBUILD")

		# Valid PKGBUILDS
		for p in valid_pkgbuilds.all_pkgbuilds:
			ret = self.run_on_pkg(p)
			self.assertEqual(ret, EMPTY_RESULT)

		# Example 1
		ret = self.run_on_pkg(self.pkgbuild1)
		self.assertEqual(ret[0], [])
		self.assertEqual(ret[1], [("missing-maintainer", ())])
		self.assertEqual(ret[2], [("missing-contributor", ())] )

		shutil.rmtree(self.tmpdir)

# vim: set ts=4 sw=4 noet:
