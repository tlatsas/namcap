#! /usr/bin/env python
# 
# namcap - A Pacman package analyzer
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
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
# 

# System wide global stuff
import sys, os, os.path, imp, getopt, types, tarfile, re, string, Namcap, pacman
import shutil

sandbox_directory = '/tmp/namcap.' + str(os.getpid())

# Functions
# Return all possible modules (rules)
def get_modules():
	return Namcap.__all__

# Display usage information
def usage():
	print "usage: " + sys.argv[0] + " [-r rulelist | --rules=rulelist] [-e rulelist | --exclude=rulelist] [-i | --info] [-m | --machine-readable] package .."
	print "       -r list    : returns list of available rules"	
	print "       -i         : prints information responses from rules"
	print "       -m         : makes the output parseable (machine-readable)"
	sys.exit(2)

# Is the package a valid package file?
def verify_package(filename):
	if not os.path.isfile(filename):
		return 0
	if not tarfile.is_tarfile(filename):
		return 0
	try:
		tar = tarfile.open(package, "r")
		if not tar:
			return 0		
		if not len(tar.getmembers()) > 0:
			tar.close()
			return 0
		if not '.PKGINFO' in tar.getnames():
			tar.close()
			return 0
	except IOError:
		if tar:
			tar.close()
		return 0
	return tar

def process_tags(filename="/usr/share/namcap/tags"):
	tags = {}
	f = open(filename)
	for i in f.readlines():
		if i[0] == "#" or i.strip() == "": continue
		tagdata = i[:-1].split("::")
		tags[tagdata[0].strip()] = tagdata[1].strip()

	return tags

def check_rules_exclude(optlist):	
	'''Check if the -r (--rules) and the -r (--exclude) options
	are being used at same time'''
	args_used = 0
	for i in optlist:	
		if '-r' in i or '-e' in i:
			args_used += 1
		if '--rules' in i or '--exclude' in i:
			args_used += 1
			
	return args_used

# Main
modules = get_modules()
tags = process_tags()
info_reporting = 0

# get our options and process them
try:
	optlist, args = getopt.getopt(sys.argv[1:], "ihmr:e:", ["rules=", "exclude=", "info","help","machine-readable"])
except getopt.GetoptError:
	usage()

active_modules = []
m = lambda s: tags[s]

# Verifying if we are using the -r and -r options at same time
if check_rules_exclude(optlist) > 1:
	print "You cannot use '-r' (--rules) and '-e' (-exclude) options at same time"
	usage()

for i, k in optlist:	
	if i in ('-r', '--rules') and active_modules == []:		
		if k == 'list':
			print "-"*20 + " Namcap rule list " + "-"*20
			for j in modules:
				print string.ljust(j, 20) + ": " + __import__('Namcap.' + j, globals(), locals(), [Namcap]).package().long_name()
			sys.exit(2)
			
		module_list = k.split(',')
		for j in module_list:
			if j in modules:
				active_modules.append(j)
			else:
				print "Error: Rule '" + j + "' does not exist"
				usage()
		
	# Used to exclude some rules from the check			
	if i in ('-e', '--exclude') and active_modules == []:
		if use_specific_rules:
			print "Error: You cannot use -r"
			usage()
		else:
			module_list = k.split(',')
			active_modules = modules
			for j in module_list:			
				if j in modules:
					active_modules.remove(j)
				else:
					print "Error: Rule '" + j + "' does not exist"
					usage()	
				
	if i in ('-i', '--info'):
		info_reporting = 1
		
	if i in ('-m', '--machine-readable'):
		machine_readable = 1
		m = lambda s: s
		
	if i in ('-h', '--help'):
		usage()

# If there are no args, print usage
if (args == []):
	usage()

packages = args

# Go through each package, get the info, and apply the rules
for package in packages:
	extracted = 0
	if not os.access(package, os.R_OK):
		print "Error: Problem reading " + package
		usage()

	if package[-7:] == '.tar.gz':
		pkgtar = verify_package(package)

		if not pkgtar:			
			print "Error: " + package + " is empty or is not a valid package"
			if len(packages) > 1:
				continue
			else:
				sys.exit(2)
			
		
		pkginfo = pacman.load(package)

		# No rules selected?  Then select them all!
		if active_modules == []:
			active_modules = modules

		# Loop through each one, load them apply if possible
		for i in active_modules:
			cur_class = __import__('Namcap.' + i, globals(), locals(), [Namcap])
			pkg = cur_class.package()
			ret = [[],[],[]]
			if pkg.type() == "tarball":
				if pkg.prereq() == "extract":
					# If it's not extracted, then extract it and then analyze the package
					if not extracted:
						os.mkdir(sandbox_directory)
						for j in pkgtar.getmembers():
							pkgtar.extract(j, sandbox_directory)
						extracted = 1
					ret = pkg.analyze(pkginfo, sandbox_directory)
				elif pkg.prereq() == "pkg":
					ret = pkg.analyze(pkginfo, None)
				elif pkg.prereq() == "tar":
					ret = pkg.analyze(pkginfo, pkgtar)
				else:
					ret = [['Error running rule (' + i + ')'],[],[]]

				# Output the three types of messages
				if ret[0] != []:
					for j in ret[0]:
						print string.ljust(pkginfo.name, 10) + " E: " + m(j[0]) % j[1]
				if ret[1] != []:
					for j in ret[1]:
						print string.ljust(pkginfo.name, 10) + " W: " +  m(j[0]) % j[1]
				if ret[2] != [] and info_reporting:
					for j in ret[2]:
						print string.ljust(pkginfo.name, 10) + " I: " +  m(j[0]) % j[1]


		# Clean up if we extracted anything
		if extracted:
			shutil.rmtree(sandbox_directory)
	elif package[-8:] == 'PKGBUILD':
		# We might want to do some verifying in here... but really... isn't that what pacman.load is for?
		pkginfo = pacman.load(package)

		if pkginfo == None:
			print "Error: " + package + " is not a valid PKGBUILD"
			continue

		if active_modules == []:
			active_modules = modules

		for i in active_modules:
			cur_class = __import__('Namcap.' + i, globals(), locals(), [Namcap])
			pkg = cur_class.package()
			ret = [[],[],[]]
			if pkg.type() == "pkgbuild":
				ret = pkg.analyze(pkginfo, package)

			# Output the PKGBUILD messages
			if ret[0] != []:
				for j in ret[0]:
					print string.ljust("PKGBUILD (" + pkginfo.name + ")", 20) + " E: " + m(j[0]) % j[1]
			if ret[1] != []:
				for j in ret[1]:
					print string.ljust("PKGBUILD (" + pkginfo.name + ")", 20) + " W: " + m(j[0]) % j[1]
			if ret[2] != [] and info_reporting:
				for j in ret[2]:
					print string.ljust("PKGBUILD (" + pkginfo.name + ")", 20) + " I: " + m(j[0]) % j[1]
# vim: set ts=4 sw=4 noet:
