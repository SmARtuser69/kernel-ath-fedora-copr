#
# spec file for a custom Linux kernel package for Fedora with ath patches
#
# Name:        kernel-ath
# Summary:     The Linux kernel (ath driver patches)
#

# Use a dynamic approach to versioning
%global ath_release 1

Name:          kernel-ath
Version:       %(make -s -C %{_sourcedir}/ath-next kernelversion)
Release:       %{ath_release}.ath%{?dist}
Summary:       The Linux kernel with ath-next driver patches
License:       GPL-2.0-only
URL:           https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git/
Source0:       https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git/snapshot/ath-next.tar.gz

ExclusiveArch: x86_64

%global debug_package %{nil}

BuildRequires: gcc
BuildRequires: make
BuildRequires: bison
BuildRequires: flex
BuildRequires: openssl-devel
BuildRequires: elfutils-libelf-devel
BuildRequires: bc
BuildRequires: ncurses-devel
BuildRequires: rpm-build
BuildRequires: perl
BuildRequires: python3
BuildRequires: rsync
BuildRequires: kmod

# Additional build dependencies for ath-next features
BuildRequires: gcc-c++
BuildRequires: rust
BuildRequires: bindgen

%description
The Linux kernel, built from the ath-next development branch, which includes
the latest patches and features for Atheros wireless drivers. This package
is intended for testing and development purposes on Fedora systems.

%prep
%setup -q -n ath-next

%build
make defconfig
make %{?_smp_mflags} LOCALVERSION="-%{release}.%{_arch}"

%install
make INSTALL_MOD_PATH=%{buildroot} modules_install

install -d %{buildroot}/boot
install -m 644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{version}-%{ath_release}.ath%{?dist}.%{_arch}
install -m 644 System.map %{buildroot}/boot/System.map-%{version}-%{ath_release}.ath%{?dist}.%{_arch}
install -m 644 .config %{buildroot}/boot/config-%{version}-%{ath_release}.ath%{?dist}.%{_arch}

%files
/boot/vmlinuz-%{version}-%{ath_release}.ath%{?dist}.%{_arch}
/boot/System.map-%{version}-%{ath_release}.ath%{?dist}.%{_arch}
/boot/config-%{version}-%{ath_release}.ath%{?dist}.%{_arch}
/lib/modules/%{version}-%{ath_release}.ath%{?dist}.%{_arch}/

%post
echo "Running kernel-install script for %{version}-%{ath_release}.ath%{?dist}.%{_arch}..."
/usr/bin/kernel-install add %{version}-%{ath_release}.ath%{?dist}.%{_arch} /boot/vmlinuz-%{version}-%{ath_release}.ath%{?dist}.%{_arch}

%postun
if [ $1 -eq 0 ] ; then
    echo "Running kernel-install remove for %{version}-%{ath_release}.ath%{?dist}.%{_arch}..."
    /usr/bin/kernel-install remove %{version}-%{ath_release}.ath%{?dist}.%{_arch}
fi

%changelog
* Fri Aug 08 2025 Bhargavjit Bhuyan <example@example.com> - 6.10.0-1.ath.fc42
- Initial kernel package from the ath-next branch for Fedora.
