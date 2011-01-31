#! /usr/bin/env python2
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
def get_modules():
	"""Return all possible modules (rules)"""
	return Namcap.rules.all_rules

def usage():
	"""Display usage information"""
	print("")
	print("Usage: " + sys.argv[0] + " [OPTIONS] packages")
	print("")
	print("Options are:")
	print("    -i                               : prints information responses from rules")
	print("    -m                               : makes the output parseable (machine-readable)")
	print("    -e rulelist, --exclude=rulelist  : don't apply RULELIST rules to the package")
	print("    -r rulelist, --rules=rulelist    : only apply RULELIST rules to the package")

	sys.exit(2)

def verify_package(filename):
	"""Checks if a tarball is a valid package"""
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

def process_tags(filename=None, machine=False):
	if machine:
		return lambda s: s
	tags = {}
	if not filename:
		filename="/usr/share/namcap/namcap-tags"
	f = open(filename)
	for i in f.readlines():
		if i[0] == "#" or i.strip() == "": continue
		tagdata = i[:-1].split("::")
		tags[tagdata[0].strip()] = tagdata[1].strip()

	return lambda s: tags[s]

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

def show_messages(name, key, messages):
	for msg in messages:
		print("%s %s: %s" % (name, key, m(msg[0]) % msg[1]))

def process_realpackage(package, modules):
	"""Runs namcap checks over a package tarball"""
	extracted = 0
	pkgtar = verify_package(package)

	if not pkgtar:
		print("Error: " + package + " is empty or is not a valid package")
		return 1

	pkginfo = pacman.load(package)

	# Loop through each one, load them apply if possible
	for i in modules:
		pkg = get_modules()[i]()
		ret = [[], [], []]

		if isinstance(pkg, Namcap.ruleclass.PkgInfoRule):
			ret = pkg.analyze(pkginfo, None)
		if isinstance(pkg, Namcap.ruleclass.TarballRule):
			if pkg.prereq() == "extract":
				# If it's not extracted, then extract it and then analyze the package
				if not extracted:
					os.mkdir(sandbox_directory)
					for j in pkgtar.getmembers():
						pkgtar.extract(j, sandbox_directory)
					extracted = 1
				ret = pkg.analyze(pkginfo, sandbox_directory)
			elif pkg.prereq() == "tar":
				ret = pkg.analyze(pkginfo, pkgtar)
			else:
				ret = [['Error running rule (' + i + ')'], [], []]

		# Output the three types of messages
		show_messages(pkginfo.name, 'E', ret[0])
		show_messages(pkginfo.name, 'W', ret[1])
		if info_reporting:
			show_messages(pkginfo.name, 'I', ret[2])

	# Clean up if we extracted anything
	if extracted:
		shutil.rmtree(sandbox_directory)

def process_pkgbuild(package, modules):
	"""Runs namcap checks over a PKGBUILD"""
	# We might want to do some verifying in here... but really... isn't that what pacman.load is for?
	pkginfo = pacman.load(package)

	if pkginfo == None:
		print("Error: " + package + " is not a valid PKGBUILD")
		return 1

	for i in modules:
		pkg = get_modules()[i]()
		ret = [[], [], []]
		if isinstance(pkg, Namcap.ruleclass.PkgInfoRule):
			ret = pkg.analyze(pkginfo, None)
		if isinstance(pkg, Namcap.ruleclass.PkgbuildRule):
			ret = pkg.analyze(pkginfo, package)

		# Output the PKGBUILD messages
		name = "PKGBUILD (" + pkginfo.name + ")"
		show_messages(name, 'E', ret[0])
		show_messages(name, 'W', ret[1])
		if info_reporting:
			show_messages(name, 'I', ret[2])

# Main
modules = get_modules()
info_reporting = 0
machine_readable = False
filename = None

# get our options and process them
try:
	optlist, args = getopt.getopt(sys.argv[1:], "ihmr:e:t:",
			["info", "help", "machine-readable", "rules=", "exclude=", "tags="])
except getopt.GetoptError:
	usage()

active_modules = []

# Verifying if we are using the -r and -r options at same time
if check_rules_exclude(optlist) > 1:
	print("You cannot use '-r' (--rules) and '-e' (-exclude) options at same time")
	usage()

for i, k in optlist:
	if i in ('-r', '--rules') and active_modules == []:
		if k == 'list':
			print("-"*20 + " Namcap rule list " + "-"*20)
			for j in modules:
				print(string.ljust(j, 20) + ": " + modules[j].description)
			sys.exit(2)

		module_list = k.split(',')
		for j in module_list:
			if j in modules:
				active_modules[j] = modules[j]
			else:
				print("Error: Rule '" + j + "' does not exist")
				usage()

	# Used to exclude some rules from the check
	if i in ('-e', '--exclude') and active_modules == []:
		module_list = k.split(',')
		active_modules.update(modules)
		for j in module_list:
			if j in modules:
				active_modules.pop(j)
			else:
				print("Error: Rule '" + j + "' does not exist")
				usage()

	if i in ('-i', '--info'):
		info_reporting = 1

	if i in ('-h', '--help'):
		usage()
	if i in ('-m', '--machine-readable'):
		machine_readable = True

	if i in ('-t', '--tags'):
		filename = k

# If there are no args, print usage
if (args == []):
	usage()

m = process_tags(filename=filename, machine=machine_readable)
packages = args

# No rules selected?  Then select them all!
if active_modules == []:
	active_modules = modules

# Go through each package, get the info, and apply the rules
for package in packages:
	if not os.access(package, os.R_OK):
		print("Error: Problem reading " + package)
		usage()

	if os.path.isfile(package) and tarfile.is_tarfile(package):
		process_realpackage(package, active_modules)
	elif package[-8:] == 'PKGBUILD':
		process_pkgbuild(package, active_modules)
	else:
		print("Error: Cannot process %s" % package)

# vim: set ts=4 sw=4 noet:
