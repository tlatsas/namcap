# -*- coding: utf-8 -*-
#
# namcap tests - makepkg launcher
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
import tempfile
import subprocess
import unittest
import shutil
import tarfile

from ..package import PacmanPackage

makepkg_conf = """
DLAGENTS=('ftp::/usr/bin/wget -c --passive-ftp -t 3 --waitretry=3 -O %%o %%u'
		  'http::/usr/bin/wget -c -t 3 --waitretry=3 -O %%o %%u'
		  'https::/usr/bin/wget -c -t 3 --waitretry=3 --no-check-certificate -O %%o %%u'
		  'rsync::/usr/bin/rsync -z %%u %%o'
		  'scp::/usr/bin/scp -C %%u %%o')
CARCH="%(arch)s"
CHOST="%(arch)s-pc-linux-gnu"
CFLAGS="-march=%(arch)s -mtune=generic -O2 -pipe"
CXXFLAGS="-march=%(arch)s -mtune=generic -O2 -pipe"
LDFLAGS="-Wl,--hash-style=gnu -Wl,--as-needed"
BUILDENV=(fakeroot !distcc color !ccache)
OPTIONS=(strip docs libtool emptydirs zipman purge)
INTEGRITY_CHECK=(md5)
STRIP_BINARIES="--strip-all"
STRIP_SHARED="--strip-unneeded"
STRIP_STATIC="--strip-debug"
MAN_DIRS=({usr{,/local}{,/share},opt/*}/{man,info})
DOC_DIRS=(usr/{,local/}{,share/}{doc,gtk-doc} opt/*/{doc,gtk-doc})
STRIP_DIRS=(bin lib sbin usr/{bin,lib,sbin,local/{bin,lib,sbin}} opt/*/{bin,lib,sbin})
PURGE_TARGETS=(usr/{,share}/info/dir .packlist *.pod)
PKGEXT='.pkg.tar.xz'
SRCEXT='.src.tar.gz'
"""

class MakepkgTest(unittest.TestCase):
	def setUp(self):
		self.tmpdir = tempfile.mkdtemp()
		self.arch = subprocess.getoutput("arch")
		with open(os.path.join(self.tmpdir, "makepkg.conf"), "w") as f:
			f.write(makepkg_conf % {"arch": self.arch})

	def tearDown(self):
		shutil.rmtree(self.tmpdir)

	def run_makepkg(self):
		pwd = os.getcwd()
		os.chdir(self.tmpdir)
		ret = subprocess.call(["makepkg", "-f", "-d"],
				env = { "MAKEPKG_CONF": "./makepkg.conf" },
				stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		os.chdir(pwd)
		self.assertEqual(ret, 0)

	def run_rule_on_tarball(self, filename, rule):
		ret = subprocess.call(["unxz", filename + ".xz"])
		self.assertEqual(ret, 0)

		# process PKGINFO
		tar = tarfile.open(filename)
		info = tar.extractfile('.PKGINFO')
		pkg = PacmanPackage(pkginfo =
				info.read().decode("utf-8", "ignore"))
		info.close()
		pkg.detected_deps = []
		pkg.process()
		tar.close()

		tar = tarfile.open(filename)
		r = rule()
		r.analyze(pkg, tar)
		tar.close()
		return pkg, r

# vim: set ts=4 sw=4 noet:

