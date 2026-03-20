# disable_lto is a workaround for unresolved symbols in the 32bit library.
# We add -flto manually after building the 32bit package, so nothing lost.
%global _disable_lto 1

%bcond_without python

# ICU support is needed in order for libreoffice, chromium, qtwebengine and
# maybe others to use system libxml.
# Please don't disable it without good reason. And if you do, fix the
# packages that rely on it.
%bcond_without icu

# (tpg) enable PGO build
%bcond_without pgo

%define major 2
%define libname %mklibname xml2.13
%define devname %mklibname xml2.13 -d
# libxml2 is used by wine -- needs a 32-bit compat package
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif
%if %{with compat32}
%define lib32name libxml2.13
%define dev32name libxml2-devel
%endif

# (tpg) optimize it a bit
%global optflags %{optflags} -O3

Summary:	Compat library providing XML and HTML support
Name:		libxml2.13
Version:	2.13.9
Release:	2
License:	MIT
Group:		System/Libraries
Url:		https://www.xmlsoft.org/
Source0:	https://download.gnome.org/sources/libxml2/%(echo %{version}|cut -d. -f1-2)/libxml2-%{version}.tar.xz
#Source0:	http://xmlsoft.org/sources/%{name}-%{version}.tar.gz
Patch1:		libxml2-2.9.9-no-Lusrlib.patch
Patch2:		https://src.fedoraproject.org/rpms/libxml2/raw/rawhide/f/libxml2-2.9.8-python3-unicode-errors.patch
BuildRequires:	cmake ninja
%if %{with python}
BuildRequires:	pkgconfig(python3)
BuildRequires:	gettext-devel
%endif
BuildRequires:	pkgconfig(readline)
BuildRequires:	pkgconfig(liblzma)
BuildRequires:	pkgconfig(zlib)
%ifarch riscv64
BuildRequires:	atomic-devel
%endif
%if %{with icu}
BuildRequires:	pkgconfig(icu-i18n)
%endif
%if %{with compat32}
# We don't require the same slew of dependencies as the regular version:
# We don't build the command line tools (hence, no need for readline),
# and since wine doesn't use python, we don't need the python bits either.
# Lastly, ICU is enabled in the regular build because of WebKit/Blink and
# LibreOffice - neither of which is relevant to wine.
BuildRequires:	devel(libz)
BuildRequires:	devel(liblzma)
%endif
%if "%{lib32name}" == "%{name}"
%endif

%description
This library allows you to manipulate XML files. It includes support
for reading, modifying and writing XML and HTML files. There is DTDs
support: this includes parsing and validation even with complex DtDs,
either at parse time or later once the document has been modified. The
output can be a simple SAX stream or and in-memory DOM-like
representations. In this case one can use the built-in XPath and
XPointer implementation to select subnodes or ranges. A flexible
Input/Output mechanism is available, with existing HTTP and FTP modules
and combined to a URI library.

%package -n %{libname}
Summary:	Shared libraries providing XML and HTML support
Group:		System/Libraries

%description -n %{libname}
This library allows you to manipulate XML files. It includes support
for reading, modifying and writing XML and HTML files. There is DTDs
support: this includes parsing and validation even with complex DtDs,
either at parse time or later once the document has been modified.

#package -n %{devname}
#Summary:	Libraries, includes, etc. to develop XML and HTML applications
#Group:		Development/C
#Requires:	%{libname} = %{EVRD}
#Provides:	%{name}-devel = %{EVRD}
#if %{with icu}
# libxml/encoding.h #includes <unicode/ucnv.h>
#Requires:	pkgconfig(icu-i18n)
#endif
# Needed because libxml2.so links to them
#Requires:	pkgconfig(liblzma)
#Requires:	pkgconfig(zlib)

#description -n %{devname}
#Libraries, include files, etc you can use to develop XML applications.
#This library allows you to manipulate XML files. It includes support
#for reading, modifying and writing XML and HTML files. There is DTDs
#support: this includes parsing and validation even with complex DtDs,
#either at parse time or later once the document has been modified.

%if %{with compat32}
%if "%{lib32name}" != "%{name}"
%package -n %{lib32name}
Summary:	Shared libraries providing XML and HTML support (32-bit)
Group:		System/Libraries

%description -n %{lib32name}
This library allows you to manipulate XML files. It includes support
for reading, modifying and writing XML and HTML files. There is DTDs
support: this includes parsing and validation even with complex DtDs,
either at parse time or later once the document has been modified.
%endif

#package -n %{dev32name}
#Summary:	Libraries, includes, etc. to develop XML and HTML applications (32-bit)
#Group:		Development/C
#Requires:	%{lib32name} = %{EVRD}
#Requires:	%{devname} = %{EVRD}
# Needed because libxml2.so links to them
#Requires:	pkgconfig(liblzma)
#Requires:	devel(libz)

#description -n %{dev32name}
#Libraries, include files, etc you can use to develop XML applications.
#This library allows you to manipulate XML files. It includes support
#for reading, modifying and writing XML and HTML files. There is DTDs
#support: this includes parsing and validation even with complex DtDs,
#either at parse time or later once the document has been modified.
%endif

%package utils
Summary:	Utilities to manipulate XML files
Group:		System/Libraries

%description utils
This packages contains utils to manipulate XML files.

%if %{with python}
%package -n python-%{name}
Summary:	Python bindings for the libxml2 library
Group:		Development/Python
%rename		%{name}-python
Requires:	%{libname} = %{EVRD}

%description -n python-%{name}
The libxml2-python package contains a module that permits applications
written in the Python programming language to use the interface
supplied by the libxml2 library to manipulate XML files.

This library allows you to manipulate XML files. It includes support
for reading, modifying and writing XML and HTML files. There is DTDs
support: this includes parsing and validation even with complex DtDs,
either at parse time or later once the document has been modified.
%endif

%prep
%autosetup -n libxml2-%{version} -p1

%if %{with compat32}
export CONFIGURE_TOP="$(pwd)"
%cmake32 \
	-G Ninja \
	-DLIBXML2_WITH_PYTHON:BOOL=OFF \
	-DLIBXML2_WITH_ICU:BOOL=OFF \
	-DLIBXML2_WITH_TLS:BOOL=ON \
	-DLIBXML2_WITH_THREAD_ALLOC:BOOL=ON
cd ..
%endif

%build
%if %{with compat32}
%ninja_build -C build32
%endif

%if %{with pgo}
export LD_LIBRARY_PATH="$(pwd)/build"

CFLAGS="%{optflags} -flto -fprofile-generate" \
CXXFLAGS="%{optflags} -flto -fprofile-generate" \
LDFLAGS="%{build_ldflags} -flto -fprofile-generate" \
%cmake \
	-G Ninja \
%if !%{with python}
	-DLIBXML2_WITH_PYTHON:BOOL=OFF \
%endif
%if %{with icu}
	-DLIBXML2_WITH_ICU:BOOL=ON \
%else
	-DLIBXML2_WITH_ICU:BOOL=OFF \
%endif
	-DLIBXML2_WITH_TLS:BOOL=ON \
	-DLIBXML2_WITH_THREAD_ALLOC:BOOL=ON
cd ..
%ninja_build -C build

./dbgenattr.pl 100000 >dba100000.xml
./build/xmllint --noout  dba100000.xml
./build/xmllint --stream  dba100000.xml
./build/xmllint --noout --valid test/valid/REC-xml-19980210.xml
./build/xmllint --stream --valid test/valid/REC-xml-19980210.xml
unset LD_LIBRARY_PATH
llvm-profdata merge --output=%{name}-llvm.profdata $(find . -name "*.profraw" -type f)
PROFDATA="$(realpath %{name}-llvm.profdata)"
rm -f *.profraw

%ninja_build -C build clean

CFLAGS="%{optflags} -flto -fprofile-use=$PROFDATA" \
CXXFLAGS="%{optflags} -flto -fprofile-use=$PROFDATA" \
LDFLAGS="%{build_ldflags} -flto -fprofile-use=$PROFDATA" \
%else
CFLAGS="%{optflags} -flto" \
CXXFLAGS="%{optflags} -flto" \
LDFLAGS="%{build_ldflags} -flto" \
%endif
%cmake \
	-G Ninja \
%if !%{with python}
	-DLIBXML2_WITH_PYTHON:BOOL=OFF \
%else
	-DLIBXML2_PYTHON_INSTALL_DIR=%{py_platsitedir} \
%endif
%if %{with icu}
	-DLIBXML2_WITH_ICU:BOOL=ON \
%else
	-DLIBXML2_WITH_ICU:BOOL=OFF \
%endif
	-DLIBXML2_WITH_TLS:BOOL=ON \
	-DLIBXML2_WITH_THREAD_ALLOC:BOOL=ON
cd ..

%ninja_build -C build

xz --text -T0 -c doc/libxml2-api.xml > doc/libxml2-api.xml.xz

%install
%if %{with compat32}
%ninja_install -C build32
# remove devel in compat package
rm -rf \
 %{buildroot}%{_prefix}/lib/libxml2.so \
 %{buildroot}%{_prefix}/lib/pkgconfig \
 %{buildroot}%{_prefix}/lib/cmake/libxml2*
  
%endif
%ninja_install -C build
# remove devel in compat package
rm -rf \
  %{buildroot}%{_datadir}/aclocal \
  %{buildroot}%{_bindir}/xml2-config \
  %{buildroot}%{_libdir}/cmake/libxml2* \
  %{buildroot}%{_libdir}/libxml2.so \
  %{buildroot}%{_libdir}/pkgconfig \
  %{buildroot}%{_includedir} \

# remove unpackaged files
rm -rf %{buildroot}%{_prefix}/doc %{buildroot}%{_datadir}/doc

#check
# all tests must pass
# use TARBALLURL_2="" TARBALLURL="" TESTDIRS="" to disable xstc test which are using remote tarball
# Currently (2.9.4-1) disabled because it freezes some build machines
#make TARBALLURL_2="" TARBALLURL="" TESTDIRS="" check

%files -n %{libname}
%{_libdir}/libxml2.so.%{major}*

%files utils
%{_bindir}/xmlcatalog
%{_bindir}/xmllint
%doc %{_mandir}/man1/xmlcatalog*
%doc %{_mandir}/man1/xmllint*

%if %{with python}
%files -n python-%{name}
%doc python/tests/*.py
%{py_platsitedir}/*.so*
%{py_platsitedir}/*.py
%endif

#files -n %{devname}
#doc README* Copyright
#doc doc/libxml2-api.xml.xz
#{_datadir}/aclocal/*
#{_bindir}/xml2-config
#{_libdir}/cmake/libxml2*
#{_libdir}/libxml2.so
#{_libdir}/pkgconfig/*
#{_includedir}/*
#doc %{_mandir}/man1/xml2-config*

%if %{with compat32}
%files -n %{lib32name}
%{_prefix}/lib/libxml2.so.%{major}*

#files -n %{dev32name}
#{_prefix}/lib/libxml2.so
#{_prefix}/lib/pkgconfig/*.pc
#{_prefix}/lib/cmake/libxml2*
%endif
