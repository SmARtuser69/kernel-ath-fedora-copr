#
# spec file for a custom Linux kernel package for Fedora with ath patches
#
# Name:        kernel-ath
# Summary:     The Linux kernel (ath driver patches)
#

# Define the base version and release
%global ath_release 1

# Get the base kernel version from the source Makefile.
%global kernver_base %(make -s -C %{_sourcedir}/ath-next kernelversion)

# Construct the full, final version string once for consistency.
%global kernel_full_version %{kernver_base}-%{ath_release}.ath%{?dist}.%{_arch}

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
# Use make defconfig for a clean build.
make defconfig
# Fix: Pass the LOCALVERSION string correctly. The kernel build system will add a hyphen.
# This ensures the final version string matches the desired `6.10.0-1.ath.fc42.x86_64` format.
make %{?_smp_mflags} LOCALVERSION="-%{ath_release}.ath%{?dist}.%{_arch}"

%install
# The modules will be installed to a directory matching the LOCALVERSION.
make INSTALL_MOD_PATH=%{buildroot} modules_install

# Create boot directory
install -d %{buildroot}/boot

# Copy files using the single, consistent full version string.
install -m 644 arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{kernel_full_version}
install -m 644 System.map %{buildroot}/boot/System.map-%{kernel_full_version}
install -m 644 .config %{buildroot}/boot/config-%{kernel_full_version}

%files
/boot/vmlinuz-%{kernel_full_version}
/boot/System.map-%{kernel_full_version}
/boot/config-%{kernel_full_version}
/lib/modules/%{kernel_full_version}/

%post
echo "Running kernel-install script for %{kernel_full_version}..."
/usr/bin/kernel-install add %{kernel_full_version} /boot/vmlinuz-%{kernel_full_version}

%postun
if [ $1 -eq 0 ] ; then
    echo "Running kernel-install remove for %{kernel_full_version}..."
    /usr/bin/kernel-install remove %{kernel_full_version}
fi

%changelog
* Fri Aug 08 2025 Bhargavjit Bhuyan <example@example.com> - %{version}-%{release}
- Initial kernel package from the ath-next branch for Fedora.
