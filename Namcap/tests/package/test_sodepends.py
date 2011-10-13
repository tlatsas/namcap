# -*- coding: utf-8 -*-
#
# namcap tests - sodepends
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
from Namcap.tests.makepkg import MakepkgTest
import Namcap.rules.sodepends

class SoDependsTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_sodepends
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
source=()
options=(!purge !zipman)
build() {
  cd "${srcdir}"
  echo "int main() { return 0; }" > main.c
  gcc -o main main.c -Wl,--no-as-needed -lalpm
}
package() {
  install -D -m 755 "$srcdir/main" "$pkgdir/usr/bin/main"
}
"""
	def test_sodepends(self):
		"Package with missing pacman dependency"
		pkgfile = "__namcap_test_sodepends-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.sodepends.SharedLibsRule
				)
		self.assertEqual(pkg.detected_deps['pacman'], [
			('libraries-needed %s %s',
			 (str(['usr/lib/libalpm.so.7']), str(["usr/bin/main"]))
			)]
		)
		e, w, i = Namcap.depends.analyze_depends(pkg)
		self.assertEqual(e, [
			('dependency-detected-not-included %s (%s)',
				('pacman', "libraries ['usr/lib/libalpm.so.7'] needed in files ['usr/bin/main']"))
		])
		self.assertEqual(w, [])

# vim: set ts=4 sw=4 noet:

