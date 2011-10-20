# -*- coding: utf-8 -*-
#
# namcap tests - permissions
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
import Namcap.rules.permissions

class PermissionsTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_permissions
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('glibc')
source=()
build() {
  true
}
package() {
  install -d -m 755 ${pkgdir}/usr/bin

  touch ${pkgdir}/usr/bin/program
  chmod 777 ${pkgdir}/usr/bin/program

  touch ${pkgdir}/usr/bin/secret
  chmod 700 ${pkgdir}/usr/bin/secret

  touch ${pkgdir}/usr/bin/unsafe
  chmod u+rwxs ${pkgdir}/usr/bin/unsafe

  install -d -m 744 ${pkgdir}/usr/share/broken

  install -d -m 755 ${pkgdir}/usr/lib/libstatic.a
  ln -s libstatic.a ${pkgdir}/usr/lib/libstaticlink.a
}
"""
	def test_nonrootowner(self):
		pkgfile = "__namcap_test_permissions-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.permissions.package
				)
		self.assertEqual(r.errors, [])
		self.assertEqual(set(r.warnings), set([
			("file-world-writable %s", "usr/bin/program"),
			("file-not-world-readable %s", "usr/bin/secret"),
			("file-setugid %s", "usr/bin/unsafe"),
			("directory-not-world-executable %s", "usr/share/broken"),
			("incorrect-library-permissions %s", "usr/lib/libstatic.a")
			]))
		self.assertEqual(r.infos, [])

# vim: set ts=4 sw=4 noet:

