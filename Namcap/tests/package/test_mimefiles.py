# -*- coding: utf-8 -*-
#
# namcap tests - mimefiles
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
import Namcap.rules.mimefiles

class MimeFilesTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_mimefiles
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
  mkdir -p "${pkgdir}/usr/share/mime/applications"

  mkdir -p "${pkgdir}/usr/share/applications"
  echo "MimeType=applcation/pdf" > "${pkgdir}/usr/share/applications/foobar.desktop"
}
"""
	def test_mimefiles_file_exists(self):
		"Packge with mimefiles but cache is not updated"
		pkgfile = "__namcap_test_mimefiles-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.mimefiles.MimeInfoRule
				)
		self.assertEqual(pkg.detected_deps,
				{"shared-mime-info": [('shared-mime-info-needed', ())] }
				)
		self.assertEqual(r.errors, [("mime-cache-not-updated", ())])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

	def test_mimetype_in_desktop(self):
		"Package with desktop files and MIME associations not updated"
		pkgfile = "__namcap_test_mimefiles-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.mimefiles.MimeDesktopRule
				)
		self.assertEqual(pkg.detected_deps,
				{"desktop-file-utils": [('desktop-file-utils-needed', ())] }
				)
		self.assertEqual(r.errors, [("desktop-database-not-updated", ())])
		self.assertEqual(r.warnings, [])
		self.assertEqual(r.infos, [])

# vim: set ts=4 sw=4 noet:

