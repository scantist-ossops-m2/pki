Name:           pki-ra
Version:        1.3.1
Release:        1%{?dist}
Summary:        Dogtag Certificate System - Registration Authority
URL:            http://pki.fedoraproject.org/
License:        GPLv2
Group:          System Environment/Daemons

BuildArch:      noarch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  ant

Requires:       mod_nss >= 1.0.7
Requires:       mod_perl >= 1.99_16
Requires:       mozldap >= 6.0.2
Requires:       pki-native-tools
Requires:       pki-ra-ui
Requires:       pki-selinux
Requires:       pki-setup
Requires:       pki-silent
Requires:       perl-DBD-SQLite
Requires:       sendmail
Requires:       sqlite
Requires(post):    chkconfig
Requires(preun):   chkconfig
Requires(preun):   initscripts
Requires(postun):  initscripts

Source0:        http://pki.fedoraproject.org/pki/sources/%{name}/%{name}-%{version}.tar.gz

%description
Dogtag Certificate System is an enterprise software system designed
to manage enterprise Public Key Infrastructure (PKI) deployments.

The Dogtag Registration Authority is an optional PKI subsystem that
acts as a front-end for authenticating and processing
enrollment requests, PIN reset requests, and formatting requests.

Dogtag Registration Authority communicates over SSL with the
Dogtag Certificate Authority to fulfill the user's requests.

%prep

%setup -q

cat << \EOF > %{name}-prov
#!/bin/sh
%{__perl_provides} $* |\
sed -e '/perl(PKI.*)/d' -e '/perl(Template.*)/d'
EOF

%global __perl_provides %{_builddir}/%{name}-%{version}/%{name}-prov
chmod +x %{__perl_provides}

cat << \EOF > %{name}-req
#!/bin/sh
%{__perl_requires} $* |\
sed -e '/perl(PKI.*)/d' -e '/perl(Template.*)/d'
EOF

%global __perl_requires %{_builddir}/%{name}-%{version}/%{name}-req
chmod +x %{__perl_requires}

%build
ant \
    -Dinit.d="rc.d/init.d" \
    -Dproduct.ui.flavor.prefix="" \
    -Dproduct.prefix="pki" \
    -Dproduct="ra" \
    -Dversion="%{version}"

%install
rm -rf %{buildroot}
cd dist/binary
unzip %{name}-%{version}.zip -d %{buildroot}
sed -i 's/^preop.product.version=.*$/preop.product.version=%{version}/' %{buildroot}%{_datadir}/pki/ra/conf/CS.cfg
mkdir -p %{buildroot}%{_localstatedir}/lock/pki/ra
mkdir -p %{buildroot}%{_localstatedir}/run/pki/ra

%clean
rm -rf %{buildroot}

%post
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add pki-rad || :

%preun
if [ $1 = 0 ] ; then
    /sbin/service pki-rad stop >/dev/null 2>&1
    /sbin/chkconfig --del pki-rad || :
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service pki-rad condrestart >/dev/null 2>&1 || :
fi

%files
%defattr(-,root,root,-)
%doc LICENSE
%{_initrddir}/*
%{_datadir}/pki/
%{_localstatedir}/lock/*
%{_localstatedir}/run/*

%changelog
* Thu Apr 8 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.1-1
- Bugzilla Bug #564131 - Config wizard : all subsystems - done panel text
  needs correction

* Tue Feb 16 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-6
- Bugzilla Bug #566060 -  Add 'pki-native-tools' as a runtime dependency
  for RA, and TPS . . .

* Fri Jan 29 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-5
- Bugzilla Bug #553076 - Apply "registry" logic to pki-ra . . .
- Applied filters for unwanted perl provides and requires
- Restored "perl-DBD-SQLite" runtime dependency

* Tue Jan 26 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-4
- Bugzilla Bug #553850 - Review Request: pki-ra - Dogtag Registration Authority
  Per direction from the Fedora community, removed the following
  explicit "Requires":

      perl-DBI
      perl-HTML-Parser
      perl-HTML-Tagset
      perl-Parse-RecDescent
      perl-URI
      perl-XML-NamespaceSupport
      perl-XML-Parser
      perl-XML-Simple

* Thu Jan 14 2010 Matthew Harmsen <mharmsen@redhat.com> 1.3.0-3
- Bugzilla Bug #512234 - Move pkiuser:pkiuser check from spec file into
  pkicreate . . .
- Bugzilla Bug #547471 - Apply PKI SELinux changes to PKI registry model
- Bugzilla Bug #553076 - Apply "registry" logic to pki-ra . . .
- Bugzilla Bug #553078 - Apply "registry" logic to pki-tps . . .
- Bugzilla Bug #553850 - Review Request: pki-ra - Dogtag Registration Authority

* Mon Dec 14 2009 Kevin Wright <kwright@redhat.com> 1.3.0-2
- Removed 'with exceptions' from License

* Fri Oct 16 2009 Ade Lee <alee@redhat.com> 1.3.0-1
- Bugzilla Bug #X - Fedora Packaging Changes
