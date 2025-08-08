#
# spec file for a custom Linux kernel package for Fedora with ath patches
#
# Name:        kernel-ath
# Summary:     The Linux kernel (ath driver patches)
#

# Use a dynamic approach to versioning
%global ath_release 1

# Define the base kernel version by getting it from the source
# The %(...) construct executes a command and uses its output as a value
%global kernver_base %(make -s -C %{_sourcedir}/ath-next kernelversion)
%global full_release_string %{kernver_base}-%{ath_release}.ath%{?dist}.%{_arch}

Name:          kernel-ath
Version:       %{kernver_base}
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
make %{?_smp_mflags} LOCALVERSION="-.ath%{ath_release}"

%install
# Install modules and pass the full version string to get the correct directory name
make INSTALL_MOD_PATH=%{buildroot} modules_install

# Create boot directory
install -d %{buildroot}/boot

# Copy files using a consistent path
install -m 644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{full_release_string}
install -m 644 System.map %{buildroot}/boot/System.map-%{full_release_string}
install -m 644 .config %{buildroot}/boot/config-%{full_release_string}

%files
/boot/vmlinuz-%{full_release_string}
/boot/System.map-%{full_release_string}
/boot/config-%{full_release_string}
/lib/modules/%{kernver_base}-.ath%{ath_release}.%{_arch}

%post
echo "Running kernel-install script for %{full_release_string}..."
/usr/bin/kernel-install add %{full_release_string} /boot/vmlinuz-%{full_release_string}

%postun
if [ $1 -eq 0 ] ; then
    echo "Running kernel-install remove for %{full_release_string}..."
    /usr/bin/kernel-install remove %{full_release_string}
fi

%changelog
* Fri Aug 08 2025 Bhargavjit Bhuyan <example@example.com> - 6.10.0-1.ath.fc42
- Initial kernel package from the ath-next branch for Fedora.
