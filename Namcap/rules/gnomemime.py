# 
# namcap rules - gnomemime
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
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
# 

from Namcap.ruleclass import *

class package(TarballRule):
    name = "gnomemime"
    description = "Checks for generated GNOME mime files"
    def analyze(self, pkginfo, tar):
        mime_files = [
                'usr/share/applications/mimeinfo.cache',
                'usr/share/mime/XMLnamespaces', 
                'usr/share/mime/aliases', 
                'usr/share/mime/globs', 
                'usr/share/mime/magic', 
                'usr/share/mime/subclasses'
                ]

        for i in tar.getnames():
            if i in mime_files:
                self.errors.append(("gnome-mime-file %s", i))
                
# vim: set ts=4 sw=4 noet:
