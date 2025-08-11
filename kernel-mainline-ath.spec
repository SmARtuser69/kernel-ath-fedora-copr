# Spec file for building a mainline Linux kernel with a custom configuration.
# This file is for a personal or test build and is not a full-featured Fedora kernel spec.
#
# Author: Bhargavjit Bhuyan
#
# Note: This spec file has been simplified to remove non-essential
# build dependencies for a basic test build.

%global mainline_version 6
%global mainline_subversion 16
%global patchlevel 0
%global kernel_version %{mainline_version}.%{mainline_subversion}.%{patchlevel}
%global release_version 1

# Use macros for better portability and consistency
%global _kernel_name kernel-mainline-ath
%global _kernel_release_name %{version}-%{release}

Name: %{_kernel_name}
Version: %{kernel_version}
Release: %{release_version}%{?dist}
Summary: The Linux kernel (patched)
License: GPLv2 and others
Source0: kernel-x86_64-fedora.config

# Minimized list of essential BuildRequires for a core kernel and modules.
BuildRequires: gcc
BuildRequires: make
BuildRequires: python3
BuildRequires: bc
BuildRequires: elfutils-libelf-devel
BuildRequires: ncurses-devel
BuildRequires: openssl-devel
BuildRequires: rpm-build
BuildRequires: bison
BuildRequires: flex
BuildRequires: python3-devel
BuildRequires: grubby
BuildRequires: kmod
BuildRequires: xz
BuildRequires: zlib-devel
BuildRequires: glibc-devel
BuildRequires: b4
BuildRequires: git
BuildRequires: dracut
BuildRequires: gpg
BuildRequires: gnupg2

ExclusiveArch: x86_64

# Use a macro and shell test to conditionally set a value, which is
# compatible with strict spec file parsers.
%global with_firmware %(test -d firmware && echo 1 || echo 0)

%description
The Linux kernel, the core of the Linux operating system. This package
contains a specific build of the mainline kernel from the 'ath' git tree.

# Kernel headers subpackage
%package headers
Summary: Header files for the Linux kernel
BuildArch: noarch
Provides: kernel-headers = %{version}-%{release}
%description headers
This package provides the kernel header files. These header files are used by
glibc to build user-space applications.

# Kernel devel subpackage
%package devel
Summary:  Development files for the Linux kernel
Requires: kernel-headers = %{version}-%{release}
Provides: kernel-devel = %{version}-%{release}
%description devel
This package provides the development files needed to build external kernel
modules.

# Conditionally define the firmware package
%if 0%{?with_firmware}
# Firmware subpackage
%package firmware
Summary: Firmware files for the Linux kernel
BuildArch: noarch
%description firmware
This package contains the firmware binary blobs required by the Linux kernel.
%endif

# The following subpackages and their related sections have been removed:
# - debuginfo (requires dwarves, etc.)
# - doc (requires asciidoc, etc.)
# - tools and tools-devel (requires rsync, pciutils-devel, etc.)

%prep
git clone https://github.com/torvalds/linux.git
cd linux
git checkout -b aspm-patch 19272b37aa4f83ca52bdf9c16d5d81bdd1354494
b4 am 20250716-ath-aspm-fix-v1-0-dd3e62c1b692@oss.qualcomm.com && mv *.mbx aspm-patch.mbx
git apply aspm-patch.mbx
cp %{SOURCE0} ./.config

%build
# Use the configuration from the currently running kernel as a base.
# This ensures a more complete set of drivers and features are included.
# : This assumes a config file exists for the host kernel.
NPROCS=$(/usr/bin/getconf _NPROCESSORS_ONLN)
make olddefconfig

# Now build the kernel and modules with the complete configuration.
make -j${NPROCS} bzImage
make -j${NPROCS} modules

%install
# Install kernel modules
make INSTALL_MOD_PATH=%{buildroot} modules_install

# Explicitly create boot directory
mkdir -p %{buildroot}/boot

# Copy built kernel files
cp -v arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{_kernel_release_name}
cp -v System.map %{buildroot}/boot/System.map-%{_kernel_release_name}
cp -v .config %{buildroot}/boot/config-%{_kernel_release_name}

# Create the initial ramdisk (initramfs) using dracut
# This is a critical step for modern systems to boot correctly
dracut --force %{buildroot}/boot/initramfs-%{_kernel_release_name}.img %{_kernel_release_name}

# Install user-space kernel headers
# This goes to /usr/include, as expected by glibc and user-space programs
make headers_install INSTALL_HDR_PATH=%{buildroot}/usr

# Install files for kernel-devel package
# This goes to /usr/src/kernels, as expected by external kernel module builders
mkdir -p %{buildroot}/usr/src/kernels/%{_kernel_release_name}
# Create a copy of the build tree's headers for the devel package
cp -a include %{buildroot}/usr/src/kernels/%{_kernel_release_name}/
cp -a Module.symvers %{buildroot}/usr/src/kernels/%{_kernel_release_name}/
cp -a scripts %{buildroot}/usr/src/kernels/%{_kernel_release_name}/
cp -a .config %{buildroot}/usr/src/kernels/%{_kernel_release_name}/
cp -a Makefile %{buildroot}/usr/src/kernels/%{_kernel_release_name}/

# Install firmware only if the 'firmware' directory exists
# This handles the 'No such file or directory' error and is consistent
# with the conditional packaging.
if [ -d firmware ]; then
 mkdir -p %{buildroot}/lib/firmware
 find firmware -type f -exec install -Dm644 '{}' '%{buildroot}/lib/firmware/{}' ';'
fi

%post
# Use grubby to add the new kernel to the bootloader
grubby --add-kernel=/boot/vmlinuz-%{_kernel_release_name} \
 --title="Linux Kernel %{_kernel_release_name}" \
 --copy-default \
 --make-default

%postun
# This handles both upgrade and erase
grubby --remove-kernel=/boot/vmlinuz-%{_kernel_release_name}

%files
%defattr(-,root,root,-)
/boot/vmlinuz-%{_kernel_release_name}
/boot/System.map-%{_kernel_release_name}
/boot/config-%{_kernel_release_name}
/boot/initramfs-%{_kernel_release_name}.img
/lib/modules/%{_kernel_release_name}/

%files headers
%defattr(-,root,root,-)
/usr/include/

%files devel
%defattr(-,root,root,-)
/usr/src/kernels/%{_kernel_release_name}/include/
/usr/src/kernels/%{_kernel_release_name}/scripts/
/usr/src/kernels/%{_kernel_release_name}/Module.symvers
/usr/src/kernels/%{_kernel_release_name}/.config
/usr/src/kernels/%{_kernel_release_name}/Makefile

%if 0%{?with_firmware}
%files firmware
%defattr(-,root,root,-)
/lib/firmware/
%endif

%changelog
* Mon Aug 11 2025 Bhargavjit Bhuyan <example@example.com> - 6.16.0-1
- Changed build configuration from 'defconfig' to a custom config based on the host kernel for a more complete build.
* Mon Aug 11 2025 Bhargavjit Bhuyan <example@example.com> - 6.16.0-1
- Fixed a critical issue by adding the dracut utility to generate the initramfs.
- Added dracut to BuildRequires and the initramfs file to the main package files.
* Sun Aug 10 2025 Bhargavjit Bhuyan <example@example.com> - 6.16.0-1
- Trimmed non-essential build dependencies for a more focused build.
- Removed subpackages for debuginfo, documentation, and tools.
* Sun Aug 10 2025 FlyingSaturn <example@example.com> - 6.16-rc1
- Made some changes
