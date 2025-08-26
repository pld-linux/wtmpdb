#
# Conditional build:
%bcond_with	wtmpdbd		# wtmpdbd daemon with sd-varlink support

Summary:	Y2038 safe version of wtmp
Summary(pl.UTF-8):	Wersja wtmp odporna na Y2038
Name:		wtmpdb
Version:	0.74.0
Release:	1
License:	BSD
Group:		Libraries
#Source0Download: https://github.com/thkukuk/wtmpdb/releases
Source0:	https://github.com/thkukuk/wtmpdb/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	789114600c2f76d16ec37b494a47b854
Patch0:		split-usr.patch
URL:		https://github.com/thkukuk/wtmpdb
BuildRequires:	audit-libs-devel
# _TIME_BITS=64
BuildRequires:	glibc-devel >= 6:2.34
BuildRequires:	libxslt-progs
BuildRequires:	meson >= 0.61.0
BuildRequires:	ninja >= 1.5
BuildRequires:	pam-devel
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 2.042
BuildRequires:	sqlite3-devel >= 3
BuildRequires:	systemd-devel >= 1:209
%{?with_wtmpdbd:BuildRequires:	systemd-devel >= 1:257}
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

%description -l pl.UTF-8
Główne cechy wtmpdb to:
- wykorzystanie sqlite3 jako backendu bazy danych
- zbieranie danych głównie poprzez moduł PAM, dzięki czemu każde
  narzędzie może z niego korzystać bez dodatkowych modyfikacji; w
  przypadkach, gdy nie jest to możliwe, istnieje biblioteka libwtmpdb
- wyjście last z wtmpdb jest zgodne ze starą implementacją last na ile
  to możliwe, ale nie wszystkie opcje są już obsługiwane; ze względu
  na zgodność, można wykonać dowiązanie do programu last wskazujące na
  wersję wtmpdb.

%package -n pam-pam_wtmpdb
Summary:	PAM module to record login and logout times of users
Summary(pl.UTF-8):	Moduł PAM do zapisu czasów zalogowania i wylogowania użytkowników
Group:		Base
Requires:	%{name} = %{version}-%{release}

%description -n pam-pam_wtmpdb
PAM module to record login and logout times of users.

%description -n pam-pam_wtmpdb -l pl.UTF-8
Moduł PAM do zapisu czasów zalogowania i wylogowania użytkowników.

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
%patch -P0 -p1

%build
%meson \
	-Daudit=enabled \
	-Dman=enabled \
	-Dsplit-usr=true \
	-Dsystemd=enabled \
	-Dwtmpdbd=%{__enabled_disabled wtmpdbd}

%meson_build

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/var/lib/wtmpdb

%meson_install

:> $RPM_BUILD_ROOT/var/lib/wtmpdb/wtmp.db

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
%systemd_post wtmpdb-rotate.timer wtmpdb-update-boot.service

%preun
%systemd_preun wtmpdb-rotate.timer wtmpdb-update-boot.service

%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE NEWS README.md
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
%if %{with wtmpdbd}
%attr(755,root,root) %{_libexecdir}/wtmpdbd
%{_mandir}/man8/wtmpdbd.8*
%{_mandir}/man8/wtmpdbd.service.8*
%{_mandir}/man8/wtmpdbd.socket.8*
%endif

%files -n pam-pam_wtmpdb
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_wtmpdb.so
%{_mandir}/man8/pam_wtmpdb.8*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libwtmpdb.so
%{_includedir}/wtmpdb.h
%{_pkgconfigdir}/libwtmpdb.pc
