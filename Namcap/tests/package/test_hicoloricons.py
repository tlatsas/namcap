# -*- coding: utf-8 -*-
#
# namcap tests - hicoloricons
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
import Namcap.depends
import Namcap.rules.hicoloricons

class HiColorIconsTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_hicoloricons
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=()
source=()
options=(!purge !zipman)
build() {
  true
}
package() {
  mkdir -p "${pkgdir}/usr/share/icons/hicolor/64x64"
}
"""
	def test_hicoloricons_file_exists(self):
		pkgfile = "__namcap_test_hicoloricons-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.hicoloricons.package
				)
		e, w, i = Namcap.depends.analyze_depends(pkg)
		self.assertEqual(pkg.detected_deps, {
			"hicolor-icon-theme": [('hicolor-icon-theme-needed-for-hicolor-dir',())]
			})
		self.assertEqual(set(r.errors + e), set([
			('dependency-detected-not-included %s (%s)',
			 ('hicolor-icon-theme', 'needed for hicolor theme hierarchy')
			),
			("hicolor-icon-cache-not-updated", ())
		]))
		self.assertEqual(r.warnings + w, [])
		self.assertEqual(r.infos + i, [
			('depends-by-namcap-sight depends=(%s)', 'hicolor-icon-theme')
			])

	valid_pkgbuild = """
pkgname=__namcap_test_hicoloricons
pkgver=1.0
pkgrel=1
pkgdesc="A package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('hicolor-icon-theme')
source=()
options=(!purge !zipman)
build() {
  true
}
package() {
  mkdir -p "${pkgdir}/usr/share/icons/hicolor/64x64"
}
"""

	def test_hicoloricons_normal(self):
		pkgfile = "__namcap_test_hicoloricons-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.valid_pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.hicoloricons.package
				)
		e, w, i = Namcap.depends.analyze_depends(pkg)
		self.assertEqual(pkg.detected_deps, {
			"hicolor-icon-theme": [('hicolor-icon-theme-needed-for-hicolor-dir',())]
			})
		self.assertEqual(r.errors + e, [
			("hicolor-icon-cache-not-updated", ())
			])
		self.assertEqual(r.warnings + w, [])
		self.assertEqual(r.infos + i, [
			('depends-by-namcap-sight depends=(%s)', 'hicolor-icon-theme')
			])


# vim: set ts=4 sw=4 noet:

