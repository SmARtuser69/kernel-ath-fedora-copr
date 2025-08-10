# Spec file for building a mainline Linux kernel with a custom configuration.
# This file is for a personal or test build and is not a full-featured Fedora kernel spec.
#
# Author: Bhargavjit Bhuyan
#
# Note: This spec file is corrected to adhere to packaging best practices
# while retaining the user's specified kernel version and source.

%global mainline_version 6
%global mainline_subversion 16
%global patchlevel 0
%global kernel_version %{mainline_version}.%{mainline_subversion}.%{patchlevel}
%global release_version 1

# Use macros for better portability and consistency
%global _kernel_name kernel-mainline-ath
%global _kernel_release_name %{version}-%{release}

Name:           %{_kernel_name}
Version:        %{kernel_version}
Release:        %{release_version}%{?dist}
Summary:        The Linux kernel (mainline from ath git tree)
License:        GPLv2
URL:            https://www.kernel.org/
Source0:        https://git.kernel.org/pub/scm/linux/kernel/git/ath/ath.git/snapshot/ath-main.tar.gz
Conflicts:      %{name} < %{version}-%{release}

# BuildRequires list is mostly correct, but has been slightly reordered for clarity
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl
BuildRequires:  python3
BuildRequires:  bc
BuildRequires:  elfutils-libelf-devel
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  rpm-build
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  rsync
BuildRequires:  python3-devel
BuildRequires:  grubby
BuildRequires:  kmod
BuildRequires:  xz
BuildRequires:  zlib-devel
BuildRequires:  libcap-devel
BuildRequires:  glibc-devel
BuildRequires:  python3-pyelftools
BuildRequires:  elfutils-devel
BuildRequires:  newt-devel
BuildRequires:  dwarves
BuildRequires:  libaio-devel
BuildRequires:  numactl-devel
BuildRequires:  audit-libs-devel

ExclusiveArch:  x86_64

%description
The Linux kernel, the core of the Linux operating system. This package
contains a specific build of the mainline kernel from the 'ath' git tree.

# Kernel headers subpackage
%package headers
Summary:        Header files for the Linux kernel
BuildArch:      noarch
Provides:       kernel-headers = %{version}-%{release}
%description headers
This package provides the kernel header files. These header files are used by
glibc to build user-space applications.

# Kernel devel subpackage
%package devel
Summary:        Development files for the Linux kernel
Requires:       kernel-headers = %{version}-%{release}
Provides:       kernel-devel = %{version}-%{release}
%description devel
This package provides the development files needed to build external kernel
modules.

# Kernel debuginfo subpackage
%package debuginfo
Summary:        Debug symbols for the Linux kernel
Requires:       %{_kernel_name} = %{version}-%{release}
%description debuginfo
This package provides debug symbols for the Linux kernel and its modules.

# Firmware subpackage
%package firmware
Summary:        Firmware files for the Linux kernel
BuildArch:      noarch
%description firmware
This package contains the firmware binary blobs required by the Linux kernel.

# Documentation subpackage
%package doc
Summary:        Documentation for the Linux kernel
BuildArch:      noarch
%description doc
This package contains the documentation for the Linux kernel.

# Tools subpackage
%package tools
Summary:        Tools for the Linux kernel
%description tools
This package contains user-space tools for interacting with the Linux kernel,
such as perf, cpupower, and turbostat.

# Tools devel subpackage
%package tools-devel
Summary:        Development files for the Linux kernel tools
Requires:       %{_kernel_name}-tools = %{version}-%{release}, kernel-devel = %{version}-%{release}
%description tools-devel
This package provides the development files (headers, libraries) needed to
build applications that use the kernel tools.

%prep
%setup -q -n ath-main

%build
# Use the default configuration and build the entire kernel and its modules
# Note: This uses a generic 'defconfig' which may not be optimized.
NPROCS=$(/usr/bin/getconf _NPROCESSORS_ONLN)
make defconfig
make -j${NPROCS}

%install
rm -rf %{buildroot}
# Install kernel modules
make INSTALL_MOD_PATH=%{buildroot} modules_install

# Explicitly create boot directory
mkdir -p %{buildroot}/boot

# Copy built kernel files
cp -v arch/x86/boot/bzImage %{buildroot}/boot/vmlinuz-%{_kernel_release_name}
cp -v System.map %{buildroot}/boot/System.map-%{_kernel_release_name}
cp -v .config %{buildroot}/boot/config-%{_kernel_release_name}

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

# Install firmware
mkdir -p %{buildroot}/lib/firmware
find firmware -type f -exec install -Dm644 {} %{buildroot}/lib/firmware/{} \;

# Install documentation
mkdir -p %{buildroot}/usr/share/doc/%{_kernel_name}-%{version}
cp -a Documentation/* %{buildroot}/usr/share/doc/%{_kernel_name}-%{version}/

# Install kernel tools and devel
make -C tools DESTDIR=%{buildroot} install

# Generate debug symbols and strip binaries
mkdir -p %{buildroot}/usr/lib/debug
# vmlinux is stripped and the debug symbols are saved
cp vmlinux %{buildroot}/usr/lib/debug/vmlinux-%{_kernel_release_name}.debug
strip --strip-debug vmlinux
objcopy --add-gnu-debuglink=%{buildroot}/usr/lib/debug/vmlinux-%{_kernel_release_name}.debug vmlinux
# Create the symlink to vmlinux in the devel directory
ln -s ../../lib/modules/%{_kernel_release_name}/vmlinux %{buildroot}/usr/src/kernels/%{_kernel_release_name}/vmlinux

# Process kernel modules for debug symbols
mkdir -p %{buildroot}/usr/lib/debug/lib/modules/%{_kernel_release_name}
find %{buildroot}/lib/modules/%{_kernel_release_name} -name "*.ko" | while read ko; do
    objcopy --only-keep-debug "$ko" "%{buildroot}/usr/lib/debug/${ko#%{buildroot}/}"
    strip --strip-debug --strip-unneeded "$ko"
done

%post
grubby --add-kernel=/boot/vmlinuz-%{_kernel_release_name} \
       --title="Linux Kernel %{_kernel_release_name}" \
       --copy-default \
       --make-default

%preun
# Removed redundant grubby command. The one in %postun is sufficient.
# No action needed here.

%postun
# This handles both upgrade and erase
grubby --remove-kernel=/boot/vmlinuz-%{_kernel_release_name}

%files
%defattr(-,root,root,-)
/boot/vmlinuz-%{_kernel_release_name}
/boot/System.map-%{_kernel_release_name}
/boot/config-%{_kernel_release_name}
/lib/modules/%{_kernel_release_name}/

%files headers
%defattr(-,root,root,-)
/usr/include/

%files devel
%defattr(-,root,root,-)
/usr/src/kernels/%{_kernel_release_name}/
%exclude /usr/src/kernels/%{_kernel_release_name}/include/
%exclude /usr/src/kernels/%{_kernel_release_name}/scripts/

%files debuginfo
%defattr(-,root,root,-)
/usr/lib/debug/vmlinux-%{_kernel_release_name}.debug
/usr/lib/debug/lib/modules/%{_kernel_release_name}/

%files firmware
%defattr(-,root,root,-)
/lib/firmware/

%files doc
%defattr(-,root,root,-)
/usr/share/doc/%{_kernel_name}-%{version}/

%files tools
%defattr(-,root,root,-)
/usr/bin/perf
/usr/bin/cpupower
/usr/bin/turbostat

%files tools-devel
%defattr(-,root,root,-)
/usr/include/perf/

%changelog
* Sat Aug 09 2025 Bhargavjit Bhuyan <example@example.com> - 6.16.0-1
- Initial build of mainline kernel 6.16.0 for Fedora COPR.
* Mon Aug 11 2025 Bhargavjit Bhuyan <example@example.com> - 6.16.0-1
- Replaced pahole with dwarves as a build dependency.
