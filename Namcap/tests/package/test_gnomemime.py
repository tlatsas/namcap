# -*- coding: utf-8 -*-
#
# namcap tests - gnomemime
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
import Namcap.rules.gnomemime

class GnomeMimeTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_gnomemime
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
  true
}
package() {
  mkdir -p "${pkgdir}/usr/share/applications"
  touch "${pkgdir}/usr/share/applications/mimeinfo.cache"
}
"""
	def test_gnomemime_file_exists(self):
		pkgfile = "__namcap_test_gnomemime-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.gnomemime.package
				)
		self.assertEqual(r.errors, [
			("gnome-mime-file %s", "usr/share/applications/mimeinfo.cache")
		])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

# vim: set ts=4 sw=4 noet:

