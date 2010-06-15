#
# namcap rules - utility functions
# Copyright (C) 2009 Dan McGee <dan@archlinux.org>
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

import os
import re
import stat

def read_carefully(path, readcall):
	if not os.path.isfile(path):
		return False
	reset_perms = False
	if not os.access(path, os.R_OK):
		# don't mess with links we can't read
		if os.path.islink(path):
			return None
		reset_perms = True
		# attempt to make it readable if possible
		statinfo = os.stat(path)
		newmode = statinfo.st_mode | stat.S_IRUSR
		try:
			os.chmod(path, newmode)
		except IOError:
			return None
	fd = open(path)
	val = readcall(fd)
	fd.close()
	# reset permissions if necessary
	if reset_perms:
		# set file back to original permissions
		os.chmod(path, statinfo.st_mode)
	return val

def is_elf(path):
	"""
	Given a file path, ensure it exists and peek at the first few bytes
	to determine if it is an ELF file.
	"""
	bytes = read_carefully(path, lambda fd: fd.read(4))
	if not bytes:
		return False
	# magic elf header, present in binaries and libraries
	if bytes == "\x7FELF":
		return True
	else:
		return False

supported_scripts = ['python', 'perl', 'ruby', 'wish', 'expect',
	'tk', 'bash', 'sh', 'dash', 'tcsh', 'pdksh' ]

def script_type(path):
	global supported_scripts
	firstline = read_carefully(path, lambda fd: fd.readline())
	if not firstline:
		return None
	script = re.compile('#!.*/(.*)')
	firstlinere = script.match(firstline)
	if firstlinere != None:
		cmdname = firstlinere.group(1).split()[0]
		if cmdname in supported_scripts:
			return cmdname
	return None

clean_filename = lambda s: re.search(r"/tmp/namcap\.[0-9]*/(.*)", s).group(1)

# vim: set ts=4 sw=4 noet:
