# 
# namcap rules - extravars
# Copyright (C) 2003-2009 Jesse Young <jesseyoung@gmail.com>
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
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# 

import re
import os
import subprocess
import tempfile
from Namcap.ruleclass import *

BASH_BUILTINS = set([
	"BASH", "BASHOPTS", "BASH_ALIASES", "BASH_ARGC", "BASH_ARGV", "BASH_CMDS", "BASH_LINENO",
	"BASH_SOURCE", "BASH_VERSINFO", "BASH_VERSION", "DIRSTACK", "EUID", "GROUPS", "HOSTNAME",
	"HOSTTYPE", "IFS", "MACHTYPE", "OPTERR", "OPTIND", "OSTYPE", "PATH", "PIPESTATUS", "PPID",
	"PS1", "PS2", "PS3", "PS4",
	"PWD", "SHELL", "SHELLOPTS", "SHLVL", "TERM", "UID",
	])

def find_lowercase_global_vars(pkgbuild):
	# list the variable names beginning with a lowercase letter
	varnames = []

	# write an annotated PKGBUILD to a temporary file
	f = tempfile.NamedTemporaryFile(delete = False)
	annotated_pkgbuild = pkgbuild + "\ndeclare +x"
	f.write(annotated_pkgbuild.encode('utf-8'))
	f.close()
	# run bash -r on it to list variables
	cwd = os.getcwd()
	os.chdir(os.path.dirname(f.name))
	p = subprocess.Popen(["bash", "-r", os.path.basename(f.name)],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	out, err = p.communicate()

	if p.returncode != 0:
		raise ValueError("parsing PKGBUILD failed")
	else:
		for l in out.decode("utf-8", "ignore").splitlines():
			m = re.match('[\s]*([a-z][a-zA-Z_0-9]*)\+?=', l)
			if not m:
				continue
			varnames.append(m.group(1))

	os.unlink(f.name)
	return set(varnames)

class package(PkgbuildRule):
	name = "extravars"
	description = "Verifies that extra variables start with an underscore"
	def analyze(self, pkginfo, tar):
		stdvars = ['arch', 'license', 'depends', 'makedepends',
				 'provides', 'conflicts' , 'replaces', 'backup',
				 'source', 'noextract', 'md5sums', 'sha1sums',
				 'sha256sums', 'sha384sums', 'sha512sums', 'pkgname',
				 'pkgbase', 'pkgver', 'pkgrel', 'pkgdesc', 'groups',
				 'url', 'install', 'changelog',
				 'options', 'optdepends']
		pkgbuild_vars = find_lowercase_global_vars("\n".join(pkginfo.pkgbuild))
		nonstdvars = pkgbuild_vars - set(stdvars)
		self.warnings.extend(
			[("extra-var-begins-without-underscore %s", varname) for
				varname in nonstdvars]
			)

# vim: set ts=4 sw=4 noet:
