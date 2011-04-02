# -*- coding: utf-8 -*-
# 
# namcap - tags
# Copyright (C) 2003-2009 Jason Chu <jason@archlinux.org>
# Copyright (c) 2011 Rémy Oudompheng <remy@archlinux.org>
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

import os

tags = {}

DEFAULT_TAGS = "/usr/share/namcap/namcap-tags"

def load_tags(filename = None, machine = False):
	"Loads tags from the given filename"
	global tags
	tags = {}
	if filename is None:
		filename = DEFAULT_TAGS

	f = open(filename)
	for line in f:
		line = line.strip()
		if line.startswith("#") or line == "":
			continue
		machinetag, humantag = line.split("::")
		machinetag = machinetag.strip()
		humantag = humantag.strip()

		if machine:
			tags[machinetag] = machinetag
		else:
			tags[machinetag] = humantag

def format_message(msg):
	"""
	Formats a tuple (tag, data)
	"""
	tag, data = msg
	return (tags[tag] % data)

# Try to load tags by default
if os.path.exists(DEFAULT_TAGS):
	load_tags(DEFAULT_TAGS)
elif os.path.exists("namcap-tags"):
	load_tags("namcap-tags")


# vim: set ts=4 sw=4 noet:
