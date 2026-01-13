Name:           webapp-manager
Version:        1.0.0
Release:        1%{?dist}
Summary:        Modern GTK4/Libadwaita Web App Manager for Firefox Kiosk mode

License:        GPLv3+
URL:            https://github.com/steve-rock-wheelhouser/webapp-manager
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       python3
Requires:       python3-gobject
Requires:       gtk4
Requires:       libadwaita
Requires:       firefox

%description
A graphical utility to manage and install web applications as standalone 
kiosk-mode desktop entries using Firefox instances.

%prep
%setup -q

%install
mkdir -p %{buildroot}%{_libexecdir}/%{name}
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

# Install python scripts
cp app.py %{buildroot}%{_libexecdir}/%{name}/
cp manager.py %{buildroot}%{_libexecdir}/%{name}/

# Create wrapper script
cat <<EOF > %{buildroot}%{_bindir}/%{name}
#!/bin/bash
exec python3 %{_libexecdir}/%{name}/app.py "\$@"
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}

# Install desktop file
cp webapp-manager.desktop %{buildroot}%{_datadir}/applications/

# Install icon
cp assets/icons/webapp-manager.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/

%files
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/scalable/apps/%{name}.svg

%changelog
* Tue Jan 13 2026 Steve Rock <steve.rock@wheelhouser.com> - 1.0.0-1
- Initial release with GTK4 and Libadwaita support
