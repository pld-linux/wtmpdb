Summary:	Y2038 safe version of wtmp
Name:		wtmpdb
Version:	0.10.0
Release:	1
License:	BSD
Group:		Libraries
Source0:	https://github.com/thkukuk/wtmpdb/releases/download/v%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	e745d4fa82fc66978a4c152e89bb2db4
Patch0:		split-usr.patch
URL:		https://github.com/thkukuk/wtmpdb
BuildRequires:	audit-libs-devel
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 0.50.0
BuildRequires:	ninja >= 1.5
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.736
BuildRequires:	sqlite3-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The main features of wtmpdb are:

- It's using sqlite3 as database backend.

- Data is mainly collected via a PAM module, so that every tool can
  make use of it, without modifying existing packages. For cases where
  this is not possible, there is a library libwtmpdb.

- The wtmpdb last output is as compatible as possible with the old
  last implementation, but not all options are yet supported. For
  compatibility reasons, a symlink last pointing to wtmpdb can be
  created.

IMPORTANT To be Y2038 safe on 32bit architectures, the binaries needs
to be build with a 64bit time_t. This should be the standard on 64bit
architectures.

%package -n pam-pam_wtmpdb
Summary:	PAM module to record login and logout times of users
Group:		Base
Requires:	%{name} = %{version}-%{release}

%description -n pam-pam_wtmpdb
PAM module to record login and logout times of users.

%package devel
Summary:	Header files for wtmpdb library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki wtmpdb
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for wtmpdb library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki wtmpdb.

%prep
%setup -q
%patch0 -p1

%build
%meson build \
	-Dsplit-usr=true

%ninja_build -C build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/lib/wtmpdb

%ninja_install -C build

:> $RPM_BUILD_ROOT/var/lib/wtmpdb/wtmp.db

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README.md
%attr(755,root,root) %{_bindir}/wtmpdb
%attr(755,root,root) %{_libdir}/libwtmpdb.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libwtmpdb.so.0
%{_mandir}/man8/wtmpdb.8*
%{systemdunitdir}/wtmpdb-rotate.service
%{systemdunitdir}/wtmpdb-rotate.timer
%{systemdunitdir}/wtmpdb-update-boot.service
%{systemdtmpfilesdir}/wtmpdb.conf
%dir /var/lib/wtmpdb
%ghost /var/lib/wtmpdb/wtmp.db

%files -n pam-pam_wtmpdb
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_wtmpdb.so
%{_mandir}/man8/pam_wtmpdb.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwtmpdb.so
%{_includedir}/wtmpdb.h
%{_pkgconfigdir}/libwtmpdb.pc
