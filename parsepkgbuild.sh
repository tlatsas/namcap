#!/bin/bash -r

source $1

# ensure $pkgname, $pkgver, and $pkgrel variables were found
if [ -z "$pkgname" -o -z "$pkgver" -o -z "$pkgrel" ]; then
	echo "error: invalid package file"
	exit 1
fi

function pkginfo() {

# create desc entry
if [ -n "$pkgname" ]; then
	echo -e "%NAME%\n$pkgname\n"
	echo -e "%VERSION%\n$pkgver-$pkgrel\n"
fi
if [ -n "$pkgdesc" ]; then
	echo -e "%DESC%\n$pkgdesc\n"
fi
if [ -n "$groups" ]; then
	echo "%GROUPS%"
	for i in ${groups[@]}; do echo $i; done
	echo ""
fi

if [ -n "$url" ]; then
	echo -e "%URL%\n$url\n"
fi
if [ -n "$license" ]; then
	echo "%LICENSE%"
	for i in ${license[@]}; do echo $i; done
	echo ""
fi
if [ -n "$arch" ]; then
	echo "%ARCH%"
	for i in ${arch[@]}; do echo $i; done
	echo ""
fi
if [ -n "$builddate" ]; then
	echo -e "%BUILDDATE%\n$builddate\n"
fi
if [ -n "$packager" ]; then
	echo -e "%PACKAGER%\n$packager\n"
fi

if [ -n "$replaces" ]; then
	echo "%REPLACES%"
	for i in "${replaces[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$force" ]; then
	echo -e "%FORCE%\n"
fi

# create depends entry
if [ -n "$depends" ]; then
	echo "%DEPENDS%"
	for i in "${depends[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$makedepends" ]; then
	echo "%MAKEDEPENDS%"
	for i in "${makedepends[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$optdepends" ]; then
	echo "%OPTDEPENDS%"
	for i in "${optdepends[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$conflicts" ]; then
	echo "%CONFLICTS%"
	for i in "${conflicts[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$provides" ]; then
	echo "%PROVIDES%"
	for i in "${provides[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$backup" ]; then
	echo "%BACKUP%"
	for i in "${backup[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$options" ]; then
	echo "%OPTIONS%"
	for i in "${options[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$source" ]; then
	echo "%SOURCE%"
	for i in "${source[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$md5sums" ]; then
	echo "%MD5SUMS%"
	for i in "${md5sums[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$sha1sums" ]; then
	echo "%SHA1SUMS%"
	for i in "${sha1sums[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$sha256sums" ]; then
	echo "%SHA256SUMS%"
	for i in "${sha256sums[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$sha384sums" ]; then
	echo "%SHA384SUMS%"
	for i in "${sha384sums[@]}"; do echo $i; done
	echo ""
fi
if [ -n "$sha512sums" ]; then
	echo "%SHA512SUMS%"
	for i in "${sha512sums[@]}"; do echo $i; done
	echo ""
fi

if [ -n "$install" ]; then
	echo -e "%INSTALL%\n$install\n"
fi

unset i
echo "%SETVARS%"
compgen -A variable
}

# is it a split pkgbuild ?
if [ -n "${pkgbase}" ]; then
	_namcap_pkgnames=(${pkgname[@]})
	unset pkgname
	echo -e "%SPLIT%\n1\n"
	echo -e "%BASE%\n${pkgbase}\n"
	echo "%NAMES%"
	for i in ${_namcap_pkgnames[@]}; do echo $i; done
	echo ""
	pkginfo
	# print per package information
	for _namcap_subpkg in ${_namcap_pkgnames[@]}
	do
		echo -e '\0'
		pkgname=$_namcap_subpkg
		package_$_namcap_subpkg
		pkginfo
		# did the function actually exist?
		echo "%PKGFUNCTION%"
		type -t package_$_namcap_subpkg || echo undefined
		echo ""
	done
else
	pkginfo
fi

# vim: set noet ts=4 sw=4:
