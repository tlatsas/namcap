import os
import unittest
import tempfile
import shutil

import pacman
import valid_pkgbuilds

import Namcap.rules.checksums as module

EMPTY_RESULT = [ [] , [] , [] ]

class NamcapChecksumTest(unittest.TestCase):
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
		self.assertEqual(ret[0], [
			("improper-checksum %s %s", ("md5sums",
			 "look-this-is-an-invalid-checksum"))
		])
		self.assertEqual(ret[1], [])
		self.assertEqual(ret[2], [])

		# Example 2
		ret = self.run_on_pkg(self.pkgbuild2)
		self.assertEqual(ret[0], [
			("not-enough-checksums %s %i needed", ("md5sums", 2))
		])
		self.assertEqual(ret[1], [])
		self.assertEqual(ret[2], [])

		shutil.rmtree(self.tmpdir)

# vim: set ts=4 sw=4 noet:
