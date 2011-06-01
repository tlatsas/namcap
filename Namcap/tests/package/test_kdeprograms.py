# -*- coding: utf-8 -*-
#
# namcap tests - kdeprograms
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
import Namcap.rules.kdeprograms

class KdeProgramsTest(MakepkgTest):
	pkgbuild = """
pkgname=__namcap_test_kdeprograms
pkgver=1.0
pkgrel=1
pkgdesc="A KDE package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('kdelibs')
source=()
options=(!purge !zipman)
backup=(etc/imaginary_file.conf)
build() {
  true
}
package() {
  mkdir -p "${pkgdir}/usr/bin"
  touch "${pkgdir}/usr/bin/kfoobar"
}
"""

	pkgbuild2 = """
pkgname=__namcap_test_kdeprograms
pkgver=1.0
pkgrel=1
pkgdesc="A KDE package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('kdegraphics-libs')
source=()
options=(!purge !zipman)
backup=(etc/imaginary_file.conf)
build() {
  true
}
package() {
  mkdir -p "${pkgdir}/usr/bin"
  touch "${pkgdir}/usr/bin/kfoobar"
}
"""

	pkgbuild3 = """
pkgname=__namcap_test_kdeprograms
pkgver=1.0
pkgrel=1
pkgdesc="A KDE package"
arch=('i686' 'x86_64')
url="http://www.example.com/"
license=('GPL')
depends=('kdegraphics-libs' 'kdebase-runtime')
source=()
options=(!purge !zipman)
backup=(etc/imaginary_file.conf)
build() {
  true
}
package() {
  mkdir -p "${pkgdir}/usr/bin"
  touch "${pkgdir}/usr/bin/kfoobar"
}
"""

	def test_kdeprograms_files_a(self):
		pkgfile = "__namcap_test_kdeprograms-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.kdeprograms.package
				)
		e, w, i = Namcap.depends.analyze_depends(pkg)
		self.assertEqual(e + r.errors,
				[('dependency-detected-not-included %s (%s)',
				  ('kdebase-runtime', "needed for programs ['usr/bin/kfoobar']")
				 )])
		self.assertEqual(r.warnings, [])
		self.assertTrue(
			("kdebase-runtime-needed-dep %s", ["usr/bin/kfoobar"])
			in r.infos)

	def test_kdeprograms_files_b(self):
		pkgfile = "__namcap_test_kdeprograms-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild2)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.kdeprograms.package
				)
		e, w, i = Namcap.depends.analyze_depends(pkg)
		self.assertEqual(e + r.errors,
				[('dependency-detected-not-included %s (%s)',
				  ('kdebase-runtime', "needed for programs ['usr/bin/kfoobar']")
				 )])
		self.assertEqual(w + r.warnings,
				[('dependency-not-needed %s', 'kdegraphics-libs')])
		self.assertTrue(
			("kdebase-runtime-needed-dep %s", ["usr/bin/kfoobar"])
			in r.infos)

	def test_kdeprograms_files_c(self):
		pkgfile = "__namcap_test_kdeprograms-1.0-1-%(arch)s.pkg.tar" % { "arch": self.arch }
		with open(os.path.join(self.tmpdir, "PKGBUILD"), "w") as f:
			f.write(self.pkgbuild3)
		self.run_makepkg()
		pkg, r = self.run_rule_on_tarball(
				os.path.join(self.tmpdir, pkgfile),
				Namcap.rules.kdeprograms.package
				)
		e, w, i = Namcap.depends.analyze_depends(pkg)
		self.assertEqual(e + r.errors, [])
		self.assertEqual(r.warnings, [])
		self.assertTrue(
			("kdebase-runtime-needed-dep %s", ["usr/bin/kfoobar"])
			in r.infos)


# vim: set ts=4 sw=4 noet:
